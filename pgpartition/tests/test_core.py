import datetime as dt

import ddf
import pytest

import pgpartition.tests.models as test_models


@pytest.mark.django_db(transaction=True)
def test_range_partition():
    ddf.G(test_models.Partition, created_at=dt.datetime(2020, 11, 1))
