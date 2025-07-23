import logging
from typing import Any, Dict, List

import requests
from decouple import config
from requests.exceptions import HTTPError, RequestException, Timeout

logger = logging.getLogger(__name__)


class SymplaAPIClient:
    """Handles low-level communication with Sympla API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'S_Token': token})

    def get(self, url: str, timeout: int = 15) -> Dict[str, Any] | None:
        """Make a GET request to the API with error handling."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Timeout:
            logger.error('Timeout on request to Sympla API: %s', url)
        except HTTPError as http_err:
            self._log_http_error(http_err, url)
        except RequestException as e:
            logger.error('Communication error with Sympla API: %s', e)
        return None

    def _log_http_error(self, error: HTTPError, url: str) -> None:
        """Log HTTP errors with detailed information."""
        status_code = getattr(error.response, 'status_code', 'unknown')
        logger.error(
            'HTTP error accessing Sympla API: %s - Status: %s - URL: %s',
            error,
            status_code,
            url,
        )


class SymplaService:
    """Service class to interact with the Sympla API."""

    def __init__(self):
        self.token = self._get_config_value('SYMPLA_API_TOKEN')
        self.base_url = self._get_config_value('SYMPLA_BASE_URL')
        self.api_client = SymplaAPIClient(self.base_url, self.token)

    def _get_config_value(self, key: str) -> str:
        """Get required configuration value or raise ValueError."""
        value = config(key, default=None)
        if not value:
            raise ValueError(f'Sympla API {key} is not configured.')
        return value

    def fetch_events(self) -> List[Dict[str, Any]]:
        """
        Fetches all events from Sympla, handling pagination.

        Returns:
            List of event dictionaries. Returns empty list on communication error.
        """
        all_events: List[Dict[str, Any]] = []
        next_page_url = self.base_url

        while next_page_url:
            logger.info('Fetching events from URL: %s', next_page_url)
            data = self.api_client.get(next_page_url)

            if not data:
                break

            all_events.extend(data.get('data', []))
            next_page_url = self._get_next_page_url(data)

        logger.info('Total of %d events found in Sympla API.', len(all_events))
        return all_events

    def _get_next_page_url(self, data: Dict[str, Any]) -> str | None:
        """Extract next page URL from pagination data if available."""
        pagination = data.get('pagination', {})
        return (
            pagination.get('next_page_url')
            if pagination.get('has_next')
            else None
        )
