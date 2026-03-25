# ET AI Concierge (Track 7) - Architecture

## Goal
Deliver a working prototype for **Track 7: AI Concierge for ET** that:
1. Runs a multi-step journey without “thin UI over an LLM”.
2. Completes the journey end-to-end: **profile extraction -> need identification -> product recommendation -> onboarding action**.
3. Surfaces an **audit trail** so judges can see how the agent transformed state.

## High-level system
This prototype is a single Streamlit app:
- `app.py`: UI + scenario runner + transcript rendering.
- `concierge/agents.py`: orchestration (multi-agent, multi-step pipeline).
- `concierge/catalog.py`: loads a real ET product catalog from `data/product_catalog.json`.
- `concierge/scenarios.py`: scenario pack inputs (cold start, re-engagement, cross-sell).

### Agentic pipeline (multi-step, stateful)
On “Run agent journey”:
1. **Profile extraction (Agent A)** (`_persona_from_scenario_id`)
   - Input: scenario pack signals + initial user message.
   - Output: `PersonaProfile` (persona bucket, stage label, goals, risk comfort).
2. **Need identification (Agent B)** (`_need_from_scenario_id`)
   - Input: scenario pack requirement.
   - Output: `NeedIdentification` (primary need, secondary needs, 0-1 clarifying question).
3. **Product recommendation (Agent C)** (`_rank_products_by_need`)
   - Input: need + catalog tag index.
   - Output: ranked top 2-3 items (deterministic scoring for judge reliability).
4. **Onboarding action (Agent D)** (scenario-specific narrative)
   - Input: persona, need, top recommendations.
   - Output: `OnboardingAction` with a short assistant message + explicit next steps.

## Auditability / Audit trail
The UI shows an “Audit trail (judge-friendly)” section by rendering:
- a list of `AuditStep` objects: each step has `stepName`, inputSummary, and `outputJSON`.

This makes the pipeline auditable even if you don’t use an LLM key.

## Tool integrations
### Real data used
- A seeded catalog of **real ET URLs** (SIP beginner guidance, ET Prime small-cap content, home loan rate + EMI calculator widget) is stored in:
  - `data/product_catalog.json`

### Optional LLM integration
The repo includes an OpenAI JSON helper (`concierge/llm.py`) intended for future upgrades.
Current scoring/demo logic is deterministic to ensure the prototype always works during hackathon judging.

## Error handling / graceful degradation
- If `OPENAI_API_KEY` is missing, the app still works using deterministic concierge logic.
- Recommendation logic is tag-driven; if the catalog is missing a tag, the UI can still render a fallback onboarding path (to be extended if needed).

## Compliance / guardrails
- The onboarding includes a clear disclaimer distinguishing **general guidance** from **licensed financial advice**.