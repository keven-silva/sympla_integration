import logging

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
    help = 'Fetches events from the Sympla API and saves them to the database.'

    def handle(self, *args, **options):
        self.stdout.write('Starting Sympla events import...')

        batch = LoadBatch.objects.create(status=Status.PENDING.name)
        logger.info(f'New load batch created: {batch.id}')

        events_processed_count = 0

        try:
            service = SymplaService()
            api_events = service.fetch_events()

            with transaction.atomic():
                for event_data in api_events:
                    try:
                        validated_event = SymplaEventSchema.model_validate(
                            event_data
                        )

                        event_obj, created = Event.objects.update_or_create(
                            event_id=validated_event.id,
                            defaults={
                                'name': validated_event.name,
                                'start_date': validated_event.start_date,
                                'end_date': validated_event.end_date,
                                'event_type': validated_event.event_type,
                                'venue_name': validated_event.address.name,
                                'city': validated_event.address.city,
                                'category': validated_event.category_prim,
                                'sub_category': validated_event.category_sec,
                                'load_batch': batch,
                            },
                        )
                        events_processed_count += 1
                        if created:
                            logger.info(f'Event created: {event_obj.name}')
                        else:
                            logger.info(f'Event updated: {event_obj.name}')

                    except ValidationError as e:
                        event_id = event_data.get('id', 'N/A')
                        logger.warning(
                            f"Skipping event due to validation error. ID: {event_id}. "
                            f"Details: {e.json()}"
                        )
                        continue

            batch.status = Status.SUCCESS.name
            self.stdout.write(
                self.style.SUCCESS('Import finished successfully!')
            )

        except Exception as e:
            batch.status = 'ERROR'
            logger.error(
                f'An error occurred during import for batch {batch.id}: {e}',
                exc_info=True,
            )
            self.stdout.write(
                self.style.ERROR('Import failed. Check logs for details.')
            )

        finally:
            batch.finished_at = timezone.now()
            batch.events_imported_count = events_processed_count
            batch.save()
            self.stdout.write(
                f"Batch {batch.id} finished with status '{batch.status}'."
                f'{events_processed_count} events processed.'
            )
