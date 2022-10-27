import datetime as dt

from django.db import models


# Partition types
RANGE = "RANGE"

# Interval values
YEARLY = "yearly"
QUARTERLY = "quarterly"
MONTHLY = "monthly"
WEEKLY = "weekly"
DAILY = "daily"
HOURLY = "hourly"
HALF_HOUR = "half-hour"
QUARTER_HOUR = "quarter-hour"


class Partition:
    def __init__(
        self,
        *,
        method,
        key,
        control=None,
        interval,
        start_partition=None,
        premake=None,
    ):
        self.method = method
        self.key = [key] if not isinstance(key, (list, tuple)) else key
        self.control = control or self.key
        self.control = (
            [self.control] if not isinstance(self.control, (list, tuple)) else self.control
        )
        self.interval = interval
        self.start_partition = start_partition
        self.premake = premake

    def get_create_parent_kwargs(self, model):
        # TODO: Use
        # https://stackoverflow.com/questions/49427036/postgresql-determine-schema-from-table-name
        # to determine the schema of the table
        kwargs = {
            "p_parent_table": f"public.{model._meta.db_table}",
            "p_control": f"{model._meta.get_field(self.control[0]).column}",
            "p_type": "native",
            "p_interval": str(self.interval),
        }

        if self.premake is not None:
            kwargs["p_premake"] = self.premake

        if self.start_partition is not None:
            kwargs["p_start_partition"] = self.start_partition

        return kwargs

    def check_control_field(self, model, field):
        field = model._meta.get_field(field)

        if isinstance(field, models.IntegerField):
            if not isinstance(self.interval, int):
                raise ValueError(
                    "Inteval must be an integer when using integer-based partitioning"
                )

            if self.start_partition is not None and not isinstance(self.start_partition, int):
                raise TypeError("start_partition must be int")

        elif isinstance(field, models.DateTimeField):
            if self.interval not in (
                YEARLY,
                QUARTERLY,
                MONTHLY,
                WEEKLY,
                DAILY,
                HOURLY,
                HALF_HOUR,
                QUARTER_HOUR,
            ):
                raise ValueError(
                    "Interval must be one of pgpartition.{YEARLY, QUARTERLY,"
                    " MONTHLY, WEEKLY, DAILY, HOURLY, HALF_HOUR, or QUARTER_HOUR}"
                )

            if self.start_partition is not None and not isinstance(
                self.start_partition, dt.datetime
            ):
                raise TypeError("start_partition must be a datetime object")

        if not isinstance(field, (models.IntegerField, models.DateTimeField)):
            raise TypeError("Range partitioning can only happen over integer or datetime fields")

    def check(self, model):
        if self.method == RANGE:
            if model._meta.pk.name not in self.key:
                raise ValueError("Primary key must be in partition key")

            if len(self.control) != 1:
                raise ValueError("Must set exactly one control field for partition")

            for field in self.control:
                self.check_control_field(model, field)

            if self.premake is not None:
                if not isinstance(self.premake, int):
                    raise TypeError("premake must be an integer")
                elif not self.premake > 0:
                    raise ValueError("premake must be a positive integer")
        else:
            raise ValueError("Invalid partition method. Must be pgpartition.RANGE")

    def deconstruct(self):
        return (
            "pgpartition.Partition",
            [],
            {
                "method": self.method,
                "key": self.key,
                "control": self.control,
                "interval": self.interval,
                "start_partition": self.start_partition,
                "premake": self.premake,
            },
        )
