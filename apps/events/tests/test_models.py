
import pytest
from django.utils import timezone

from apps.events.models import Event, LoadBatch
from utils.enums import EventType, Status


@pytest.mark.django_db
def test_create_event_model():
    """Tests if an Event object can be created in the database with the new fields."""
    batch = LoadBatch.objects.create(status=Status.SUCCESS.name)
    event = Event.objects.create(
        event_id='evt_test_123',
        name="Test Event via TDD",
        start_date=timezone.now(),
        end_date=timezone.now(),
        event_type=EventType.PRESENTIAL.name,
        venue_name="Test Venue",
        city="Test City",
        category="Technology",
        sub_category="Python",
        load_batch=batch
    )
    assert Event.objects.count() == 1
    assert event.name == "Test Event via TDD"
    assert event.event_id == 'evt_test_123'
    assert str(event) == 'Test Event via TDD (evt_test_123)'
