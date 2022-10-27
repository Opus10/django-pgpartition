from django.db import models

import pgpartition


class Partition(models.Model):
    created_at = models.DateTimeField(primary_key=True)
    int_field = models.IntegerField()

    class Meta:
        partition = pgpartition.Partition(method=pgpartition.RANGE, key="created_at")


class PartitionFK(models.Model):
    partition = models.ForeignKey(Partition, on_delete=models.CASCADE)
