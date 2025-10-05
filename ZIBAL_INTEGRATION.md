# 💳 Zibal Payment Integration - Apatye Backend

## Overview

This document describes the Zibal payment gateway integration for Apatye's Business Plan subscriptions and future payment scenarios.

## 🏗️ Architecture

### Payment Flow

```
1. Client → POST /api/billing/subscriptions/start
   ↓
2. Server creates PaymentTransaction & Subscription
   ↓
3. Server → Zibal API (request payment)
   ↓
4. Server ← Zibal (trackId)
   ↓
5. Client ← Redirect URL (/start/{trackId})
   ↓
6. User completes payment on Zibal gateway
   ↓
7. Zibal → GET /api/payments/zibal/callback?trackId=...
   ↓
8. Server → Zibal API (verify payment)
   ↓
9. Server ← Zibal (payment confirmation)
   ↓
10. Server activates subscription
   ↓
11. Client ← Redirect to success/failure page
```

## 📦 Components

### 1. Models (`apps/billing/models.py`)

#### PaymentTransaction
Tracks all payment attempts and results.

**Fields:**
- `order_id`: Unique identifier for idempotency
- `track_id`: Zibal's tracking ID
- `amount_irr`: Amount in Iranian Rials
- `status`: INITIATED → PENDING → PAID/FAILED
- `purpose`: SUBSCRIPTION | APPOINTMENT_DEPOSIT | DELIVERY_FEE
- `result_code`: Zibal result code
- `ref_number`: Bank reference number
- `card_pan_masked`: Masked card number

#### Subscription
Manages Business Plan subscriptions.

**Fields:**
- `plan_type`: BUSINESS (expandable)
- `status`: PENDING → ACTIVE/EXPIRED/CANCELLED
- `duration_months`: Subscription duration
- `expires_at`: Expiry date
- `payment_transaction`: Link to payment

### 2. Zibal Client (`apps/billing/payments/zibal_client.py`)

Service layer for Zibal API communication.

**Methods:**
- `request_payment()`: Initialize payment
- `verify_payment()`: Verify after callback (CRITICAL)
- `inquiry()`: Check payment status (for reconciliation)
- `create_start_url()`: Generate redirect URL

**Configuration:**
```python
ZIBAL_MERCHANT_ID=zibal  # 'zibal' for sandbox
ZIBAL_GATEWAY_BASE=https://gateway.zibal.ir
ZIBAL_API_BASE=https://gateway.zibal.ir
ZIBAL_TIMEOUT=10
ZIBAL_SANDBOX=True
```

### 3. API Endpoints

#### Start Payment
```http
POST /api/billing/subscriptions/start/
Content-Type: application/json
Authorization: Bearer <token>

{
  "plan_type": "business",
  "months": 3,
  "vendor_id": 1  // optional
}
```

**Response (201):**
```json
{
  "order_id": "AP-20251005142530-123-abc456",
  "track_id": 123456789,
  "redirect_url": "https://gateway.zibal.ir/start/123456789",
  "amount": 1425000,
  "amount_display": "1,425,000 ریال",
  "subscription_id": 42
}
```

#### Payment Callback
```http
GET /api/payments/zibal/callback/?trackId=123456789
```

**Response (200):**
```json
{
  "order_id": "AP-20251005142530-123-abc456",
  "status": "paid",
  "result_code": 100,
  "message": "پرداخت با موفقیت انجام شد",
  "paid_at": "2025-10-05T14:30:45Z",
  "subscription_id": 42,
  "redirect": "http://localhost:3000/payment/success?order_id=..."
}
```

#### Get My Subscriptions
```http
GET /api/billing/subscriptions/me/
Authorization: Bearer <token>
```

#### Get Transaction by Order ID
```http
GET /api/billing/transactions/by-order/AP-20251005142530-123-abc456/
Authorization: Bearer <token>
```

## 🔐 Security & Best Practices

### 1. Idempotency
- **Unique `order_id`** prevents duplicate payments
- Format: `AP-{timestamp}-{user_id}-{random}`
- Database constraint ensures uniqueness

### 2. Only-Verify Trust
**CRITICAL:** Never trust callback parameters!
- Callback params can be manipulated
- Always call `verify_payment()` server-to-server
- Only trust verify response

### 3. Optimistic Locking
```python
transaction = PaymentTransaction.objects.select_for_update().get(...)
```

### 4. Status Transitions
```
INITIATED → PENDING → PAID
                    ↘ FAILED
                    ↘ EXPIRED
```

### 5. Logging
All Zibal requests/responses logged with:
- `order_id` / `track_id` for correlation
- No sensitive data (card numbers, etc.)
- Request/response times for monitoring

## 💰 Pricing Logic

```python
def calculate_subscription_amount(months):
    base = 500_000  # Rials per month
    
    if months >= 12:
        discount = 0.15  # 15% off
    elif months >= 6:
        discount = 0.10  # 10% off
    elif months >= 3:
        discount = 0.05  # 5% off
    else:
        discount = 0
    
    return int(base * months * (1 - discount))
```

## 🧪 Testing

### Run Tests
```bash
# All billing tests
pytest apps/billing/tests/

# Specific test file
pytest apps/billing/tests/test_api.py -v

# With coverage
pytest apps/billing/tests/ --cov=apps.billing --cov-report=html
```

### Mock Fixtures

**Successful Payment:**
```python
def test_payment_success(zibal_mock, user, api_client):
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/billing/subscriptions/start/', {...})
    assert response.status_code == 201
```

**Failed Payment:**
```python
def test_payment_failed(zibal_mock_failed, user, api_client):
    # ... test failed payment scenario
```

**Duplicate Callback:**
```python
def test_callback_idempotency(zibal_mock_duplicate, ...):
    # ... test handling duplicate verify calls
```

## 🔄 Reconciliation

### Manual Reconciliation
```bash
# Reconcile last 24 hours
python manage.py zibal_reconcile --hours=24

# Reconcile last 7 days
python manage.py zibal_reconcile --since=7

# Specific transaction
python manage.py zibal_reconcile --track-id=123456789

# Dry run (no changes)
python manage.py zibal_reconcile --dry-run
```

### Automated Reconciliation (Celery)
```python
# In config/celery.py
app.conf.beat_schedule = {
    'reconcile-pending-payments': {
        'task': 'apps.billing.tasks.reconcile_pending_payments',
        'schedule': crontab(hour='*/4', minute=0),  # Every 4 hours
    },
}
```

## 📊 Zibal Result Codes

| Code | Meaning | Action |
|------|---------|--------|
| 100 | Success | Mark as PAID |
| 102 | Not found | Log error |
| 103 | Invalid merchant | Check config |
| 105 | Invalid amount | Validation error |
| 106 | Already verified | Check idempotency |
| 201 | Already verified (duplicate) | Idempotent success |
| 202 | Not paid / Failed | Mark as FAILED |

## 🚨 Error Handling

### Gateway Timeout
```python
try:
    result = zibal_client.request_payment(...)
except ZibalError as e:
    logger.error(f"Zibal error: {e}")
    return Response({'error': 'خطا در اتصال به درگاه'}, 502)
```

### Network Retry
Uses `tenacity` for automatic retry:
- 3 attempts
- Exponential backoff (1s, 2s, 4s)
- Only for transient errors

### Validation Errors
```python
try:
    validated = ZibalRequestResponse(**result)
except ValidationError as e:
    raise ZibalError(f"Invalid response: {e}")
```

## 📈 Monitoring & Metrics

### Key Metrics
- `payments_started`: Total payment initiations
- `payments_paid`: Successful payments
- `payments_failed`: Failed payments
- `verify_latency_ms`: Verify API latency
- `pending_count`: Pending transactions count

### Logging
```python
logger.info(
    f"Payment started: order_id={order_id}",
    extra={
        'user_id': user.id,
        'order_id': order_id,
        'track_id': track_id,
        'amount': amount
    }
)
```

## 🧪 Sandbox Testing

### Sandbox Configuration
```env
ZIBAL_MERCHANT_ID=zibal
ZIBAL_SANDBOX=True
```

### Test Cards
Zibal provides test cards for sandbox:
- Use merchant `zibal` for testing
- All payments are simulated
- No real money involved

### Test Flow
1. Start payment with `merchant=zibal`
2. Redirect to `gateway.zibal.ir/start/{trackId}`
3. Test payment page appears
4. Complete/cancel payment
5. Callback received
6. Verify payment

## 🔮 Future Enhancements

### 1. Additional Payment Purposes
```python
class PaymentPurpose:
    SUBSCRIPTION = 'subscription'  # ✅ Implemented
    APPOINTMENT_DEPOSIT = 'appointment_deposit'  # 🔜 Future
    DELIVERY_FEE = 'delivery_fee'  # 🔜 Future
```

### 2. Refund Support
```python
def refund_payment(track_id, amount):
    """Refund full or partial amount."""
    # Implement Zibal refund API
```

### 3. Direct Debit
For recurring subscriptions without user interaction.

### 4. Multi-Gateway Support
Add ZarinPal, Saman, etc. with unified interface.

## 📚 API Documentation

Full OpenAPI documentation available at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

Search for "billing" or "payment" to see all endpoints.

## 🆘 Troubleshooting

### Payment stuck in PENDING
```bash
python manage.py zibal_reconcile --track-id=<track_id>
```

### Callback not received
- Check `ZIBAL_CALLBACK_BASE` in settings
- Ensure callback URL is accessible
- Check Zibal dashboard for callback attempts

### Verify fails
- Check merchant ID
- Verify track_id is correct
- Check Zibal API status

### Database deadlock
- Ensure `select_for_update()` is used
- Keep transaction blocks small
- Add retry logic

## 📞 Support

- **Zibal Documentation**: https://docs.zibal.ir
- **Zibal Support**: support@zibal.ir
- **Project Issues**: [GitHub Issues]

---

**Last Updated**: 2025-10-05  
**Version**: 1.0.0  
**Author**: Apatye Backend Team
