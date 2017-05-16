# vi: set ft=python ts=4 sw=4 et:
from __future__ import print_function
from __future__ import unicode_literals
import math
import time
import monotonic_time


def test_order_of_magnitude():
    first = monotonic_time.monotonic()
    time.sleep(3)
    second = monotonic_time.monotonic()
    assert second > first
    distance = math.fabs(second - first)
    assert distance > 2.5
    assert distance < 3.5
