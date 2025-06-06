# Imports
import pandas as pd
import ollama

# === Constants ===
TRAINING_TASKS_PATH = "data/training_tasks.csv"  # (only used if needed)
CURATED_EXAMPLES_PATH = "data/curated_examples.csv"
UNLABELED_TASKS_PATH = "data/unlabeled_tasks_2025-04-25.csv"
OUTPUT_PATH = "categorized_tasks_with_ranking.csv"
PATIENT_PANEL_PATH = "data/patient_panel.csv"
PRIORITY_RULES_PATH = "data/priority_rules_updated.csv"
patient_panel_df = pd.read_csv(PATIENT_PANEL_PATH)
priority_rules = pd.read_csv(PRIORITY_RULES_PATH)

required_columns = ['rule_id', 'task_category', 'keyword', 'patient_field', 'patient_field_operator', 'patient_field_value', 'points']
for col in required_columns:
    assert col in priority_rules.columns, f"Missing expected column: {col}"



CRITICAL_KEYWORDS = ["safety plan", "relapse", "warning signs", "crisis"]
PRIORITY_LABELS = {
    1: "Critical",
    2: "High",
    3: "Medium",
    4: "Low",
    5: "Low"
}

# === Helper Functions ===
def build_prompt(examples, new_task):
    intro = (
        "You are a manager of social workers at a value-based-care company that treats patients with severe mental illnesses who use Medicaid or Medicare for insurance. You need to classify tasks for patient care into one of the following categories:\n"
        "- Individual Agency\n"
        "- Social Stability\n"
        "- Clinical Stability\n"
        "- External Clinicians\n"
        "- Medication Adherence\n\n"
        "Tasks involving clinical symptom tracking, safety planning, early warning signs of relapse, or psychiatric stabilization should be categorized under Clinical Stability. "
        "Tasks that involve legal, financial, housing, or insurance support should be categorized under Social Stability — even if they involve patient empowerment.\n"
        "Here are some example tasks and their categories:\n"
    )

    formatted_examples = "\n".join([
        f"- \"{row['Task']}\" → {row['risk_factor_stage']}"
        for _, row in examples.iterrows()
    ])

    task_to_label = f"\n\nNow categorize the following task:\n\"{new_task}\"\n\nRespond with only the category name."
    return intro + formatted_examples + task_to_label


def apply_operator(field_value, operator, rule_value):
    """Helper to apply flexible comparison operators."""
    if operator == "==":
        return field_value == rule_value
    elif operator == "!=":
        return field_value != rule_value
    elif operator == "<":
        return float(field_value) < float(rule_value)
    elif operator == ">":
        return float(field_value) > float(rule_value)
    elif operator == "<=":
        return float(field_value) <= float(rule_value)
    elif operator == ">=":
        return float(field_value) >= float(rule_value)
    elif operator == "in":
        return field_value in eval(rule_value)  # careful — rule_value must be a Python list string
    else:
        return False

def rank_task(task_text, predicted_category, patient_info, priority_rules_df):
    task_text_lower = task_text.lower()
    score = 0

    patient_id = patient_info["patient_id"]
    patient_name = patient_info["patient_name"]

    print(f"\n--- Scoring for Task: \"{task_text}\" (Category: {predicted_category}) ---")
    print(f"Patient: {patient_name} (ID: {patient_id})")

    point_reasons = []

    for _, rule in priority_rules_df.iterrows():
        match = False
        reasons_to_add = []  # Hold reasons temporarily, don't log immediately!

        # Task category match
        if isinstance(rule["task_category"], str) and predicted_category == rule["task_category"]:
            match = True
            reasons_to_add.append(f"Matched Task Category: {rule['task_category']}")

        # Keyword match
        if isinstance(rule["keyword"], str) and rule["keyword"].lower() in task_text_lower:
            match = True
            reasons_to_add.append(f"Matched Keyword: {rule['keyword']}")

        # Patient field match
        if isinstance(rule["patient_field"], str):
            patient_value = patient_info.get(rule["patient_field"], None)
            if patient_value is not None:
                if apply_operator(patient_value, rule["patient_field_operator"], rule["patient_field_value"]):
                    match = True
                    reasons_to_add.append(f"Matched Patient Field: {rule['patient_field']}={patient_value}")

        # 🚨 Now check condition (AFTER initial matching)
        if match and isinstance(rule.get("condition_field"), str):
            condition_value_patient = patient_info.get(rule["condition_field"], None)
            if condition_value_patient != rule["condition_value"]:
                match = False
                reasons_to_add = []  # 🚨 Clear any earlier reasons if condition fails

        # Only if truly matched, apply points and reasons
        if match:
            score += rule["points"]
            point_reasons.extend(reasons_to_add)  # Log reasons now
            point_reasons.append(f"+{rule['points']} points from Rule {rule['rule_id']}")


    # Print why points were added
    for reason in point_reasons:
        print(reason)

    print(f"Total Score for Task: {score}")

    # Map score to priority rank
    if score >= 10:
        priority_rank = 1
    elif score >= 7:
        priority_rank = 2
    elif score >= 4:
        priority_rank = 3
    else:
        priority_rank = 4

    return priority_rank, score, point_reasons



# === Main Script ===
def main():
    # Load data
    patient_panel_df = pd.read_csv(PATIENT_PANEL_PATH)
    priority_rules = pd.read_csv(PRIORITY_RULES_PATH)
    example_sample = pd.read_csv(CURATED_EXAMPLES_PATH)
    unlabeled_df = pd.read_csv(UNLABELED_TASKS_PATH)

    assert "TASK" in unlabeled_df.columns, "Expected 'TASK' column not found in the unlabeled tasks file."
    required_columns = ['rule_id', 'task_category', 'keyword', 'patient_field', 'patient_field_operator', 'patient_field_value', 'points']
    for col in required_columns:
        assert col in priority_rules.columns, f"Missing expected column: {col}"

    results = []

    for idx, row in unlabeled_df.iterrows():
        patient_id = row["patient_id"]
        patient_name = row["patient_name"]
        task = row["TASK"]

        patient_info = patient_panel_df[patient_panel_df["patient_id"] == patient_id].iloc[0]

        prompt = build_prompt(example_sample, task)
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        predicted_category = response["message"]["content"].strip()

        priority_rank, score, point_reasons = rank_task(task, predicted_category, patient_info, priority_rules)

        results.append({
            "Patient ID": patient_id,
            "Patient Name": patient_name,
            "Task": task,
            "Predicted Category": predicted_category,
            "Priority Rank": priority_rank,
            "Priority Label": PRIORITY_LABELS[priority_rank],
            "Priority Score": score,
            "Patient Factors": "\n".join(f"• {reason}" for reason in point_reasons) if point_reasons else ""
        })

    output_df = pd.DataFrame(results)
    output_df = output_df.sort_values(by=["Priority Rank", "Priority Score"], ascending=[True, False])

    output_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Categorization, ranking, and labeling complete. Saved to {OUTPUT_PATH}")
    print(output_df["Priority Label"].value_counts())

# === Only run main() if called directly ===
if __name__ == "__main__":
    main()