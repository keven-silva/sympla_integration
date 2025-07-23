from unittest.mock import patch

import pytest
from django.core.management import call_command

from apps.events.models import Event, LoadBatch
from utils.enums import EventType, Status


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
            'id': 'evt001',
            'name': 'Evento Presencial',
            'start_date': '2025-10-20T20:00:00',
            'end_date': '2025-10-20T22:00:00',
            'address': {'name': 'Local A', 'city': 'Recife'},
            'category_prim': {'name': 'Música'},
            'category_sec': {'name': 'Rock'},
        },
        {
            'id': 'evt002',
            'name': 'Evento Online',
            'start_date': '2025-11-15T09:00:00',
            'end_date': '2025-11-15T11:00:00',
            'address': {'addre_num': 0},
            'category_prim': {'name': 'Tecnologia'},
            'category_sec': {'name': 'Lives'},
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
    assert batch.status == Status.SUCCESS.name
    assert batch.events_imported_count == EVENTS_COUNT

    presential_event = Event.objects.get(event_id='evt001')
    assert presential_event.name == 'Evento Presencial'
    assert presential_event.city == 'Recife'
    assert presential_event.event_type == EventType.PRESENTIAL.name
    assert presential_event.sub_category == 'Rock'

    online_event = Event.objects.get(event_id='evt002')
    assert online_event.name == 'Evento Online'
    assert online_event.city is None
    assert online_event.venue_name is None
    assert online_event.event_type == EventType.ONLINE.name


@patch('apps.events.management.commands.import_sympla_events.SymplaService')
@pytest.mark.django_db
def test_import_command_skips_invalid_data(MockSymplaService):
    """
    Tests that the command skips events that fail Pydantic validation.
    """
    mock_api_data = [
        {
            'id': 'evt001',
            'name': 'Evento Válido',
            'start_date': '2025-10-20T20:00:00',
            'end_date': '2025-10-20T22:00:00',
            'address': {'address_num': 0},
            'category_prim': {'name': 'Música'},
            'category_sec': {'name': 'Pop'},
        },
        {
            'id': 'evt002',  # 'name' is missing
            'start_date': '2025-11-15T09:00:00',
            'end_date': '2025-11-15T11:00:00',
            'address': {'address_num': 0},
            'category_prim': {'name': 'Tecnologia'},
            'category_sec': {'name': 'Hackathon'},
        },
    ]
    mock_service_instance = MockSymplaService.return_value
    mock_service_instance.fetch_events.return_value = mock_api_data

    call_command('import_sympla_events')

    EVENTS_COUNT = 1
    LOAD_BATCH_COUNT = 1

    assert Event.objects.count() == EVENTS_COUNT
    assert Event.objects.filter(event_id='evt001').exists()
    assert not Event.objects.filter(event_id='evt002').exists()

    batch = LoadBatch.objects.first()
    assert batch.status == Status.SUCCESS.name
    assert batch.events_imported_count == LOAD_BATCH_COUNT
