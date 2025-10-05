"""
Base models for Apatye project.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    An abstract base class model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(_('Is deleted'), default=False)
    deleted_at = models.DateTimeField(_('Deleted at'), null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the object."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
