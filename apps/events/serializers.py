from rest_framework import serializers

from apps.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'event_id',
            'name',
            'start_date',
            'end_date',
            'venue_name',
            'city',
            'category',
            'sub_category',
            'load_batch',
            'event_type'
        ]
