import logging

from dateutil.parser import parse as parse_datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.events.models import Event, LoadBatch
from apps.events.services import SymplaService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetches events from the Sympla API and saves them to the database.'

    def handle(self, *args, **options):
        self.stdout.write('Starting Sympla events import...')

        batch = LoadBatch.objects.create(status='RUNNING')
        logger.info(f'New load batch created: {batch.id}')

        events_processed_count = 0

        try:
            service = SymplaService()
            api_events = service.fetch_events()

            with transaction.atomic():
                for event_data in api_events:
                    try:
                        start_date = parse_datetime(event_data['start_date'])

                        event_obj, created = Event.objects.update_or_create(
                            sympla_id=event_data['id'],
                            defaults={
                                'name': event_data['name'],
                                'start_date': start_date,
                                'venue_name': event_data['venue']['name'],
                                'city': event_data['venue']['city'],
                                'category': event_data['category']['name'],
                                'load_batch': batch,
                            },
                        )
                        events_processed_count += 1
                        if created:
                            logger.info(f'Event created: {event_obj.name}')
                        else:
                            logger.info(f'Event updated: {event_obj.name}')

                    except (KeyError, TypeError) as e:
                        logger.warning(
                            'Skipping event with invalid/missing data: '
                            f'{event_data.get("id")}. '
                            f'Error: {e}'
                        )
                        continue

            batch.status = 'SUCCESS'
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
