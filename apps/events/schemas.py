from datetime import datetime

from dateutil.parser import parse as parse_datetime
from pydantic import BaseModel, computed_field, field_validator

from utils.enums import EventType


class AddressSchema(BaseModel):
    name: str | None = None
    city: str | None = None


class SymplaEventSchema(BaseModel):
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    address: AddressSchema | None = None
    category_prim: str | dict
    category_sec: str | dict

    @computed_field
    @property
    def event_type(self) -> str:
        if not self.address or (
            not self.address.name and not self.address.city
        ):
            return EventType.ONLINE.name
        return EventType.PRESENTIAL.name

    @field_validator('start_date', 'end_date', mode='before')
    def validate_and_parsing(cls, value):
        if isinstance(value, str):
            return parse_datetime(value)

    @field_validator('category_prim', 'category_sec', mode='before')
    def get_category_name(cls, value):
        if isinstance(value, dict) and 'name' in value:
            return value['name']
        return None

    class Config:
        from_attributes = True
