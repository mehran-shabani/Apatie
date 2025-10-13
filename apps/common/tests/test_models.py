"""Tests for common app models."""
import pytest
from django.db import connection, models

from apps.common.models import SoftDeleteModel


@pytest.mark.django_db(transaction=True)
def test_soft_delete_and_restore_roundtrip():
    """SoftDeleteModel should toggle flags and persist timestamps."""

    class TemporaryModel(SoftDeleteModel):
        name = models.CharField(max_length=50)

        class Meta:
            app_label = 'tests'
            managed = True

    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF;')
    try:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TemporaryModel)

        instance = TemporaryModel.objects.create(name='sample')
        assert instance.is_deleted is False
        assert instance.deleted_at is None

        instance.soft_delete()
        instance.refresh_from_db()
        assert instance.is_deleted is True
        assert instance.deleted_at is not None

        instance.restore()
        instance.refresh_from_db()
        assert instance.is_deleted is False
        assert instance.deleted_at is None
    finally:
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TemporaryModel)
        cursor.execute('PRAGMA foreign_keys = ON;')
