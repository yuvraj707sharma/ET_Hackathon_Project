# ET AI Concierge (Track 7) — Architecture

## Goal

Deliver a truly agentic prototype for **Track 7: AI Concierge for ET** that:
1. Runs a **multi-step autonomous journey** — not a thin UI over an LLM.
2. Completes the full concierge pipeline: **profile → need → product → onboarding**.
3. Surfaces a **per-agent audit trail** so judges can verify every decision.
4. **Gracefully degrades** — works without any API key (deterministic mode).

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐       │
│  │ Scenario │  │  Chat    │  │  Audit   │  │ Analytics │       │
│  │ Selector │  │ Interface│  │  Trail   │  │ Dashboard │       │
│  └────┬─────┘  └────┬─────┘  └──────────┘  └───────────┘       │
│       │              │                                           │
│       ▼              ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Orchestrator (run_concierge_journey)         │   │
│  │                                                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │ Profile  │→ │  Need    │→ │ Product  │→ │Onboarding│ │   │
│  │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │ │   │
│  │  │ LLM/Rule │  │ LLM/Rule │  │ Tags+LLM │  │ LLM/Rule │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │   │
│  │                                                           │   │
│  │  Each agent: attempt LLM → fallback to deterministic      │   │
│  │  Each agent: records timing, reasoning, errors            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │                    Data Layer                            │    │
│  │  product_catalog.json (8 real ET URLs)                   │    │
│  │  scenarios.py (3 hackathon scenario packs)               │    │
│  │  llm.py (Groq/OpenAI via OpenAI SDK)                    │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Pipeline (4 autonomous steps)

### Agent A: Profile Extraction (`run_profile_agent`)
- **Input**: user message + scenario signals (age, history, intent)
- **LLM mode**: sends message + signals → extracts stageLabel, goals, riskComfort via structured JSON
- **Fallback**: deterministic persona lookup by scenario ID
- **Output**: `PersonaProfile` (persona bucket, stage, goals, risk comfort)

### Agent B: Need Identification (`run_need_agent`)
- **Input**: user message + extracted persona
- **LLM mode**: analyzes message in persona context → identifies primaryNeed, secondaryNeeds, tone
- **Fallback**: deterministic need mapping by scenario ID
- **Output**: `NeedIdentification` (primary need, secondary needs, tone guidance, clarifying questions)

### Agent C: Product Recommendation (`run_product_agent`)
- **Input**: need + ET product catalog
- **Method**: deterministic tag-based scoring (reliable for judging) + optional LLM-enhanced reasons
- **Output**: ranked top 2-3 `ProductRecommendationItem` with match scores and reasons

### Agent D: Onboarding Action (`run_onboarding_agent`)
- **Input**: persona, need, selected products
- **LLM mode**: rewrites deterministic onboarding message with warmer, personalized tone
- **Fallback**: scenario-specific structured message with product links + next steps
- **Output**: `OnboardingAction` (assistant message, next steps, product IDs, disclaimer)

## Error Handling & Graceful Degradation

- Each agent wrapped in try/except — LLM failures fall back to deterministic rules
- `AgentResult` model tracks: `success`, `error`, `durationMs`, `llmUsed`
- No API key? App works fully in deterministic mode (sub-1ms per scenario)
- Audit trail records errors so judges see recovery behavior

## Auditability

The UI shows a **judge-friendly audit trail** with:
- Per-agent expandable sections showing input/output JSON
- Timing per step (milliseconds)
- LLM vs Deterministic label per agent
- Pipeline stats (total steps, LLM steps used, total latency)

## Tool Integrations

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Groq (Llama 3.1 8B) via OpenAI SDK | Profile extraction, need analysis, tone rewriting |
| Catalog | `product_catalog.json` | 8 real ET URLs (articles, masterclass, tools) |
| UI | Streamlit | Demo runner, chat interface, analytics dashboard |
| Deployment | Docker | Containerized deployment |

## Compliance / Guardrails

- Every onboarding message includes SEBI/RBI compliance disclaimer
- Agent never provides licensed financial advice — only general guidance
- No competitor platforms mentioned in responses
- Non-pushy tone enforced via LLM system prompts and deterministic templates