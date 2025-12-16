#!/usr/bin/env python3
"""
1RM (One Rep Max) estimation formulas from exercise science literature.
All formulas take weight (w) and reps (r) and return estimated 1RM.
"""

import math


def adams(w: float, r: int) -> float:
    """Adams formula: w / (1 - 0.02r)"""
    if r >= 50:
        return float('inf')
    return w / (1 - 0.02 * r)


def baechle(w: float, r: int) -> float:
    """Baechle formula: w * (1 + 0.033r)"""
    return w * (1 + 0.033 * r)


def berger(w: float, r: int) -> float:
    """Berger formula: w / (1.0261 * e^(-0.0262r))"""
    return w / (1.0261 * math.exp(-0.0262 * r))


def brown(w: float, r: int) -> float:
    """Brown formula: w * (0.9849 + 0.0328r)"""
    return w * (0.9849 + 0.0328 * r)


def brzycki(w: float, r: int) -> float:
    """Brzycki formula: w * 36 / (37 - r)"""
    if r >= 37:
        return float('inf')
    return w * 36 / (37 - r)


def epley(w: float, r: int) -> float:
    """Epley formula: w * (1 + r/30), for r > 1"""
    if r <= 1:
        return w
    return w * (1 + r / 30)


def kemmler(w: float, r: int) -> float:
    """Kemmler et al. formula: w * (0.988 + 0.0104r + 0.00190r² - 0.0000584r³)"""
    return w * (0.988 + 0.0104 * r + 0.00190 * r**2 - 0.0000584 * r**3)


def landers(w: float, r: int) -> float:
    """Landers formula: w / (1.013 - 0.0267123r)"""
    denom = 1.013 - 0.0267123 * r
    if denom <= 0:
        return float('inf')
    return w / denom


def lombardi(w: float, r: int) -> float:
    """Lombardi formula: w * r^0.10"""
    if r <= 0:
        return w
    return w * (r ** 0.10)


def mayhew(w: float, r: int) -> float:
    """Mayhew et al. formula: w / (0.522 + 0.419 * e^(-0.055r))"""
    return w / (0.522 + 0.419 * math.exp(-0.055 * r))


def naclerio(w: float, r: int) -> float:
    """Naclerio et al. formula: w / (0.951 * e^(-0.021r))"""
    return w / (0.951 * math.exp(-0.021 * r))


def oconner(w: float, r: int) -> float:
    """O'Conner et al. formula: w * (1 + 0.025r)"""
    return w * (1 + 0.025 * r)


def wathen(w: float, r: int) -> float:
    """Wathen formula: w / (0.4880 + 0.538 * e^(-0.075r))"""
    return w / (0.4880 + 0.538 * math.exp(-0.075 * r))


# All available formulas
ALL_FORMULAS = {
    "adams": adams,
    "baechle": baechle,
    "berger": berger,
    "brown": brown,
    "brzycki": brzycki,
    "epley": epley,
    "kemmler": kemmler,
    "landers": landers,
    "lombardi": lombardi,
    "mayhew": mayhew,
    "naclerio": naclerio,
    "oconner": oconner,
    "wathen": wathen,
}

# Most commonly used and validated formulas
RECOMMENDED_FORMULAS = {
    "brzycki": brzycki,
    "epley": epley,
}


def estimate_1rm(w: float, r: int, formula: str = "brzycki") -> float:
    """Estimate 1RM using specified formula."""
    if formula not in ALL_FORMULAS:
        raise ValueError(f"Unknown formula: {formula}. Available: {list(ALL_FORMULAS.keys())}")
    return ALL_FORMULAS[formula](w, r)


def estimate_1rm_average(w: float, r: int) -> float:
    """Estimate 1RM as average of Brzycki and Epley (most common pair)."""
    return (brzycki(w, r) + epley(w, r)) / 2


def estimate_1rm_conservative(w: float, r: int) -> float:
    """Estimate 1RM using minimum of all formulas (conservative estimate)."""
    return min(f(w, r) for f in ALL_FORMULAS.values())


def estimate_1rm_all(w: float, r: int) -> dict[str, float]:
    """Return 1RM estimates from all formulas."""
    return {name: f(w, r) for name, f in ALL_FORMULAS.items()}


if __name__ == "__main__":
    # Test with example: 12 reps at 32kg
    w, r = 32, 12
    print(f"Estimating 1RM for {r} reps @ {w}kg:\n")

    results = estimate_1rm_all(w, r)
    for name, value in sorted(results.items(), key=lambda x: x[1]):
        print(f"  {name:<12} {value:.1f}kg")

    print(f"\n  Average (Brzycki/Epley): {estimate_1rm_average(w, r):.1f}kg")
