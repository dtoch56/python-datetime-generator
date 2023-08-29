import re
import random

from typing import Dict, Optional, Union
from datetime import tzinfo as TzInfo
from datetime import date as dtdate
from datetime import date, datetime, timedelta
from calendar import timegm
from dateutil.tz import tzlocal, tzutc


DateParseType = Union[date, datetime, timedelta, str, int]


def datetime_to_timestamp(dt: Union[dtdate, datetime]) -> int:
    if isinstance(dt, datetime) and getattr(dt, "tzinfo", None) is not None:
        dt = dt.astimezone(tzutc())
    return timegm(dt.timetuple())


def convert_timestamp_to_datetime(timestamp: Union[int, float], tzinfo: TzInfo) -> datetime:
    import datetime as dt

    if timestamp >= 0:
        return dt.datetime.fromtimestamp(timestamp, tzinfo)
    else:
        return dt.datetime(1970, 1, 1, tzinfo=tzinfo) + dt.timedelta(seconds=int(timestamp))


class ParseError(ValueError):
    pass


timedelta_pattern: str = r""
for name, sym in [
    ("years", "y"),
    ("months", "M"),
    ("weeks", "w"),
    ("days", "d"),
    ("hours", "h"),
    ("minutes", "m"),
    ("seconds", "s"),
]:
    timedelta_pattern += r"((?P<{}>(?:\+|-)\d+?){})?".format(name, sym)


class DateGenerator:

    regex = re.compile(timedelta_pattern)

    @classmethod
    def _parse_date_time(cls, value: DateParseType, tzinfo: Optional[TzInfo] = None) -> int:
        if isinstance(value, (datetime, dtdate)):
            return datetime_to_timestamp(value)
        now = datetime.now(tzinfo)
        if isinstance(value, timedelta):
            return datetime_to_timestamp(now + value)
        if isinstance(value, str):
            if value == "now":
                return datetime_to_timestamp(datetime.now(tzinfo))
            time_params = cls._parse_date_string(value)
            return datetime_to_timestamp(now + timedelta(**time_params))  # type: ignore
        if isinstance(value, int):
            return value
        raise ParseError(f"Invalid format for date {value!r}")

    @classmethod
    def _parse_date_string(cls, value: str) -> Dict[str, float]:
        parts = cls.regex.match(value)
        if not parts:
            raise ParseError(f"Can't parse date string `{value}`")
        parts = parts.groupdict()
        time_params: Dict[str, float] = {}
        for name_, param_ in parts.items():
            if param_:
                time_params[name_] = int(param_)

        if "years" in time_params:
            if "days" not in time_params:
                time_params["days"] = 0
            time_params["days"] += 365.24 * time_params.pop("years")
        if "months" in time_params:
            if "days" not in time_params:
                time_params["days"] = 0
            time_params["days"] += 30.42 * time_params.pop("months")

        if not time_params:
            raise ParseError(f"Can't parse date string `{value}`")
        return time_params

    def date_time_between_dates(
            self,
            datetime_start: Optional[DateParseType] = None,
            datetime_end: Optional[DateParseType] = None,
            tzinfo: Optional[TzInfo] = None,
    ) -> datetime:
        """
        Takes two datetime objects and returns a random datetime between the two
        given datetimes.
        Accepts datetime objects.

        :param datetime_start: datetime
        :param datetime_end: datetime
        :param tzinfo: timezone, instance of datetime.tzinfo subclass
        :example: datetime('1999-02-02 11:42:52')
        :return: datetime
        """
        datetime_start_ = (
            datetime_to_timestamp(datetime.now(tzinfo))
            if datetime_start is None
            else self._parse_date_time(datetime_start)
        )
        datetime_end_ = (
            datetime_to_timestamp(datetime.now(tzinfo)) if datetime_end is None else self._parse_date_time(datetime_end)
        )

        timestamp = random.randint(datetime_start_, datetime_end_)
        try:
            if tzinfo is None:
                pick = convert_timestamp_to_datetime(timestamp, tzlocal())
                try:
                    pick = pick.astimezone(tzutc()).replace(tzinfo=None)
                except OSError:
                    pass
            else:
                pick = datetime.fromtimestamp(timestamp, tzinfo)
        except OverflowError:
            raise OverflowError(
                "You specified an end date with a timestamp bigger than the maximum allowed on this"
                " system. Please specify an earlier date.",
            )
        return pick

    def date_between_dates(
            self,
            date_start: Optional[DateParseType] = None,
            date_end: Optional[DateParseType] = None,
    ) -> dtdate:
        """
        Takes two Date objects and returns a random date between the two given dates.
        Accepts Date or datetime objects

        :param date_start: Date
        :param date_end: Date
        :return: Date
        """
        return self.date_time_between_dates(date_start, date_end).date()

