import time

import pytest
from django.utils import timezone

from apps.events.models import Event, LoadBatch, Log
from utils.enums import LogLevel, Status


@pytest.mark.django_db
def test_create_event_model():
    """
    Test creating an Event model instance and verify its attributes.
    """
    batch = LoadBatch.objects.create(status=Status.SUCCESS.name)
    event = Event.objects.create(
        sympla_id=123,
        name='Evento de Teste',
        start_date=timezone.now(),
        venue_name='Local de Teste',
        city='Cidade Teste',
        category='Tecnologia',
        load_batch=batch,
    )
    assert Event.objects.count() == 1
    assert event.name == 'Evento de Teste'
    assert event.load_batch.status == Status.SUCCESS.name


@pytest.mark.django_db
def test_create_log_with_batch():
    """
    Test creating a Log model instance with a related LoadBatch instance.
    """
    batch = LoadBatch.objects.create(status=Status.PENDING.name)
    log = Log.objects.create(
        level=LogLevel.INFO.name,
        message='Starting batch processing.',
        load_batch=batch,
    )
    assert Log.objects.count() == 1
    assert log.level == LogLevel.INFO.name
    assert log.message == 'Starting batch processing.'
    assert log.load_batch == batch
    assert log.timestamp is not None


@pytest.mark.django_db
def test_create_log_without_batch():
    """
    Test creating a Log model instance without a related LoadBatch instance.
    """
    log = Log.objects.create(
        level=LogLevel.ERROR.name, message='A general error occurred.'
    )
    assert Log.objects.count() == 1
    assert log.level == LogLevel.ERROR.name
    assert log.load_batch is None
    assert log.timestamp is not None


@pytest.mark.django_db
def test_log_meta_options_and_str():
    """
    Test Log model's Meta options and __str__ method.
    """

    log1 = Log.objects.create(
        level=LogLevel.DEBUG.name,
        message='Debugging...',
    )
    time.sleep(0.01)
    log2 = Log.objects.create(level='WARNING', message='A warning.')

    assert str(log1).startswith('Log:')
    assert Log.objects.first() == log2
    assert Log._meta.ordering == ['-timestamp']
