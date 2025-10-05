"""
Management command for reconciling pending Zibal payments.

Usage:
    python manage.py zibal_reconcile --since=1
    python manage.py zibal_reconcile --hours=24
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.billing.models import PaymentTransaction
from apps.billing.payments.zibal_client import get_zibal_client, ZibalError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reconcile pending Zibal payment transactions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--since',
            type=int,
            default=1,
            help='Reconcile transactions from N days ago (default: 1)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            help='Reconcile transactions from N hours ago (overrides --since)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry run - do not update database',
        )
        parser.add_argument(
            '--track-id',
            type=int,
            help='Reconcile specific transaction by track_id',
        )
    
    def handle(self, *args, **options):
        since_days = options['since']
        hours = options.get('hours')
        dry_run = options['dry_run']
        specific_track_id = options.get('track_id')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        # Calculate time threshold
        if hours:
            time_threshold = timezone.now() - timedelta(hours=hours)
            self.stdout.write(f'Reconciling transactions from last {hours} hours')
        else:
            time_threshold = timezone.now() - timedelta(days=since_days)
            self.stdout.write(f'Reconciling transactions from last {since_days} days')
        
        # Get pending transactions
        if specific_track_id:
            transactions = PaymentTransaction.objects.filter(
                track_id=specific_track_id,
                gateway=PaymentTransaction.PaymentGateway.ZIBAL
            )
            self.stdout.write(f'Reconciling specific transaction: track_id={specific_track_id}')
        else:
            transactions = PaymentTransaction.objects.filter(
                gateway=PaymentTransaction.PaymentGateway.ZIBAL,
                status__in=[
                    PaymentTransaction.PaymentStatus.INITIATED,
                    PaymentTransaction.PaymentStatus.PENDING
                ],
                created_at__gte=time_threshold,
                track_id__isnull=False
            ).order_by('created_at')
        
        total = transactions.count()
        self.stdout.write(f'Found {total} pending transactions to reconcile')
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No transactions to reconcile'))
            return
        
        zibal_client = get_zibal_client()
        
        reconciled = 0
        failed = 0
        already_processed = 0
        
        for txn in transactions:
            self.stdout.write(f'\nProcessing: {txn.order_id} (track_id={txn.track_id})')
            
            try:
                # Inquiry payment status
                inquiry_result = zibal_client.inquiry(txn.track_id)
                
                result_code = inquiry_result.get('result')
                status_code = inquiry_result.get('status')
                
                self.stdout.write(
                    f'  Result: {result_code}, Status: {status_code}, '
                    f'Message: {inquiry_result.get("message", "N/A")}'
                )
                
                if not dry_run:
                    with transaction.atomic():
                        # Check current status
                        txn.refresh_from_db()
                        
                        if txn.status == PaymentTransaction.PaymentStatus.PAID:
                            self.stdout.write(
                                self.style.WARNING(f'  Already processed: {txn.order_id}')
                            )
                            already_processed += 1
                            continue
                        
                        # Status 1 = Paid
                        if status_code == 1:
                            # Verify the payment
                            verify_result = zibal_client.verify_payment(txn.track_id)
                            
                            if verify_result['success']:
                                txn.mark_as_paid(
                                    result_code=verify_result['result'],
                                    ref_number=verify_result['ref_number'],
                                    card_pan=verify_result['card_number']
                                )
                                
                                # Activate subscription if applicable
                                if txn.purpose == PaymentTransaction.PaymentPurpose.SUBSCRIPTION:
                                    from apps.billing.models import Subscription
                                    subscription_id = txn.meta.get('subscription_id')
                                    if subscription_id:
                                        try:
                                            subscription = Subscription.objects.get(id=subscription_id)
                                            subscription.payment_transaction = txn
                                            subscription.amount_paid = txn.amount_irr
                                            subscription.activate(
                                                duration_months=txn.meta.get('months', 1)
                                            )
                                            self.stdout.write(
                                                self.style.SUCCESS(
                                                    f'  ✓ Subscription {subscription.id} activated'
                                                )
                                            )
                                        except Subscription.DoesNotExist:
                                            self.stdout.write(
                                                self.style.WARNING(
                                                    f'  Subscription {subscription_id} not found'
                                                )
                                            )
                                
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Paid: {txn.order_id}'))
                                reconciled += 1
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'  Verify failed: {verify_result}')
                                )
                                failed += 1
                        
                        # Status -2 = Cancelled
                        elif status_code == -2:
                            txn.mark_as_failed(
                                result_code=result_code,
                                message='پرداخت لغو شد'
                            )
                            self.stdout.write(self.style.WARNING(f'  ✗ Cancelled: {txn.order_id}'))
                            reconciled += 1
                        
                        # Still pending
                        elif status_code == -1:
                            # Check if too old (more than 30 minutes)
                            age = timezone.now() - txn.created_at
                            if age > timedelta(minutes=30):
                                txn.status = PaymentTransaction.PaymentStatus.EXPIRED
                                txn.message = 'منقضی شده'
                                txn.save()
                                self.stdout.write(
                                    self.style.WARNING(f'  ⏱ Expired: {txn.order_id}')
                                )
                                reconciled += 1
                            else:
                                self.stdout.write(f'  ⏳ Still pending: {txn.order_id}')
                        
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  Unknown status: {status_code} for {txn.order_id}'
                                )
                            )
                else:
                    self.stdout.write(self.style.NOTICE('  (Dry run - no changes made)'))
                    reconciled += 1
                
            except ZibalError as e:
                self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
                failed += 1
                logger.error(f'Reconcile error for {txn.order_id}: {str(e)}', exc_info=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Unexpected error: {str(e)}'))
                failed += 1
                logger.error(
                    f'Unexpected reconcile error for {txn.order_id}: {str(e)}',
                    exc_info=True
                )
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'\nReconciliation Summary:'))
        self.stdout.write(f'  Total processed: {total}')
        self.stdout.write(f'  Reconciled: {reconciled}')
        self.stdout.write(f'  Already processed: {already_processed}')
        self.stdout.write(f'  Failed: {failed}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were saved'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Reconciliation complete'))
