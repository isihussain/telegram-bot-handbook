from __future__ import annotations

import pytest

from tgkit.ratelimit import TokenBucket


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_burst_then_deny() -> None:
    limiter = TokenBucket(capacity=3, refill_per_second=1, clock=FakeClock())
    assert [limiter.allow("user") for _ in range(3)] == [True, True, True]
    assert limiter.allow("user") is False


def test_refills_at_the_configured_rate() -> None:
    clock = FakeClock()
    limiter = TokenBucket(capacity=2, refill_per_second=0.5, clock=clock)
    assert limiter.allow("user", 2) is True
    assert limiter.allow("user") is False

    clock.advance(1.0)  # 0.5 tokens
    assert limiter.allow("user") is False
    clock.advance(1.0)  # 1.0 token
    assert limiter.allow("user") is True


def test_keys_are_independent() -> None:
    limiter = TokenBucket(capacity=1, refill_per_second=1, clock=FakeClock())
    assert limiter.allow("alice") is True
    assert limiter.allow("alice") is False
    assert limiter.allow("bob") is True


def test_retry_after_is_a_free_probe() -> None:
    clock = FakeClock()
    limiter = TokenBucket(capacity=2, refill_per_second=0.5, clock=clock)
    assert limiter.retry_after("unknown") == 0.0
    assert limiter.allow("user", 2) is True

    assert limiter.retry_after("user") == pytest.approx(2.0)
    assert limiter.retry_after("user") == pytest.approx(2.0)  # unchanged by the probe

    clock.advance(1.0)
    assert limiter.retry_after("user") == pytest.approx(1.0)
    assert limiter.allow("user") is False

    clock.advance(1.0)
    assert limiter.allow("user") is True


def test_forget_drops_the_bucket() -> None:
    limiter = TokenBucket(capacity=1, refill_per_second=1, clock=FakeClock())
    assert limiter.allow("user") is True
    assert len(limiter) == 1
    limiter.forget("user")
    assert len(limiter) == 0
    assert limiter.allow("user") is True


@pytest.mark.parametrize(
    ("capacity", "rate"),
    [(0, 1), (-1, 1), (1, 0), (1, -0.5)],
)
def test_invalid_configuration(capacity: int, rate: float) -> None:
    with pytest.raises(ValueError):
        TokenBucket(capacity=capacity, refill_per_second=rate)


def test_cost_must_be_positive_and_within_capacity() -> None:
    limiter = TokenBucket(capacity=2, refill_per_second=1, clock=FakeClock())
    with pytest.raises(ValueError):
        limiter.allow("user", 0)
    with pytest.raises(ValueError):
        limiter.allow("user", 3)
    with pytest.raises(ValueError):
        limiter.retry_after("user", -1)


def test_bucket_is_capped_at_capacity() -> None:
    clock = FakeClock()
    limiter = TokenBucket(capacity=2, refill_per_second=10, clock=clock)
    assert limiter.allow("user", 2) is True
    clock.advance(60)
    assert limiter.allow("user", 2) is True
    assert limiter.allow("user") is False
