import pytest
from django.utils import timezone

from apps.events.models import Event, LoadBatch
from apps.events.serializers import EventSerializer


@pytest.mark.django_db
def test_event_serializer_serialization():
    """
    Test that the EventSerializer correctly serializes an Event instance.
    """
    batch = LoadBatch.objects.create(status='SUCCESS')
    SYMPLA_ID = 456

    event_obj = Event.objects.create(
        sympla_id=SYMPLA_ID,
        name='Evento Serializado',
        start_date=timezone.now(),
        venue_name='Local da API',
        city='Cidade da API',
        category='API',
        load_batch=batch,
    )

    serializer = EventSerializer(instance=event_obj)
    data = serializer.data

    expected_keys = [
        'id',
        'sympla_id',
        'name',
        'start_date',
        'venue_name',
        'city',
        'category',
        'load_batch',
    ]
    assert set(data.keys()) == set(expected_keys)

    # Verify that the serialized values match the original object
    assert data['id'] == event_obj.id
    assert data['sympla_id'] == SYMPLA_ID
    assert data['name'] == 'Evento Serializado'
    assert data['venue_name'] == 'Local da API'
    assert data['city'] == 'Cidade da API'
    assert data['category'] == 'API'
    assert data['load_batch'] == batch.id


@pytest.mark.django_db
def test_event_serializer_deserialization_and_create():
    """
    Test that the EventSerializer can validate data and create a new Event.
    """
    batch = LoadBatch.objects.create(status='PENDING')
    SYMPLA_ID = 789

    event_data = {
        'sympla_id': SYMPLA_ID,
        'name': 'Novo Evento via Serializer',
        'start_date': timezone.now(),
        'venue_name': 'Local do Novo Evento',
        'city': 'Nova Cidade',
        'category': 'Testes',
        'load_batch': batch.id,
    }

    serializer = EventSerializer(data=event_data)
    assert serializer.is_valid(raise_exception=True)
    event_instance = serializer.save()

    assert Event.objects.count() == 1
    assert event_instance.name == 'Novo Evento via Serializer'
    assert event_instance.sympla_id == SYMPLA_ID
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
