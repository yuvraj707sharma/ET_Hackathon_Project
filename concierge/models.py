from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class PersonaProfile(BaseModel):
    userPersona: Literal["cold_start_beginner", "reengaged_prime", "home_buy_intent", "seasoned_investor"]
    stageLabel: str = Field(description="Short human-readable stage.")
    goals: list[str] = Field(default_factory=list)
    riskComfort: Literal["low", "medium", "high"] = "medium"
    preferences: dict[str, Any] = Field(default_factory=dict)


class NeedIdentification(BaseModel):
    primaryNeed: str
    secondaryNeeds: list[str] = Field(default_factory=list)
    toneGuidance: str = Field(description="How the agent should speak (non-jargon, reassuring, etc.).")
    questionsToAsk: list[str] = Field(
        default_factory=list,
        description="Up to 2 questions to keep cold-start within 3 turns.",
    )


class ProductRecommendationItem(BaseModel):
    productId: str
    reason: str
    matchScore: float = Field(ge=0, le=1)


class OnboardingAction(BaseModel):
    assistantMessage: str
    nextSteps: list[str]
    selectedProductIds: list[str]
    disclaimer: str


class AuditStep(BaseModel):
    stepName: str
    agentName: str = "System"
    inputSummary: str
    outputJSON: dict[str, Any]
    durationMs: float = 0.0
    llmUsed: bool = False
    error: str | None = None


class AgentResult(BaseModel):
    """Wrapper for individual agent step results with metadata."""
    agentName: str
    success: bool = True
    data: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""
    durationMs: float = 0.0
    llmUsed: bool = False
    error: str | None = None
