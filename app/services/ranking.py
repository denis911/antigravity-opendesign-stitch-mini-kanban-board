from typing import Optional, TypeVar, List

T = TypeVar("T")

INITIAL_RANK = 1000.0
RANK_STEP = 1000.0
PRECISION_THRESHOLD = 1e-6


def calculate_rank(prev_rank: Optional[float], next_rank: Optional[float]) -> float:
    """
    Calculate new floating-point rank for card positioning according to spec 3.3.
    - Between Card A (R_A) and Card B (R_B): (R_A + R_B) / 2
    - At top of column before first card: R_first / 2
    - At bottom of column after last card: R_last + 1000.0
    - Into an empty column: 1000.0
    """
    if prev_rank is not None and next_rank is not None:
        return (prev_rank + next_rank) / 2.0
    elif prev_rank is not None and next_rank is None:
        return prev_rank + RANK_STEP
    elif prev_rank is None and next_rank is not None:
        return next_rank / 2.0
    else:
        return INITIAL_RANK


def should_rebalance(prev_rank: Optional[float], next_rank: Optional[float], threshold: float = PRECISION_THRESHOLD) -> bool:
    """
    Check if distance between adjacent ranks has collapsed below the floating point precision threshold.
    """
    if prev_rank is not None and next_rank is not None:
        return abs(next_rank - prev_rank) < threshold
    elif prev_rank is None and next_rank is not None:
        return next_rank < threshold
    return False


def rebalance_ranks(cards: List[T], start: float = RANK_STEP, step: float = RANK_STEP) -> List[T]:
    """
    Re-spaces ordered cards to [1000.0, 2000.0, 3000.0, ...].
    Cards must be passed in current sorted order.
    """
    current = start
    for card in cards:
        card.rank = current
        current += step
    return cards
