import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from utils.enums import EventType
from apps.events.models import Event, LoadBatch


@pytest.mark.django_db
def test_list_events_api_view():
    """
    Test the ListEventsAPIView view.
    """
    client = APIClient()

    batch = LoadBatch.objects.create(status='SUCCESS')
    Event.objects.create(
        event_id='evt_test_123',
        name="Test Event",
        start_date=timezone.now(),
        end_date=timezone.now(),
        event_type=EventType.PRESENTIAL.name,
        venue_name="Test Venue",
        city="Test City",
        category="Technology",
        sub_category="Python",
        load_batch=batch
    )
    Event.objects.create(
       event_id='evt_test_1234',
        name='Test Event B',
        start_date=timezone.now(),
        end_date=timezone.now(),
        event_type=EventType.ONLINE.name,
        category="Marketing",
        sub_category="workshop",
        load_batch=batch,
    )

    url = '/api/events/'
    response = client.get(url)
    EVENT_COUNT = 2

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) == EVENT_COUNT

    assert response.data[0]['name'] == 'Test Event B'
    assert response.data[0]['event_type'] == EventType.ONLINE.name,