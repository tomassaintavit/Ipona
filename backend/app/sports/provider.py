import abc
import datetime as dt

from app.sports.models import EventResult, Sport, SportEvent


class SportsDataProvider(abc.ABC):
    @abc.abstractmethod
    async def get_day_events(self, date: dt.date, sport: Sport) -> list[SportEvent]: ...

    @abc.abstractmethod
    async def get_event_result(self, event: SportEvent) -> EventResult: ...
