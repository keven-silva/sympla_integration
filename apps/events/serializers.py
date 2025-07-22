from rest_framework import serializers

from apps.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'sympla_id',
            'name',
            'start_date',
            'venue_name',
            'city',
            'category',
            'load_batch',
        ]
