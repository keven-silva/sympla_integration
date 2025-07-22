from django.db import models

from utils.enums import LogLevel, Status


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

    sympla_id = models.PositiveIntegerField(
        unique=True, verbose_name='ID Sympla'
    )
    name = models.CharField(max_length=255, verbose_name='Event Name')
    start_date = models.DateTimeField(verbose_name='Start Date')
    venue_name = models.CharField(max_length=255, verbose_name='Venue Name')
    city = models.CharField(max_length=100, verbose_name='City')
    category = models.CharField(max_length=100, verbose_name='Category')
    load_batch = models.ForeignKey(
        LoadBatch, on_delete=models.CASCADE, related_name='events'
    )

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} ({self.sympla_id})'


class Log(models.Model):
    """
    Stores log entries for various operations.
    """

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp',
    )
    level = models.CharField(
        max_length=20, choices=LogLevel.choices(), verbose_name='Level'
    )
    message = models.TextField(verbose_name='Message')
    load_batch = models.ForeignKey(
        LoadBatch,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True,
        verbose_name='Load Batch',
    )

    def __str__(self):
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M')
        return f'Log: {self.id} - {self.level} - {timestamp_str}'

    class Meta:
        verbose_name = 'Log Entry'
        verbose_name_plural = 'Log Entries'
        ordering = ['-timestamp']
