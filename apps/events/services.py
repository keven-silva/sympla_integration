import logging
from typing import Any, Dict, List

import requests
from decouple import config
from requests.exceptions import HTTPError, RequestException, Timeout

logger = logging.getLogger(__name__)


class SymplaService:
    """
    Service class to interact with the Sympla API.
    """

    def __init__(self):
        self.token = config('SYMPLA_API_TOKEN', default=None)
        self.base_url = config('SYMPLA_BASE_URL', default=None)

        if not self.token:
            raise ValueError(
                'Sympla API token (SYMPLA_API_TOKEN) is not configured.'
            )

        self.session = requests.Session()
        self.session.headers.update({'S_Token': self.token})

    def fetch_events(self) -> List[Dict[str, Any]]:
        """
        Fetches all events from Sympla, handling pagination.

        Returns:
            list[dict]: A list of dictionaries, where each one represents an
                        event.
                        Returns an empty list in case of communication error.
        """
        all_events = []
        next_page_url = self.base_url

        while next_page_url:
            logger.info(f'Fetching events from URL: {next_page_url}')
            try:
                response = self.session.get(next_page_url, timeout=15)

                response.raise_for_status()

                data = response.json()

                all_events.extend(data.get('data', []))

                pagination_info = data.get('pagination', {})
                if pagination_info.get('has_next'):
                    next_page_url = pagination_info.get('next_page_url')
                else:
                    next_page_url = None

            except Timeout:
                logger.error(
                    'Timeout on request to Sympla API: %s',
                    next_page_url,
                )
                break
            except HTTPError as http_err:
                logger.error(
                    'HTTP error accessing Sympla API: %s - Status: %s',
                    http_err,
                    http_err.response.status_code,
                )
                break
            except RequestException as e:
                logger.error('Communication error with Sympla API: %s', e)
                break

        logger.info(f'Total of {len(all_events)} events found in Sympla API.')
        return all_events
