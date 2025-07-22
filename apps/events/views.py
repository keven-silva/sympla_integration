from rest_framework import generics

from apps.events.models import Event
from apps.events.serializers import EventSerializer


class EventListAPIView(generics.ListAPIView):
    """
    API view to list all events.
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
