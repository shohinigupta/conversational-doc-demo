import streamlit as st
import pandas as pd
import os
from llm import ask_llm, get_structured_prompt
from example_notes import example_notes
from patient_data import PATIENTS, PHASE_DISPLAY

# Load structured rules with error handling
try:
    csv_path = os.path.join(os.path.dirname(__file__), "structured_fields.csv")
    rules_df = pd.read_csv(csv_path)
except FileNotFoundError:
    st.error(f"Could not find structured_fields.csv at {csv_path}")
    st.stop()
except Exception as e:
    st.error(f"Error loading structured_fields.csv: {str(e)}")
    st.stop()

st.set_page_config(page_title="Conversational Documentation Demo", layout="centered")

# Create tab layout
tab1, tab2 = st.tabs(["📄 Visit Note Assistant", "📋 Structured Rules"])

# === Tab 1: Main documentation flow ===
with tab1:
    st.title("📝 Visit Note Assistant")

    # Create patient selection dropdown
    patient_options = [f"{p['name']} ({PHASE_DISPLAY[p['engagement_phase']]})" for p in PATIENTS]
    selected_patient_name = st.selectbox(
        "Select Patient",
        options=patient_options,
        format_func=lambda x: x
    )

    # Get selected patient data
    selected_patient = next(p for p in PATIENTS if f"{p['name']} ({PHASE_DISPLAY[p['engagement_phase']]})" == selected_patient_name)

    # Display selected patient metadata
    st.markdown("---")
    st.markdown("**Selected Patient Information:**")
    st.markdown(f"""
    - **Name:** {selected_patient['name']}
    - **Phase:** {PHASE_DISPLAY[selected_patient['engagement_phase']]}
    - **Primary Diagnosis:** {selected_patient['primary_diagnosis']}
    - **Recent Hospitalization:** {'Yes' if 'recent_hospitalization' in selected_patient['flags'] else 'No'}
    """)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "final_note" not in st.session_state:
        st.session_state.final_note = ""
    if "rounds" not in st.session_state:
        st.session_state.rounds = 0
    if "current_note" not in st.session_state:
        st.session_state.current_note = ""

    MAX_ROUNDS = 1

    # Filter sample notes for the selected patient
    patient_name = selected_patient['name']
    relevant_notes = {
        k: v for k, v in example_notes.items() 
        if k.startswith(patient_name)
    }

    # Add sample note selector outside the form
    selected_sample = st.selectbox(
        "Try a sample note:",
        ["Select a sample..."] + list(relevant_notes.keys())
    )

    # Update current note when a sample is selected
    if selected_sample != "Select a sample...":
        st.session_state.current_note = relevant_notes[selected_sample]

    with st.form("visit_form"):
        user_input = st.text_area(
            "Enter visit summary (free-text):",
            value=st.session_state.current_note,
            height=200
        )
        
        # Update the current note in session state when user types
        if user_input != st.session_state.current_note:
            st.session_state.current_note = user_input
        
        submitted = st.form_submit_button("Submit")

    if submitted and user_input:
        st.session_state.messages = []
        st.session_state.final_note = user_input
        st.session_state.rounds = 0

        with st.spinner("helpinghand coach is analyzing your note..."):
            prompt = get_structured_prompt(user_input, selected_patient)
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
                st.session_state.messages.append(("helpinghand coach", "Thank you for the additional information. Let me review the complete note."))

    # Final note display
    if st.session_state.rounds >= MAX_ROUNDS or (
        st.session_state.messages and "sufficiently covered" in st.session_state.messages[-1][1].lower()
    ):
        st.markdown("---")
        st.subheader("✅ Final Combined Note")
        st.code(st.session_state.final_note, language="markdown")

# === Tab 2: Structured Rules Table ===
with tab2:
    st.header("📋 Structured Fields Reference")
    st.write("Below are all structured fields, grouped by what kind of patient criteria they apply to.")

    grouped = rules_df.groupby("criteria_type")

    for criteria_type, group in grouped:
        st.subheader(f"📌 {criteria_type.replace('_', ' ').title()}")
        for _, row in group.iterrows():
            st.markdown(f"- **{row['field_name']}** (if `{row['criteria_value']}`): {row['instructions']}") 