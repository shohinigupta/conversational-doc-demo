import pandas as pd
import streamlit as st

def build_structured_followup_prompt(visit_text, structured_fields_df, patient):
    """
    Builds a prompt for the LLM based on visit text and patient-specific structured fields.
    
    Parameters:
    - visit_text (str): Free-text note from the care team.
    - structured_fields_df (pd.DataFrame): DataFrame of structured questions.
    - patient (dict): Dictionary containing patient information including engagement_phase, diagnosis, and flags.
    
    Returns:
    - messages (list): List of messages for use with Anthropic chat API.
    """
    phase = patient["engagement_phase"]
    diagnosis = patient["primary_diagnosis"]
    flags = patient["flags"]

    # Debug: Show what we're filtering on
    # st.write("Debug - Patient Criteria:")
    # st.write(f"- Phase: {phase}")
    # st.write(f"- Diagnosis: {diagnosis}")
    # st.write(f"- Active Flags: {flags}")

    # Debug: Show all unique values in the DataFrame
    # st.write("Debug - Unique values in structured_fields_df:")
    # st.write("Criteria types:", structured_fields_df["criteria_type"].unique())
    # st.write("Criteria values:", structured_fields_df["criteria_value"].unique())

    # Filter structured fields
    phase_fields = structured_fields_df[
        (structured_fields_df["criteria_type"] == "engagement_phase") & 
        ((structured_fields_df["criteria_value"].str.lower() == phase.lower()) | 
         (structured_fields_df["criteria_value"] == "all"))
    ]
    
    diagnosis_fields = structured_fields_df[
        (structured_fields_df["criteria_type"] == "primary_diagnosis") & 
        (structured_fields_df["criteria_value"].str.lower() == diagnosis.lower())
    ]
    
    flag_fields = structured_fields_df[
        (structured_fields_df["criteria_type"] == "flag") & 
        (structured_fields_df["criteria_value"].isin(flags))
    ]

    # Debug: Show what fields we found
    # st.write("Debug - Fields Found:")
    # st.write("Phase-specific fields:")
    # st.write(phase_fields[["field_name", "criteria_value", "instructions"]])
    # st.write("Diagnosis-specific fields:")
    # st.write(diagnosis_fields[["field_name", "criteria_value", "instructions"]])
    # st.write("Flag-specific fields:")
    # st.write(flag_fields[["field_name", "criteria_value", "instructions"]])

    # Combine all relevant fields
    relevant_fields = pd.concat([phase_fields, diagnosis_fields, flag_fields])

    # Debug: Show final combined fields
    # st.write("Debug - Final Combined Fields:")
    # st.write(relevant_fields[["field_name", "criteria_type", "criteria_value", "instructions"]])

    # Prepare a hidden context for the LLM: field names and instructions (not to be output)
    field_context = "\n".join([
        f"- {row['field_name']}: {row['instructions']}"
        for _, row in relevant_fields.iterrows()
    ])

    system_instruction = (
        "You are a documentation assistant helping a peer recovery specialist review their visit note. "
        "You have a list of required fields for this patient phase. "
        "For each field, only consider it answered if it is clearly and directly addressed in the note. "
        "Do not infer, assume, or guess. "
        "Do not introduce any fields or topics that are not in the provided list. "
        "For each missing field, provide feedback in a warm, encouraging, and collegial tone: "
        "1) Briefly explain in plain language what is missing, and "
        "2) Ask a single, specific follow-up question that would help complete that field. "
        "If all required fields are clearly addressed, say: 'All fields are sufficiently covered.' "
        "Never list or mention the field names or instructions in your output."
    )

    user_prompt = (
        f"Here is the visit summary to review:\n\"\"\"\n{visit_text}\n\"\"\"\n\n"
        f"Required fields for this phase (for your reference, do not output):\n{field_context}\n\n"
        f"Please check only the required fields for this phase. "
        f"For each missing field, give a brief, plain-language explanation and a single, specific follow-up question. "
        f"Keep your feedback warm and supportive, like a helpful colleague. "
        f"If everything is covered, just say: 'All fields are sufficiently covered.'"
    )

    return [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ]