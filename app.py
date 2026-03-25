from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from concierge.agents import run_concierge_journey
from concierge.catalog import load_product_catalog
from concierge.scenarios import SCENARIOS


st.set_page_config(page_title="ET AI Concierge (Track 7)", layout="wide")

st.title("ET AI Concierge (Track 7 Demo)")
st.caption("Solo-friendly prototype: multi-step agentic journey + audit trail, seeded with real ET product URLs.")

catalog_path = Path(__file__).parent / "data" / "product_catalog.json"
catalog = load_product_catalog(catalog_path)

openai_key = os.getenv("OPENAI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
if not openai_key and not groq_key:
    st.sidebar.info("No LLM API key set (`OPENAI_API_KEY` or `GROQ_API_KEY`). Demo will still work using deterministic concierge logic.")
elif groq_key:
    st.sidebar.success("✅ Groq API key detected. LLM-enhanced responses enabled.")
elif openai_key:
    st.sidebar.success("✅ OpenAI API key detected. LLM-enhanced responses enabled.")

with st.sidebar:
    st.header("Scenario Pack Runner")
    scenario_key = st.selectbox(
        "Choose a required scenario",
        options=list(SCENARIOS.keys()),
        format_func=lambda k: SCENARIOS[k].title,
    )
    run_btn = st.button("Run agent journey", type="primary")
    run_all_btn = st.button("Run all required scenarios")

scenario = SCENARIOS[scenario_key]

def _run_one(s_key: str):
    s = SCENARIOS[s_key]
    return run_concierge_journey(
        scenario_id=s.scenarioId,
        user_message=s.initialUserMessage,
        catalog=catalog,
    )


if run_all_btn:
    st.subheader("All required scenarios (for judge convenience)")
    for s_key in SCENARIOS.keys():
        s = SCENARIOS[s_key]
        result = _run_one(s_key)
        with st.expander(f"{s.title}", expanded=False):
            st.markdown("**Onboarding action**")
            st.write(result["onboarding"]["assistantMessage"])
            st.markdown("**Recommendations**")
            for p in result["selectedProducts"]:
                st.markdown(f"- {p['title']} ({p['url']})")
            st.markdown("**Audit trail**")
            st.json(result["audit"])

elif run_btn:
    result = _run_one(scenario_key)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("Agent journey (demo transcript)")
        chat = result["chatTranscript"]
        for turn in chat:
            role = turn["role"].title()
            content = turn["content"]
            if turn["role"] == "user":
                st.markdown(f"**{role}:** {content}")
            else:
                st.markdown(f"**{role}:**\n\n{content}")

        st.subheader("Onboarding action")
        st.write(result["onboarding"]["assistantMessage"])

        if result["onboarding"]["nextSteps"]:
            st.markdown("**Next steps for the user:**")
            for step in result["onboarding"]["nextSteps"]:
                st.markdown(f"- {step}")

    with col2:
        st.subheader("Product recommendations (real ET URLs)")
        selected_products = result["selectedProducts"]
        # preserve order from selectedProducts
        for p in selected_products:
            st.markdown(f"### {p['title']}")
            if p.get("lastUpdatedISO"):
                st.caption(f"Last updated: {p['lastUpdatedISO']}")
            st.write(p["url"])
            st.write("---")

        st.subheader("Audit trail (judge-friendly)")
        st.json(result["audit"])

        st.caption("Audit trail shows how each agent stage transforms state. Computation is deterministic; text is concierge-guided.")

else:
    st.info("Pick a scenario from the sidebar, then click `Run agent journey`.")

