from unittest.mock import MagicMock, patch

import pytest
import requests

from apps.events.services import SymplaService


@patch('apps.events.services.requests.Session.get')
def test_fetch_events_success_single_page(mock_get):
    """
    Test the fetch_events method for successful single-page response.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': [{'id': 1, 'name': 'Evento Mockado 1'}],
        'pagination': {'has_next': False},
    }
    mock_get.return_value = mock_response

    service = SymplaService()
    events = service.fetch_events()

    assert len(events) == 1
    assert events[0]['name'] == 'Evento Mockado 1'

    mock_get.assert_called_once()


@patch('apps.events.services.requests.Session.get')
def test_fetch_events_handles_pagination(mock_get):
    """Test the fetch_events method for successful multi-page response."""
    response_page1 = MagicMock()
    response_page1.status_code = 200
    response_page1 = MagicMock()
    response_page1.json.return_value = {
        'data': [{'id': 1, 'name': 'Evento da Página 1'}],
        'pagination': {
            'has_next': True,
            'next_page_url': 'http://api.com/page2',
        },
    }

    response_page2 = MagicMock()
    EVENTS_COUNT = 2
    response_page2.json.return_value = {
        'data': [{'id': 2, 'name': 'Evento da Página 2'}],
        'pagination': {'has_next': False},
    }

    mock_get.side_effect = [response_page1, response_page2]

    service = SymplaService()
    events = service.fetch_events()

    assert len(events) == EVENTS_COUNT
    assert events[0]['name'] == 'Evento da Página 1'
    assert events[1]['name'] == 'Evento da Página 2'
    assert mock_get.call_count == EVENTS_COUNT


@patch('apps.events.services.requests.Session.get')
def test_fetch_events_handles_http_error(mock_get):
    """Test the fetch_events method for HTTP errors."""
    mock_response = MagicMock()
    mock_response.status_code = 500

    http_error = requests.exceptions.HTTPError(
        'Server Error', response=mock_response
    )
    mock_get.side_effect = http_error

    service = SymplaService()
    events = service.fetch_events()

    assert events == []
    mock_get.assert_called_once()


@patch('apps.events.services.requests.Session.get')
def test_fetch_events_handles_timeout(mock_get):
    """Test the fetch_events method for timeout errors."""
    mock_get.side_effect = requests.exceptions.Timeout('Request timed out')

    service = SymplaService()
    events = service.fetch_events()

    assert events == []
    mock_get.assert_called_once()


@patch('apps.events.services.config', return_value=None)
def test_service_initialization_fails_without_token(mock_config):
    """
    Test that SymplaService initialization fails if SYMPLA_API_TOKEN is not
    set.
    """

    with pytest.raises(ValueError) as excinfo:  # noqa: PT011
        SymplaService()

    assert 'Sympla API SYMPLA_API_TOKEN is not configured.' in str(
        excinfo.value
    )
