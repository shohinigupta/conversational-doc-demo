import pandas as pd
import ollama
from utils import build_structured_followup_prompt

# === Load structured fields ===
structured_fields_df = pd.read_csv("structured_fields.csv")
phase = "newly_engaged"
print(f"📋 Current phase: {phase}\n")

# === Start session ===
while True:
    visit_summary = input("\n📝 Enter visit summary (or 'q' to quit):\n")
    if visit_summary.lower() == "q":
        break

    full_note = visit_summary
    rounds = 0
    max_rounds = 2

    while rounds < max_rounds:
        print("🤖 Checking response...\n")
        messages = build_structured_followup_prompt(full_note, structured_fields_df, phase=phase)
        response = ollama.chat(model="llama3.2", messages=messages)
        followup = response['message']['content']

        print("\n🤖 LLM Follow-Up:\n")
        print(followup)

        if "all fields are sufficiently covered" in followup.lower():
            break

        followup_response = input("\n✏️ Your response:\n")
        full_note += "\n" + followup_response
        rounds += 1

    print("\n✅ Final documentation note:\n")
    print(full_note)