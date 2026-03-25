# ET AI Concierge (Track 7 Demo)

hackathon prototype for **Track 7: AI Concierge for ET**.

## What it does
- Runs an **autonomous multi-step journey**: profile extraction → need identification → product recommendation → onboarding action.
- Shows an **audit trail** in the UI (judge-friendly).
- Uses a **real ET product catalog** seeded in `data/product_catalog.json`.
- Implements the **Track 7 scenario pack demos**:
  - Cold-start onboarding
  - Re-engagement (lapsed ET Prime)
  - Multi-product cross-sell (home loan)

## Run locally
1. Create a virtual environment
2. Install deps:
   - `pip install -r requirements.txt`
3. Start the app:
   - `streamlit run app.py`

## Configuration (optional)
- Set `OPENAI_API_KEY` if you want to extend the prototype to LLM-based text generation.

## Deployment (quick)
This is a single Streamlit app; easiest options:
- Render: use a Python/requirements start command or Docker (recommended for reliability)
- Fly.io / Railway: Docker-based deploy using the included `Dockerfile`

## Compliance / guardrail
The UI includes a clear disclaimer: this is **not licensed financial advice**.