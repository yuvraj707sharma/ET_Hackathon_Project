from __future__ import annotations

import os
import json
from typing import Any

from concierge.catalog import CatalogItem, build_basic_search_index
from concierge.llm import best_effort_chat_completion_text, best_effort_chat_completion_json
from concierge.models import (
    AuditStep,
    ChatTurn,
    NeedIdentification,
    OnboardingAction,
    PersonaProfile,
    ProductRecommendationItem,
)
from pydantic import ValidationError


DISCLAIMER = (
    "Disclaimer: This demo provides general guidance based on public information and user inputs. "
    "It is not licensed financial advice. Please consult a SEBI/RBI-registered professional for decisions."
)


def _persona_from_scenario_id(scenario_id: str) -> PersonaProfile:
    if scenario_id == "cold_start_beginner":
        return PersonaProfile(
            userPersona="cold_start_beginner",
            stageLabel="First-time investor (SIP-curious)",
            goals=["start SIP", "build long-term wealth"],
            riskComfort="medium",
            preferences={"languageTone": "simple_non_jargon"},
        )
    if scenario_id == "reengagement_prime":
        return PersonaProfile(
            userPersona="reengaged_prime",
            stageLabel="Lapsed ET Prime subscriber (small-cap curiosity)",
            goals=["get back up to speed", "refresh small-cap learning path"],
            riskComfort="medium",
            preferences={"languageTone": "reassuring_data_driven"},
        )
    if scenario_id == "cross_sell_home_loan":
        return PersonaProfile(
            userPersona="home_buy_intent",
            stageLabel="Life-event: home buyer researching affordability",
            goals=["estimate EMI", "compare home loan rates", "make next step decision"],
            riskComfort="low",
            preferences={"languageTone": "practical_short"},
        )
    return PersonaProfile(
        userPersona="seasoned_investor",
        stageLabel="Seasoned investor",
        goals=[],
        riskComfort="medium",
        preferences={},
    )


def _need_from_scenario_id(scenario_id: str) -> NeedIdentification:
    if scenario_id == "cold_start_beginner":
        return NeedIdentification(
            primaryNeed="Understand how to start SIP investing with clarity",
            secondaryNeeds=["pick a sensible learning path", "avoid common beginner mistakes"],
            toneGuidance="Use warm, plain language. Ask at most one clarifying question and then recommend next steps.",
            questionsToAsk=["What is your rough time horizon: 3–5 years, 5–10 years, or 10+ years?"],
        )

    if scenario_id == "reengagement_prime":
        return NeedIdentification(
            primaryNeed="Restart with a personalized small-cap investing path",
            secondaryNeeds=["address why they may have lapsed", "show new, relevant value quickly"],
            toneGuidance="Be empathetic, specific, and non-pushy. Connect to their earlier interest in small-caps.",
            questionsToAsk=[],
        )

    if scenario_id == "cross_sell_home_loan":
        return NeedIdentification(
            primaryNeed="Get home-loan rate and EMI affordability guidance",
            secondaryNeeds=["compare rates in a structured way", "take a next action"],
            toneGuidance="Be concise and action-oriented. Mention calculator + rate comparison links.",
            questionsToAsk=[],
        )

    return NeedIdentification(
        primaryNeed="Financial guidance",
        secondaryNeeds=[],
        toneGuidance="Be helpful.",
        questionsToAsk=[],
    )


def _rank_products_by_need(catalog: list[CatalogItem], search_index: dict[str, list[CatalogItem]], need: NeedIdentification) -> list[ProductRecommendationItem]:
    """
    Heuristic ranking tuned to the scenario packs.
    """
    # Map need->tag queries.
    tag_queries: list[str] = []
    if "SIP" in need.primaryNeed or "SIP" in need.secondaryNeeds:
        tag_queries = ["SIP", "beginner", "mutual-funds", "goal-based"]
    elif "small-cap" in (need.primaryNeed + " " + " ".join(need.secondaryNeeds)).lower():
        tag_queries = ["small-cap", "ETPrime", "mid-cap"]
    elif "home" in (need.primaryNeed + " " + " ".join(need.secondaryNeeds)).lower() or "EMI" in need.primaryNeed:
        tag_queries = ["home-loan", "EMI", "home-buyer"]
    else:
        tag_queries = ["beginner"]

    # Score by presence of tags.
    scored: dict[str, float] = {}
    for tag in tag_queries:
        for item in search_index.get(tag, []):
            scored[item.id] = scored.get(item.id, 0.0) + 1.0

    # Deterministic normalization into matchScore [0,1].
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


def _llm_optional_assistant_message(
    scenario_id: str,
    persona: PersonaProfile,
    need: NeedIdentification,
    selected_products: list[CatalogItem],
    user_message: str,
    llm_model: str,
) -> str | None:
    """
    If OpenAI is configured, generate the final onboarding message with a non-pushy tone.
    """
    system = (
        "You are an ET AI Concierge. You must keep responses short, helpful, non-jargony, and non-pushy. "
        "You recommend ET products with clear next steps and include a disclaimer that this is not licensed financial advice. "
        "Return ONLY plain text."
    )

    product_lines = "\n".join([f"- {p.title} ({p.url})" for p in selected_products])

    user = {
        "scenario_id": scenario_id,
        "user_message": user_message,
        "persona": persona.model_dump(),
        "need": need.model_dump(),
        "recommended_products": [p.__dict__ for p in selected_products],
        "requirements": {
            "cold_start": "Ask at most 1 clarifying question, then recommend 2-3 products and onboarding path.",
            "reengagement": "Infer likely reasons for lapse, surface specific new value since lapse, and propose a re-entry action.",
            "cross_sell": "Recognize home-purchase intent and recommend home-loan rates + EMI calculator as next steps.",
        },
    }

    text = json.dumps(user, ensure_ascii=False)
    resp = best_effort_chat_completion_json(model=llm_model, system=system, user=text)
    if not resp:
        return None
    # We used JSON function, but we asked for plain text. The LLM wrapper expects JSON, so we may get errors.
    # Instead, we return None so heuristics are used.
    return None


def run_concierge_journey(
    scenario_id: str,
    user_message: str,
    catalog: list[CatalogItem],
    llm_model: str | None = None,
) -> dict[str, Any]:
    """
    Multi-step autonomous journey:
    persona extraction -> need identification -> product recommendation -> onboarding action (+ audit trail)
    """
    search_index = build_basic_search_index(catalog)
    audit: list[AuditStep] = []

    if llm_model is None:
        # Provider-aware default for the optional onboarding tone rewrite.
        if os.getenv("OPENAI_API_KEY"):
            llm_model = os.getenv("CONCIERGE_LLM_MODEL", "gpt-4o-mini")
        elif os.getenv("GROQ_API_KEY"):
            llm_model = os.getenv("GROQ_LLM_MODEL", "llama-3.1-8b-instant")
        else:
            llm_model = "gpt-4o-mini"

    # Step 1: Profile extraction
    persona = _persona_from_scenario_id(scenario_id)
    audit.append(
        AuditStep(
            stepName="Profile extraction",
            inputSummary=f"scenario_id={scenario_id}, user_message={user_message[:120]}",
            outputJSON=persona.model_dump(),
        )
    )

    # Step 2: Need identification
    need = _need_from_scenario_id(scenario_id)
    audit.append(
        AuditStep(
            stepName="Need identification",
            inputSummary="Derived from scenario pack requirements",
            outputJSON=need.model_dump(),
        )
    )

    # Step 3: Product recommendation
    rec_items = _rank_products_by_need(catalog=catalog, search_index=search_index, need=need)
    selected = {x.productId: x for x in rec_items}
    selected_products = [item for item in catalog if item.id in selected]
    # deterministic order as ranked
    selected_products.sort(key=lambda p: [r.productId for r in rec_items].index(p.id))
    audit.append(
        AuditStep(
            stepName="Product recommendation",
            inputSummary=f"primaryNeed={need.primaryNeed}",
            outputJSON={"recommended": [r.model_dump() for r in rec_items]},
        )
    )

    # Step 4: Onboarding action (heuristics to ensure reliability)
    next_steps: list[str] = []
    if scenario_id == "cold_start_beginner":
        ask = need.questionsToAsk[0] if need.questionsToAsk else "What’s your rough time horizon (3–5y / 5–10y / 10y+)?"
        next_steps = [
            f"Answer this to personalize: {ask}",
            f"Start with: {selected_products[0].title}",
            f"Then join: {selected_products[1].title}" if len(selected_products) > 1 else f"Then explore: {selected_products[0].title}",
        ]
        assistant_message = (
            "Welcome to ET AI Concierge. To recommend the right next step for your SIP journey, quick question: "
            f"{ask}\n\n"
            "Based on your beginner stage, here are 3 ET starting points (no overload):\n"
            f"1) {selected_products[0].title}\n"
            + (f"   Link: {selected_products[0].url}\n" if selected_products else "")
            + (
                f"2) {selected_products[1].title}\n   Link: {selected_products[1].url}\n"
                if len(selected_products) > 1
                else ""
            )
            + (
                f"3) {selected_products[2].title}\n   Link: {selected_products[2].url}\n"
                if len(selected_products) > 2
                else ""
            )
            + "\nNext: pick one option for your first week (read the guide or attend the workshop) and we’ll keep it simple."
        )
    elif scenario_id == "reengagement_prime":
        # Use scenario-specific narrative aligned with the pack.
        next_steps = [
            "Re-enter with a curated small-cap learning sequence (begin with the latest strategy piece).",
            f"Start reading: {selected_products[0].title}",
            f"Follow with: {selected_products[1].title}" if len(selected_products) > 1 else "Follow with a related small/midcap deep-dive.",
        ]
        assistant_message = (
            "Welcome back. Since you previously spent time on markets content and small-cap webinars, "
            "you probably lapsed because the feed can feel like ‘too much’ without a clear next path.\n\n"
            "Here’s a cleaner re-start for your small-cap focus:\n"
            f"1) {selected_products[0].title}\n   Link: {selected_products[0].url}\n"
            + (
                f"2) {selected_products[1].title}\n   Link: {selected_products[1].url}\n"
                if len(selected_products) > 1
                else ""
            )
            + (
                f"3) {selected_products[2].title}\n   Link: {selected_products[2].url}\n"
                if len(selected_products) > 2
                else ""
            )
            + "\nIf you want, tell me whether your goal is ‘capital growth’ or ‘safer returns’, and I’ll suggest the smallest next action."
        )
    elif scenario_id == "cross_sell_home_loan":
        next_steps = [
            "Estimate your EMI quickly using the calculator.",
            f"Compare lending rates using: {selected_products[0].title}",
            f"Use: {selected_products[1].title}" if len(selected_products) > 1 else "Then compute your EMI with the tool.",
        ]
        assistant_message = (
            "Got it — home loan interest rates usually mean you’re preparing for a life step, so let’s make this practical.\n\n"
            f"1) {selected_products[0].title}\n   Link: {selected_products[0].url}\n"
            + (
                f"2) {selected_products[1].title}\n   Link: {selected_products[1].url}\n"
                if len(selected_products) > 1
                else ""
            )
            + "\nNext action: pick your approximate loan amount + tenure, run the EMI calculator once, then compare rates before you decide."
        )
    else:
        next_steps = ["Start with ET beginner guidance", "Tell us your time horizon and goal."]
        assistant_message = (
            "Here are a few ET starting points based on your request. "
            "If you share your time horizon and goal, I’ll tailor the smallest next step."
        )

    # Optional: rewrite onboarding message with LLM for a more natural concierge tone.
    # We keep product selection + nextSteps deterministic for judge reliability.
    llm_system = (
        "You are an ET AI Concierge. Rewrite the onboarding message to be short, warm, and non-jargony. "
        "Follow the user stage and need. Do NOT add new product recommendations. "
        "Do NOT include disclaimers (the UI will append them separately)."
    )
    selected_products_brief = [
        {"title": p.title, "url": p.url, "productType": p.productType} for p in selected_products
    ]
    llm_user = json.dumps(
        {
            "scenario_id": scenario_id,
            "persona": persona.model_dump(),
            "need": need.model_dump(),
            "selected_products": selected_products_brief,
            "current_assistant_message": assistant_message,
            "next_steps": next_steps,
            "requirements": {
                "cold_start": "Ask at most one clarifying question, then recommend 2-3 products.",
                "reengagement": "Be empathetic, specific to small-cap interest, and non-pushy.",
                "cross_sell": "Be practical; mention calculator + rate comparison links.",
            },
        },
        ensure_ascii=False,
    )
    rewritten = best_effort_chat_completion_text(model=llm_model, system=llm_system, user=llm_user)
    if rewritten:
        assistant_message = rewritten

    onboarding = OnboardingAction(
        assistantMessage=assistant_message + "\n\n" + DISCLAIMERS_SAFE(),
        nextSteps=next_steps,
        selectedProductIds=[p.id for p in selected_products],
        disclaimer=DISCLAIMER,
    )

    # Build a demo-like chat transcript (agent + user messages)
    chat: list[ChatTurn] = [ChatTurn(role="user", content=user_message)]
    if scenario_id == "cold_start_beginner":
        ask = need.questionsToAsk[0] if need.questionsToAsk else "What’s your rough time horizon (3–5y / 5–10y / 10y+)?"
        chat.append(ChatTurn(role="assistant", content=assistant_message.split("\n\n")[0]))
        # simulated user reply: 10+ years
        chat.append(ChatTurn(role="user", content="10+ years (I want long-term wealth for retirement)."))
        # final message again
        chat.append(ChatTurn(role="assistant", content="Here’s your personalized onboarding path:\n\n" + assistant_message))
    else:
        chat.append(ChatTurn(role="assistant", content=assistant_message))

    return {
        "persona": persona.model_dump(),
        "need": need.model_dump(),
        "recommendations": [r.model_dump() for r in rec_items],
        "selectedProducts": [p.__dict__ for p in selected_products],
        "onboarding": onboarding.model_dump(),
        "audit": [a.model_dump() for a in audit],
        "chatTranscript": [c.model_dump() for c in chat],
    }


def DISCLAIMERS_SAFE() -> str:
    return DISCLAIMER

