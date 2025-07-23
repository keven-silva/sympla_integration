from django.db import models

from utils.enums import EventType, Status


class LoadBatch(models.Model):
    """
    Represents a batch of events loaded from an external source.
    """

    started_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Start Load Time'
    )
    finished_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Finish Load Time'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices(),
        verbose_name='Status',
    )
    events_imported_count = models.PositiveIntegerField(
        default=0, verbose_name='Events Imported Count'
    )

    def __str__(self):
        return f'LoadBatch: {self.id} - {self.get_status_display()}'

    class Meta:
        verbose_name = 'Load Batch'
        verbose_name_plural = 'Load Batches'


class Event(models.Model):
    """
    Represents an event loaded from an external source.
    """

    event_id = models.CharField(
        max_length=50, unique=True, verbose_name='Event ID'
    )
    name = models.CharField(max_length=255, verbose_name='Event Name')
    start_date = models.DateTimeField(verbose_name='Start Date')
    end_date = models.DateTimeField(
        blank=True, null=True, verbose_name='End Date'
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices(),
        blank=True,
        null=True,
        verbose_name='Event Type',
    )
    venue_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Venue Name'
    )
    city = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='City'
    )
    category = models.CharField(max_length=100, verbose_name='Category')
    sub_category = models.CharField(
        max_length=100, verbose_name='Sub Category'
    )
    load_batch = models.ForeignKey(
        LoadBatch, on_delete=models.CASCADE, related_name='events'
    )

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} ({self.event_id})'
