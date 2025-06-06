import ollama
import pandas as pd
from utils import build_structured_followup_prompt

def ask_ollama(prompt_messages):
    response = ollama.chat(model="llama3.2", messages=prompt_messages)
    return response["message"]["content"]

def get_structured_prompt(visit_text, phase="all"):
    structured_fields_df = pd.read_csv("structured_fields.csv")
    return build_structured_followup_prompt(visit_text, structured_fields_df, phase=phase) 