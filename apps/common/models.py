"""Base models for Apatye project."""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """An abstract base class that tracks creation and update timestamps."""

    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """An abstract model that provides soft delete behaviour."""

    is_deleted = models.BooleanField(_('Is deleted'), default=False)
    deleted_at = models.DateTimeField(_('Deleted at'), null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the instance as deleted without removing it from the database."""

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        """Restore a previously soft-deleted instance."""

        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
