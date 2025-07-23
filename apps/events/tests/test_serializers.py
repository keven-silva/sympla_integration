import pytest
from django.utils import timezone

from apps.events.models import Event, LoadBatch
from apps.events.serializers import EventSerializer
from utils.enums import EventType, Status


@pytest.mark.django_db
def test_event_serializer_contains_expected_fields():
    """
        Tests that the EventSerializer serializes an Event object with the 
        correct new fields.
    """
    batch = LoadBatch.objects.create(status=Status.SUCCESS.name)

    event_obj = Event.objects.create(
        event_id='ser_test_456',
        name="Serialized Event",
        start_date=timezone.now(),
        end_date=timezone.now(),
        event_type=EventType.ONLINE.name,
        category="API",
        sub_category="REST",
        load_batch=batch
    )

    serializer = EventSerializer(instance=event_obj)
    data = serializer.data

    expected_keys = {
        'id', 'event_id', 'name', 'start_date', 'end_date', 'venue_name',
        'city', 'category', 'sub_category', 'load_batch', 'event_type'
    }

    assert set(data.keys()) == expected_keys
    assert data['name'] == "Serialized Event"
    assert data['event_type'] == EventType.ONLINE.name


@pytest.mark.django_db
def test_event_serializer_deserialization_and_create():
    """
    Test that the EventSerializer can validate data and create a new Event.
    """
    batch = LoadBatch.objects.create(status='PENDING')

    event_data = {
        'id': 1,
        'event_id':'evt001',
        'name': 'Novo Evento via Serializer',
        'start_date': timezone.now(),
        'end_date': timezone.now(),
        'event_type': EventType.PRESENTIAL.name,
        'venue_name': 'Local do Novo Evento',
        'city': 'Nova Cidade',
        'category': 'Música',
        'sub_category': 'Rock',
        'load_batch': batch.id
    }

    serializer = EventSerializer(data=event_data)
    assert serializer.is_valid(raise_exception=True)
    event_instance = serializer.save()

    assert Event.objects.count() == 1
    assert event_instance.name == 'Novo Evento via Serializer'
    assert event_instance.event_id == 'evt001'
    assert event_instance.load_batch == batch


@pytest.mark.django_db
def test_event_serializer_invalid_data():
    """
    Test that the EventSerializer fails validation with invalid data (e.g.,
    missing required fields).
    """
    invalid_data = {'sympla_id': 101, 'name': 'Evento Incompleto'}

    serializer = EventSerializer(data=invalid_data)
    assert not serializer.is_valid()

    assert 'start_date' in serializer.errors
    assert 'load_batch' in serializer.errors
