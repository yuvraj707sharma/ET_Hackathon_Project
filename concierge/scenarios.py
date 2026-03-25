from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScenarioInput:
    scenarioId: str
    title: str
    rawUserSignals: dict[str, Any]
    initialUserMessage: str


SCENARIOS: dict[str, ScenarioInput] = {
    "cold_start_beginner": ScenarioInput(
        scenarioId="cold_start_beginner",
        title="Cold-start onboarding (<= 3 turns)",
        initialUserMessage="Hi! I’m new to investing. I’ve heard about SIPs but I’m not sure where to start.",
        rawUserSignals={
            "age": 28,
            "salaried": True,
            "investingHistory": "savings_account_only",
            "awareness": ["SIPs"],
            "goalAwareness": "vague",
        },
    ),
    "reengagement_prime": ScenarioInput(
        scenarioId="reengagement_prime",
        title="Re-engagement (lapsed ET Prime)",
        initialUserMessage="I’m back on ET after not using ET Prime for a while. I used to read markets content and attended some small-cap webinars.",
        rawUserSignals={
            "primeLapseDays": 90,
            "previousUsage": {
                "consumed": ["markets_content", "small_cap_articles"],
                "attended": ["small_cap_webinars", "small_cap_masterclass_like_sessions"],
            },
        },
    ),
    "cross_sell_home_loan": ScenarioInput(
        scenarioId="cross_sell_home_loan",
        title="Multi-product cross-sell moment (home loan)",
        initialUserMessage="I searched for home loan interest rates and clicked on a couple of related articles.",
        rawUserSignals={
            "searchQuery": "home loan interest rates",
            "clickedArticleThemes": ["home loan rates", "EMI affordability"],
        },
    ),
}

