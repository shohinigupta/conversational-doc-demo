import pandas as pd

def build_structured_followup_prompt(visit_text, structured_fields_df, phase="all"):
    """
    Builds a prompt for the LLM based on visit text and phase-specific structured fields.
    
    Parameters:
    - visit_text (str): Free-text note from the care team.
    - structured_fields_df (pd.DataFrame): DataFrame of structured questions.
    - phase (str): The patient's current engagement phase (e.g., 'newly_engaged', 'ongoing').
    
    Returns:
    - messages (list): List of messages for use with Ollama chat API.
    """
    if "phase_list" not in structured_fields_df.columns:
        structured_fields_df["phase_list"] = structured_fields_df["phase"].str.split("|")

    relevant_fields = structured_fields_df[
        structured_fields_df["phase_list"].apply(lambda x: phase in x or "all" in x)
    ]

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