# apps/events/tests/test_commands.py
from unittest.mock import patch

import pytest
from django.core.management import call_command

from apps.events.models import Event, LoadBatch


@patch('apps.events.management.commands.import_sympla_events.SymplaService')
@pytest.mark.django_db
def test_import_command_success(MockSymplaService):
    """
    Tests the import command in the success scenario.
    Verifies that the service is called and events are created/updated
    correctly.
    """
    mock_api_data = [
        {
            'id': 101,
            'name': 'Rock Concert',
            'start_date': '2025-10-20T20:00:00',
            'venue': {'name': 'Main Stadium', 'city': 'Recife'},
            'category': {'name': 'Music'},
        },
        {
            'id': 102,
            'name': 'Tech Fair',
            'start_date': '2025-11-15T09:00:00',
            'venue': {'name': 'Convention Center', 'city': 'São Paulo'},
            'category': {'name': 'Technology'},
        },
    ]

    mock_service_instance = MockSymplaService.return_value
    mock_service_instance.fetch_events.return_value = mock_api_data

    assert Event.objects.count() == 0
    assert LoadBatch.objects.count() == 0

    call_command('import_sympla_events')

    mock_service_instance.fetch_events.assert_called_once()

    EVENTS_COUNT = 2
    LOAD_BATCH_COUNT = 1

    assert Event.objects.count() == EVENTS_COUNT
    assert LoadBatch.objects.count() == LOAD_BATCH_COUNT

    batch = LoadBatch.objects.first()
    assert batch.status == 'SUCCESS'
    assert batch.events_imported_count == EVENTS_COUNT

    event = Event.objects.get(sympla_id=101)
    assert event.name == 'Rock Concert'
    assert event.city == 'Recife'
    assert event.load_batch == batch
