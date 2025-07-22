import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.events.models import Event, LoadBatch


@pytest.mark.django_db
def test_list_events_api_view():
    """
    Test the ListEventsAPIView view.
    """
    client = APIClient()

    batch = LoadBatch.objects.create(status='SUCCESS')
    Event.objects.create(
        sympla_id=1,
        name='Evento A',
        start_date=timezone.now(),
        venue_name='Local A',
        city='Cidade A',
        category='Cat A',
        load_batch=batch,
    )
    Event.objects.create(
        sympla_id=2,
        name='Evento B',
        start_date=timezone.now(),
        venue_name='Local B',
        city='Cidade B',
        category='Cat B',
        load_batch=batch,
    )

    url = '/api/events/'
    response = client.get(url)
    EVENT_COUNT = 2

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) == EVENT_COUNT

    assert response.data[0]['name'] == 'Evento B'
