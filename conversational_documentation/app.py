import streamlit as st
from llm import ask_llm, get_structured_prompt

st.set_page_config(page_title="Conversational Documentation Demo", layout="centered")

st.title("📝 Visit Note Assistant")

# Add phase selection
phase = st.selectbox(
    "Select patient phase:",
    ["all", "newly_engaged", "ongoing", "at_risk"],
    index=0
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "final_note" not in st.session_state:
    st.session_state.final_note = ""
if "rounds" not in st.session_state:
    st.session_state.rounds = 0

MAX_ROUNDS = 1

with st.form("visit_form"):
    user_input = st.text_area("Enter visit summary (free-text):", height=200)
    submitted = st.form_submit_button("Submit")

if submitted and user_input:
    st.session_state.messages = []
    st.session_state.final_note = user_input
    st.session_state.rounds = 0

    with st.spinner("helpinghand coach is analyzing your note..."):
        prompt = get_structured_prompt(user_input, phase=phase)
        llm_response = ask_llm(prompt)

    st.session_state.messages.append(("helpinghand coach", llm_response))

# Show conversation history and take follow-up answers
if st.session_state.messages:
    st.markdown("---")
    st.subheader("Follow-up Questions")

    for i, (role, content) in enumerate(st.session_state.messages):
        st.markdown(f"**{role}:** {content}")

    if st.session_state.rounds < MAX_ROUNDS and "sufficiently covered" not in st.session_state.messages[-1][1].lower():
        followup_response = st.text_area("Your follow-up response:", key=f"round_{st.session_state.rounds}")
        if st.button("Submit follow-up response"):
            st.session_state.final_note += "\n" + followup_response
            st.session_state.rounds += 1

            with st.spinner("helpinghand coach is analyzing your follow-up response..."):
                prompt = get_structured_prompt(st.session_state.final_note, phase=phase)
                new_response = ask_llm(prompt)

            st.session_state.messages.append(("helpinghand coach", new_response))

# Final note display
if st.session_state.rounds >= MAX_ROUNDS or (
    st.session_state.messages and "sufficiently covered" in st.session_state.messages[-1][1].lower()
):
    st.markdown("---")
    st.subheader("✅ Final Combined Note")
    st.code(st.session_state.final_note, language="markdown") 