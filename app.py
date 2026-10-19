import time
import streamlit as st
from src.graph import ask

st.set_page_config(page_title="PolicyWise AI", page_icon="📚", layout="centered")
st.title("PolicyWise AI")
st.caption("Document-grounded GitLab handbook policy brief assistant | Source briefs are not authoritative policy text")
st.info("Policy applicability varies by employment country, entity, and role. Check the live handbook for official guidance.")
country = st.text_input("Employment country (optional)", placeholder="e.g. United States")
examples = ["What does GitLab's PTO policy cover?", "How should remote team members communicate?",
            "Am I eligible for paid leave?", "How many PTO days do I personally have remaining?"]
if 'history' not in st.session_state:
    st.session_state.history = []
if 'suggested' not in st.session_state:
    st.session_state.suggested = None
with st.expander("Try a sample question"):
    for i, example in enumerate(examples):
        if st.button(example, key=f"q{i}"):
            st.session_state.suggested = example
for item in st.session_state.history:
    with st.chat_message('user'):
        st.write(item['question'])
    with st.chat_message('assistant'):
        st.write(item['answer'])
        st.caption(f"Status: {item['status']} | {item['elapsed']:.2f} s")
        for c in item['citations']:
            with st.expander(f"{c['filename']} · p. {c['page']}"):
                st.caption(c['chunk_id'])
                st.write(c['excerpt'])
question = st.chat_input("Ask about a policy") or st.session_state.suggested
if question:
    st.session_state.suggested = None
    start = time.perf_counter()
    try:
        with st.spinner("Searching policy documents..."):
            result = ask(question, country)
        response = dict(question=question, answer=result.get('answer', ''),
                        status=result.get('status', 'unknown'), citations=result.get('citations', []),
                        elapsed=time.perf_counter()-start)
    except Exception as exc:
        # Avoid revealing API keys, internal stack traces, or user data in the UI.
        error_type = type(exc).__name__.lower()
        msg = "Model provider request failed. Please retry later." if ('rate' in error_type or 'limit' in error_type) else "Service temporarily unavailable. Check application logs."
        response = dict(question=question, answer=msg, status='error', citations=[], elapsed=time.perf_counter()-start)
    st.session_state.history.append(response)
    st.rerun()
