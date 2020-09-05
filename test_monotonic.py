# vi: set ft=python ts=4 sw=4 et:
from sys import path
from time import sleep
from monotonic_time import monotonic


def test_order_of_magnitude():
    t0 = monotonic()
    t1 = monotonic()
    sleep(2)
    t2 = monotonic()
    assert t0 <= t1 < t2
    assert 1.5 < t2 - t1 < 2.5
