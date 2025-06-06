import pandas as pd
import os
from utils import build_structured_followup_prompt
import anthropic  # Replace this if you're still using ollama

import streamlit as st

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def ask_llm(prompt_messages):
    # Extract the system prompt (first message)
    system_prompt = None
    if prompt_messages and prompt_messages[0]["role"] == "system":
        system_prompt = prompt_messages[0]["content"]
        prompt_messages = prompt_messages[1:]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        temperature=0.7,
        system=system_prompt,  # Passed here instead of in messages
        messages=prompt_messages,
    )

    return response.content[0].text

def get_structured_prompt(visit_text, phase="all"):
    csv_path = os.path.join(os.path.dirname(__file__), "structured_fields.csv")
    structured_fields_df = pd.read_csv(csv_path)
    return build_structured_followup_prompt(visit_text, structured_fields_df, phase=phase)