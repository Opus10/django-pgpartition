from django.db import models

import pgpartition


class TimePartition(models.Model):
    created_at = models.DateTimeField(primary_key=True)
    int_field = models.IntegerField()

    class Meta:
        partition = pgpartition.Partition(
            method=pgpartition.RANGE, key="created_at", interval=pgpartition.DAILY
        )


class PartitionFK(models.Model):
    partition = models.ForeignKey(TimePartition, on_delete=models.CASCADE)


class IntPartition(models.Model):
    class Meta:
        partition = pgpartition.Partition(
            method=pgpartition.RANGE, key="id", interval=1000
        )
