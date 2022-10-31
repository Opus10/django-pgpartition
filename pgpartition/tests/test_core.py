import datetime as dt

import ddf
import pytest

import pgpartition.tests.models as test_models


@pytest.mark.django_db()
def test_time_partition():
    ddf.G(test_models.TimePartition, created_at=dt.datetime(2020, 11, 1))


@pytest.mark.django_db()
def test_int_partition():
    ddf.G(test_models.IntPartition)
