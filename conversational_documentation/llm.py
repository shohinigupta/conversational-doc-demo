import os
import pandas as pd
import streamlit as st
from anthropic import Anthropic
from utils import build_structured_followup_prompt

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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

def get_structured_prompt(visit_text, patient):
    """
    Get structured prompt for the LLM based on visit text and patient phase.
    
    Parameters:
    - visit_text (str): Free-text note from the care team.
    - patient (dict): Dictionary containing patient information.
    
    Returns:
    - messages (list): List of messages for use with Anthropic chat API.
    """
    # Load structured fields with error handling
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "structured_fields.csv")
        structured_fields_df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error(f"Could not find structured_fields.csv at {csv_path}")
        return None
    except Exception as e:
        st.error(f"Error loading structured_fields.csv: {str(e)}")
        return None
    
    # Debug: Show the loaded structured fields
    # st.write("Debug - Loaded Structured Fields:")
    # st.write(structured_fields_df)
    
    # Debug: Show what we're sending to the LLM
    # st.write("Debug - LLM Input:")
    # st.write(f"Visit Text: {visit_text}")
    # st.write(f"Patient Info: {patient}")
    
    # Build the prompt
    messages = build_structured_followup_prompt(visit_text, structured_fields_df, patient)
    
    # Debug: Show the full prompt
    # st.write("Debug - Full LLM Prompt:")
    # st.write("System Message:")
    # st.write(messages[0]["content"])
    # st.write("User Message:")
    # st.write(messages[1]["content"])
    
    return messages

def get_llm_response(messages):
    """
    Get response from the LLM.
    
    Parameters:
    - messages (list): List of messages for use with Anthropic chat API.
    
    Returns:
    - str: LLM response.
    """
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error calling LLM: {str(e)}")
        return None