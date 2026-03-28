from __future__ import annotations

import os
import json
import time
from typing import Any

from concierge.catalog import CatalogItem, build_basic_search_index
from concierge.llm import (
    best_effort_chat_completion_text,
    best_effort_chat_completion_json,
    get_default_model,
    is_llm_available,
)
from concierge.models import (
    AgentResult,
    AuditStep,
    ChatTurn,
    NeedIdentification,
    OnboardingAction,
    PersonaProfile,
    ProductRecommendationItem,
)


DISCLAIMER = (
    "Disclaimer: This demo provides general guidance based on public information and user inputs. "
    "It is not licensed financial advice. Please consult a SEBI/RBI-registered professional for decisions."
)


# ---------------------------------------------------------------------------
# AGENT 1: Profile Extraction
# ---------------------------------------------------------------------------

def _persona_deterministic(scenario_id: str) -> PersonaProfile:
    """Deterministic fallback for persona extraction."""
    PERSONAS = {
        "cold_start_beginner": PersonaProfile(
            userPersona="cold_start_beginner",
            stageLabel="First-time investor (SIP-curious)",
            goals=["start SIP", "build long-term wealth"],
            riskComfort="medium",
            preferences={"languageTone": "simple_non_jargon"},
        ),
        "reengagement_prime": PersonaProfile(
            userPersona="reengaged_prime",
            stageLabel="Lapsed ET Prime subscriber (small-cap curiosity)",
            goals=["get back up to speed", "refresh small-cap learning path"],
            riskComfort="medium",
            preferences={"languageTone": "reassuring_data_driven"},
        ),
        "cross_sell_home_loan": PersonaProfile(
            userPersona="home_buy_intent",
            stageLabel="Life-event: home buyer researching affordability",
            goals=["estimate EMI", "compare home loan rates", "make next step decision"],
            riskComfort="low",
            preferences={"languageTone": "practical_short"},
        ),
    }
    return PERSONAS.get(scenario_id, PersonaProfile(
        userPersona="seasoned_investor",
        stageLabel="Seasoned investor",
        goals=[],
        riskComfort="medium",
        preferences={},
    ))


def run_profile_agent(
    scenario_id: str,
    user_message: str,
    raw_signals: dict[str, Any],
    llm_model: str,
) -> AgentResult:
    """
    Agent A — Profile Extraction.
    Attempts LLM-powered profiling from the user message and signals.
    Falls back to deterministic rules if LLM is unavailable.
    """
    t0 = time.time()
    persona = _persona_deterministic(scenario_id)
    llm_used = False
    reasoning = f"Deterministic profile: {persona.stageLabel}"
    error = None

    if is_llm_available():
        try:
            system = (
                "You are an ET AI Concierge Profile Agent. Analyze the user message and signals "
                "to extract a user profile. Return a JSON object with these fields:\n"
                '- "stageLabel": a short human-readable financial stage description\n'
                '- "goals": list of 2-3 specific financial goals\n'
                '- "riskComfort": "low", "medium", or "high"\n'
                '- "reasoning": 1-2 sentences explaining your profiling logic\n'
                "Be concise. Base your analysis on the user's actual words and context."
            )
            user_payload = json.dumps({
                "user_message": user_message,
                "signals": raw_signals,
                "scenario_id": scenario_id,
            })
            result = best_effort_chat_completion_json(model=llm_model, system=system, user=user_payload)
            if result:
                llm_used = True
                reasoning = result.get("reasoning", reasoning)
                persona = PersonaProfile(
                    userPersona=persona.userPersona,  # keep deterministic bucket
                    stageLabel=result.get("stageLabel", persona.stageLabel),
                    goals=result.get("goals", persona.goals),
                    riskComfort=result.get("riskComfort", persona.riskComfort),
                    preferences=persona.preferences,
                )
        except Exception as e:
            error = f"LLM profiling failed, using deterministic: {str(e)}"

    duration = (time.time() - t0) * 1000
    return AgentResult(
        agentName="Profile Agent",
        success=True,
        data=persona.model_dump(),
        reasoning=reasoning,
        durationMs=round(duration, 1),
        llmUsed=llm_used,
        error=error,
    )


# ---------------------------------------------------------------------------
# AGENT 2: Need Identification
# ---------------------------------------------------------------------------

def _need_deterministic(scenario_id: str) -> NeedIdentification:
    """Deterministic fallback for need identification."""
    NEEDS = {
        "cold_start_beginner": NeedIdentification(
            primaryNeed="Understand how to start SIP investing with clarity",
            secondaryNeeds=["pick a sensible learning path", "avoid common beginner mistakes"],
            toneGuidance="Use warm, plain language. Ask at most one clarifying question and then recommend next steps.",
            questionsToAsk=["What is your rough time horizon: 3–5 years, 5–10 years, or 10+ years?"],
        ),
        "reengagement_prime": NeedIdentification(
            primaryNeed="Restart with a personalized small-cap investing path",
            secondaryNeeds=["address why they may have lapsed", "show new, relevant value quickly"],
            toneGuidance="Be empathetic, specific, and non-pushy. Connect to their earlier interest in small-caps.",
            questionsToAsk=[],
        ),
        "cross_sell_home_loan": NeedIdentification(
            primaryNeed="Get home-loan rate and EMI affordability guidance",
            secondaryNeeds=["compare rates in a structured way", "take a next action"],
            toneGuidance="Be concise and action-oriented. Mention calculator + rate comparison links.",
            questionsToAsk=[],
        ),
    }
    return NEEDS.get(scenario_id, NeedIdentification(
        primaryNeed="Financial guidance",
        secondaryNeeds=[],
        toneGuidance="Be helpful.",
        questionsToAsk=[],
    ))


def run_need_agent(
    scenario_id: str,
    user_message: str,
    persona: PersonaProfile,
    llm_model: str,
) -> AgentResult:
    """
    Agent B — Need Identification.
    Analyzes the user's message in context of their profile to identify financial needs.
    """
    t0 = time.time()
    need = _need_deterministic(scenario_id)
    llm_used = False
    reasoning = f"Deterministic need: {need.primaryNeed}"
    error = None

    if is_llm_available():
        try:
            system = (
                "You are an ET AI Concierge Need Agent. Given a user profile and their message, "
                "identify their primary financial need and secondary needs. Return JSON:\n"
                '- "primaryNeed": one-sentence description of the main need\n'
                '- "secondaryNeeds": list of 1-2 secondary needs\n'
                '- "toneGuidance": how the concierge should speak to this user\n'
                '- "questionsToAsk": 0-1 clarifying questions (keep cold-start under 3 turns)\n'
                '- "reasoning": 1-2 sentences explaining how you identified these needs\n'
                "Be specific to the user's actual situation."
            )
            user_payload = json.dumps({
                "user_message": user_message,
                "persona": persona.model_dump(),
                "scenario_id": scenario_id,
            })
            result = best_effort_chat_completion_json(model=llm_model, system=system, user=user_payload)
            if result:
                llm_used = True
                reasoning = result.get("reasoning", reasoning)
                need = NeedIdentification(
                    primaryNeed=result.get("primaryNeed", need.primaryNeed),
                    secondaryNeeds=result.get("secondaryNeeds", need.secondaryNeeds),
                    toneGuidance=result.get("toneGuidance", need.toneGuidance),
                    questionsToAsk=result.get("questionsToAsk", need.questionsToAsk)[:1],
                )
        except Exception as e:
            error = f"LLM need analysis failed, using deterministic: {str(e)}"

    duration = (time.time() - t0) * 1000
    return AgentResult(
        agentName="Need Agent",
        success=True,
        data=need.model_dump(),
        reasoning=reasoning,
        durationMs=round(duration, 1),
        llmUsed=llm_used,
        error=error,
    )


# ---------------------------------------------------------------------------
# AGENT 3: Product Recommendation
# ---------------------------------------------------------------------------

def _rank_products_deterministic(
    catalog: list[CatalogItem],
    search_index: dict[str, list[CatalogItem]],
    need: NeedIdentification,
) -> list[ProductRecommendationItem]:
    """Deterministic tag-based product ranking."""
    combined = need.primaryNeed + " " + " ".join(need.secondaryNeeds)
    combined_lower = combined.lower()

    tag_queries: list[str] = []
    if "SIP" in need.primaryNeed or "SIP" in combined:
        tag_queries = ["SIP", "beginner", "mutual-funds", "goal-based"]
    elif "small-cap" in combined_lower:
        tag_queries = ["small-cap", "ETPrime", "mid-cap"]
    elif "home" in combined_lower or "EMI" in need.primaryNeed:
        tag_queries = ["home-loan", "EMI", "home-buyer"]
    else:
        tag_queries = ["beginner"]

    scored: dict[str, float] = {}
    for tag in tag_queries:
        for item in search_index.get(tag, []):
            scored[item.id] = scored.get(item.id, 0.0) + 1.0

    if not scored:
        return []

    max_score = max(scored.values()) or 1.0
    ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
    return [
        ProductRecommendationItem(
            productId=pid,
            reason=f"Matches your need via tags: {', '.join(tag_queries)}",
            matchScore=round(score / max_score, 3),
        )
        for pid, score in ranked[:3]
    ]


def run_product_agent(
    scenario_id: str,
    user_message: str,
    persona: PersonaProfile,
    need: NeedIdentification,
    catalog: list[CatalogItem],
    llm_model: str,
) -> AgentResult:
    """
    Agent C — Product Recommendation.
    Ranks ET products by relevance. Uses deterministic tag matching for reliability,
    then optionally enhances recommendation reasons with LLM.
    """
    t0 = time.time()
    search_index = build_basic_search_index(catalog)
    rec_items = _rank_products_deterministic(catalog, search_index, need)
    llm_used = False
    reasoning = "Tag-based deterministic product ranking"
    error = None

    # Optionally enhance reasons with LLM
    if is_llm_available() and rec_items:
        try:
            selected_products = [item for item in catalog if item.id in {r.productId for r in rec_items}]
            system = (
                "You are an ET AI Concierge Product Agent. Given the user's profile, needs, "
                "and a set of pre-ranked product matches, write a brief personalized reason "
                "(1 sentence each) for why each product is relevant. Return JSON:\n"
                '- "reasons": dict mapping productId to a personalized reason string\n'
                '- "reasoning": 1 sentence explaining your ranking logic'
            )
            user_payload = json.dumps({
                "persona": persona.model_dump(),
                "need": need.model_dump(),
                "products": [{"id": p.id, "title": p.title, "type": p.productType, "tags": p.categoryTags} for p in selected_products],
            })
            result = best_effort_chat_completion_json(model=llm_model, system=system, user=user_payload)
            if result and "reasons" in result:
                llm_used = True
                reasoning = result.get("reasoning", reasoning)
                reasons_map = result["reasons"]
                for item in rec_items:
                    if item.productId in reasons_map:
                        item.reason = reasons_map[item.productId]
        except Exception as e:
            error = f"LLM reason enhancement failed, using tag-based reasons: {str(e)}"

    duration = (time.time() - t0) * 1000
    return AgentResult(
        agentName="Product Agent",
        success=True,
        data={"recommendations": [r.model_dump() for r in rec_items]},
        reasoning=reasoning,
        durationMs=round(duration, 1),
        llmUsed=llm_used,
        error=error,
    )


# ---------------------------------------------------------------------------
# AGENT 4: Onboarding Action
# ---------------------------------------------------------------------------

def _onboarding_deterministic(
    scenario_id: str,
    persona: PersonaProfile,
    need: NeedIdentification,
    selected_products: list[CatalogItem],
) -> tuple[str, list[str]]:
    """Deterministic onboarding message and next steps."""
    if scenario_id == "cold_start_beginner":
        ask = need.questionsToAsk[0] if need.questionsToAsk else "What's your rough time horizon (3–5y / 5–10y / 10y+)?"
        next_steps = [
            f"Answer this to personalize: {ask}",
            f"Start with: {selected_products[0].title}" if selected_products else "Explore ET beginner content",
            f"Then join: {selected_products[1].title}" if len(selected_products) > 1 else "Then explore ET Masterclass",
        ]
        msg = (
            f"Welcome to ET AI Concierge! Quick question to personalize your journey: {ask}\n\n"
            "Based on your beginner stage, here are your ET starting points:\n"
        )
        for i, p in enumerate(selected_products[:3], 1):
            msg += f"{i}) {p.title}\n   Link: {p.url}\n"
        msg += "\nPick one to start your first week — we'll keep it simple and build from there."

    elif scenario_id == "reengagement_prime":
        next_steps = [
            "Re-enter with a curated small-cap learning sequence.",
            f"Start reading: {selected_products[0].title}" if selected_products else "Check latest ET Prime articles",
            f"Follow with: {selected_products[1].title}" if len(selected_products) > 1 else "Follow with a related deep-dive",
        ]
        msg = (
            "Welcome back! Since you previously spent time on markets content and small-cap webinars, "
            "you probably lapsed because the feed felt overwhelming without a clear path.\n\n"
            "Here's a focused re-start for your small-cap interest:\n"
        )
        for i, p in enumerate(selected_products[:3], 1):
            msg += f"{i}) {p.title}\n   Link: {p.url}\n"
        msg += "\nTell me: is your goal 'capital growth' or 'safer returns'? I'll suggest the smallest next action."

    elif scenario_id == "cross_sell_home_loan":
        next_steps = [
            "Estimate your EMI quickly using the calculator.",
            f"Compare lending rates: {selected_products[0].title}" if selected_products else "Check ET home loan comparison",
            f"Use: {selected_products[1].title}" if len(selected_products) > 1 else "Then compute your EMI",
        ]
        msg = (
            "Got it — researching home loan rates usually means you're preparing for a big step. "
            "Let's make this practical:\n\n"
        )
        for i, p in enumerate(selected_products[:3], 1):
            msg += f"{i}) {p.title}\n   Link: {p.url}\n"
        msg += "\nNext: pick your approximate loan amount + tenure, run the EMI calculator, then compare rates."

    else:
        next_steps = ["Start with ET beginner guidance", "Share your goals for a tailored path."]
        msg = "Here are a few ET starting points based on your request. Share your time horizon and goal for personalization."

    return msg, next_steps


def run_onboarding_agent(
    scenario_id: str,
    user_message: str,
    persona: PersonaProfile,
    need: NeedIdentification,
    selected_products: list[CatalogItem],
    llm_model: str,
) -> AgentResult:
    """
    Agent D — Onboarding Action.
    Creates personalized onboarding message and action plan.
    Uses LLM to rewrite the deterministic message with a warmer tone.
    """
    t0 = time.time()
    assistant_message, next_steps = _onboarding_deterministic(
        scenario_id, persona, need, selected_products
    )
    llm_used = False
    reasoning = "Deterministic scenario-based onboarding message"
    error = None

    # LLM tone rewrite — keeps product selection deterministic, only improves phrasing
    if is_llm_available():
        try:
            system = (
                "You are an ET AI Concierge Onboarding Agent. Rewrite the onboarding message below "
                "to be warmer, more conversational, and non-jargony. Rules:\n"
                "- Keep ALL product recommendations and links exactly as given\n"
                "- Keep the same structure (numbered list with links)\n"
                "- Do NOT add new products or remove existing ones\n"
                "- Match the tone guidance for this user persona\n"
                "- Do NOT include disclaimers (the UI adds them separately)\n"
                "- Keep it under 200 words\n"
                "Return ONLY the rewritten message as plain text."
            )
            user_payload = json.dumps({
                "persona_stage": persona.stageLabel,
                "tone_guidance": need.toneGuidance,
                "current_message": assistant_message,
                "next_steps": next_steps,
            })
            rewritten = best_effort_chat_completion_text(model=llm_model, system=system, user=user_payload)
            if rewritten and len(rewritten) > 50:
                assistant_message = rewritten
                llm_used = True
                reasoning = "LLM-rewritten onboarding with warm, personalized tone"
        except Exception as e:
            error = f"LLM rewrite failed, using deterministic message: {str(e)}"

    onboarding = OnboardingAction(
        assistantMessage=assistant_message + "\n\n" + DISCLAIMER,
        nextSteps=next_steps,
        selectedProductIds=[p.id for p in selected_products],
        disclaimer=DISCLAIMER,
    )

    duration = (time.time() - t0) * 1000
    return AgentResult(
        agentName="Onboarding Agent",
        success=True,
        data=onboarding.model_dump(),
        reasoning=reasoning,
        durationMs=round(duration, 1),
        llmUsed=llm_used,
        error=error,
    )


# ---------------------------------------------------------------------------
# ORCHESTRATOR — Multi-Step Autonomous Journey
# ---------------------------------------------------------------------------

def run_concierge_journey(
    scenario_id: str,
    user_message: str,
    catalog: list[CatalogItem],
    llm_model: str | None = None,
    raw_signals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Multi-step autonomous journey orchestrator.
    Runs 4 agents in sequence with full audit trail:
      Profile Agent → Need Agent → Product Agent → Onboarding Agent

    Each agent:
    - Attempts LLM-powered analysis first
    - Falls back to deterministic rules if LLM unavailable
    - Records timing, reasoning, and any errors in the audit trail
    """
    if llm_model is None:
        llm_model = get_default_model()

    if raw_signals is None:
        raw_signals = {}

    audit: list[AuditStep] = []
    agent_results: list[AgentResult] = []

    # ── Step 1: Profile Agent ──
    profile_result = run_profile_agent(scenario_id, user_message, raw_signals, llm_model)
    agent_results.append(profile_result)
    persona = PersonaProfile(**profile_result.data)
    audit.append(AuditStep(
        stepName="Profile extraction",
        agentName="Profile Agent",
        inputSummary=f"scenario_id={scenario_id}, user_message={user_message[:120]}",
        outputJSON=profile_result.data,
        durationMs=profile_result.durationMs,
        llmUsed=profile_result.llmUsed,
        error=profile_result.error,
    ))

    # ── Step 2: Need Agent ──
    need_result = run_need_agent(scenario_id, user_message, persona, llm_model)
    agent_results.append(need_result)
    need = NeedIdentification(**need_result.data)
    audit.append(AuditStep(
        stepName="Need identification",
        agentName="Need Agent",
        inputSummary=f"persona={persona.stageLabel}",
        outputJSON=need_result.data,
        durationMs=need_result.durationMs,
        llmUsed=need_result.llmUsed,
        error=need_result.error,
    ))

    # ── Step 3: Product Agent ──
    product_result = run_product_agent(scenario_id, user_message, persona, need, catalog, llm_model)
    agent_results.append(product_result)
    rec_items = [ProductRecommendationItem(**r) for r in product_result.data.get("recommendations", [])]
    selected_ids = {r.productId for r in rec_items}
    selected_products = [item for item in catalog if item.id in selected_ids]
    # Keep ranked order
    id_order = [r.productId for r in rec_items]
    selected_products.sort(key=lambda p: id_order.index(p.id) if p.id in id_order else 999)
    audit.append(AuditStep(
        stepName="Product recommendation",
        agentName="Product Agent",
        inputSummary=f"primaryNeed={need.primaryNeed}",
        outputJSON=product_result.data,
        durationMs=product_result.durationMs,
        llmUsed=product_result.llmUsed,
        error=product_result.error,
    ))

    # ── Step 4: Onboarding Agent ──
    onboarding_result = run_onboarding_agent(
        scenario_id, user_message, persona, need, selected_products, llm_model
    )
    agent_results.append(onboarding_result)
    onboarding = OnboardingAction(**onboarding_result.data)
    audit.append(AuditStep(
        stepName="Onboarding action",
        agentName="Onboarding Agent",
        inputSummary=f"products={[p.title[:40] for p in selected_products]}",
        outputJSON=onboarding_result.data,
        durationMs=onboarding_result.durationMs,
        llmUsed=onboarding_result.llmUsed,
        error=onboarding_result.error,
    ))

    # ── Build chat transcript ──
    chat: list[ChatTurn] = [ChatTurn(role="user", content=user_message)]
    if scenario_id == "cold_start_beginner":
        ask = need.questionsToAsk[0] if need.questionsToAsk else "What's your rough time horizon (3–5y / 5–10y / 10y+)?"
        chat.append(ChatTurn(role="assistant", content=onboarding.assistantMessage.split("\n\n")[0]))
        chat.append(ChatTurn(role="user", content="10+ years (I want long-term wealth for retirement)."))
        chat.append(ChatTurn(role="assistant", content="Here's your personalized onboarding path:\n\n" + onboarding.assistantMessage))
    else:
        chat.append(ChatTurn(role="assistant", content=onboarding.assistantMessage))

    # ── Total timing ──
    total_duration = sum(r.durationMs for r in agent_results)
    llm_steps = sum(1 for r in agent_results if r.llmUsed)

    return {
        "persona": persona.model_dump(),
        "need": need.model_dump(),
        "recommendations": [r.model_dump() for r in rec_items],
        "selectedProducts": [p.__dict__ for p in selected_products],
        "onboarding": onboarding.model_dump(),
        "audit": [a.model_dump() for a in audit],
        "agentResults": [r.model_dump() for r in agent_results],
        "chatTranscript": [c.model_dump() for c in chat],
        "meta": {
            "totalDurationMs": round(total_duration, 1),
            "llmStepsUsed": llm_steps,
            "totalSteps": len(agent_results),
            "model": llm_model,
        },
    }
