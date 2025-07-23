import logging
from typing import Any, Dict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from pydantic import ValidationError

from apps.events.models import Event, LoadBatch
from apps.events.schemas import SymplaEventSchema
from apps.events.services import SymplaService
from utils.enums import Status

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to fetch events from Sympla API and save them to database."""

    help = 'Fetches events from the Sympla API and saves them to the database.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch: LoadBatch | None = None
        self.events_processed_count = 0

    def handle(self, *args: Any, **options: Any) -> None:
        """Main command execution handler."""
        self._start_import_process()

    def _start_import_process(self) -> None:
        """Initialize and control the import process flow."""
        self.stdout.write('Starting Sympla events import...')

        try:
            self.batch = LoadBatch.objects.create(status=Status.PENDING.name)
            logger.info(f'New load batch created: {self.batch.id}')

            self._process_events()
            self._mark_batch_success()

        except Exception as e:
            self._handle_import_error(e)
        finally:
            self._finalize_batch()

    def _process_events(self) -> None:
        """Fetch and process events from Sympla API."""
        service = SymplaService()
        api_events = service.fetch_events()

        with transaction.atomic():
            for event_data in api_events:
                self._process_single_event(event_data)

    def _process_single_event(self, event_data: Dict[str, Any]) -> None:
        """Process and validate a single event."""
        try:
            validated_event = SymplaEventSchema.model_validate(event_data)
            self._update_or_create_event(validated_event)

        except ValidationError as e:
            self._log_validation_error(event_data, e)

    def _update_or_create_event(
        self, validated_event: SymplaEventSchema
    ) -> None:
        """Update or create an event in the database."""
        event_obj, created = Event.objects.update_or_create(
            event_id=validated_event.id,
            defaults=self._build_event_defaults(validated_event),
        )

        self.events_processed_count += 1
        self._log_event_operation(event_obj, created)

    def _build_event_defaults(
        self, event: SymplaEventSchema
    ) -> Dict[str, Any]:
        """Build dictionary of event attributes for update_or_create."""
        return {
            'name': event.name,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'event_type': event.event_type,
            'venue_name': event.address.name,
            'city': event.address.city,
            'category': event.category_prim,
            'sub_category': event.category_sec,
            'load_batch': self.batch,
        }

    def _log_event_operation(self, event: Event, created: bool) -> None:  # noqa: PLR6301
        """Log event creation or update."""
        action = 'created' if created else 'updated'
        logger.info(f'Event {action}: {event.name}')

    def _log_validation_error(  # noqa: PLR6301
        self, event_data: Dict[str, Any], error: ValidationError
    ) -> None:
        """Log validation errors for problematic events."""
        event_id = event_data.get('id', 'N/A')
        logger.warning(
            'Skipping event due to validation error. '
            f'ID: {event_id}. Details: {error.json()}'
        )

    def _mark_batch_success(self) -> None:
        """Mark the current batch as successful."""
        if self.batch:
            self.batch.status = Status.SUCCESS.name
            self.stdout.write(
                self.style.SUCCESS('Import finished successfully!')
            )

    def _handle_import_error(self, error: Exception) -> None:
        """Handle errors during the import process."""
        if self.batch:
            self.batch.status = Status.ERROR.name
            logger.error(
                f'An error occurred during import for batch {self.batch.id}:'
                f'{error}',
                exc_info=True,
            )
            self.stdout.write(
                self.style.ERROR('Import failed. Check logs for details.')
            )

    def _finalize_batch(self) -> None:
        """Finalize the batch by setting completion timestamp and count."""
        if self.batch:
            self.batch.finished_at = timezone.now()
            self.batch.events_imported_count = self.events_processed_count
            self.batch.save()

            self.stdout.write(
                f'Batch {self.batch.id} finished with status '
                f"'{self.batch.status}'. "
                f'{self.events_processed_count} events processed.'
            )
