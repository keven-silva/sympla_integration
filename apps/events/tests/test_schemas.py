from datetime import datetime

import pytest
from pydantic import ValidationError

from apps.events.schemas import SymplaEventSchema
from utils.enums import EventType


def test_presential_event_schema_validation():
    """Tests that a valid payload for a presential event is correctly parsed."""
    payload = {
        'id': '12345',
        'name': 'Conferência de Python',
        'start_date': '2025-10-20T20:00:00',
        'end_date': '2025-10-21T22:00:00',
        'address': {'name': 'Centro de Convenções', 'city': 'São Paulo'},
        'category_prim': {'name': 'Tecnologia'},
        'category_sec': {'name': 'Programação'},
    }

    validated_event = SymplaEventSchema.model_validate(payload)

    assert validated_event.id == '12345'
    assert isinstance(validated_event.start_date, datetime)
    assert validated_event.event_type == EventType.PRESENTIAL.name
    assert validated_event.address.city == 'São Paulo'
    assert validated_event.category_prim == 'Tecnologia'
    assert validated_event.category_sec == 'Programação'


def test_online_event_schema_validation():
    """Tests that a valid payload for an online event is correctly parsed."""
    payload = {
        'id': '54321',
        'name': 'Live sobre Django',
        'start_date': '2025-11-05T19:00:00',
        'end_date': '2025-11-05T20:00:00',
        'address': {'address_num': 0 },
        'category_prim': {'name': 'Tecnologia'},
        'category_sec': {'name': 'Web Development'},
    }

    validated_event = SymplaEventSchema.model_validate(payload)

    assert validated_event.event_type == EventType.ONLINE.name
    assert validated_event.address.name is None
    assert validated_event.address.city is None

def test_schema_raises_validation_error_on_missing_data():
    """Tests that Pydantic raises a ValidationError for missing required fields."""
    invalid_payload = {
        'id': '99999',
        # 'name' field is missing
        'start_date': '2025-12-01T10:00:00',
        'end_date': '2025-12-01T11:00:00',
        'address': {"address_num": 0},
        'category_prim': {'name': 'Outros'},
        'category_sec': {'name': 'Geral'},
    }

    with pytest.raises(ValidationError):
        SymplaEventSchema.model_validate(invalid_payload)
