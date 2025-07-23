from enum import Enum


class EventType(Enum):
    PRESENTIAL = 'Presencial'
    ONLINE = 'Online'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]


class LogLevel(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]


class Status(Enum):
    SUCCESS = 'Sucesso'
    ERROR = 'Error'
    PENDING = 'Pendente'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]
