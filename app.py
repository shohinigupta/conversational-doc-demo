import streamlit as st
import pandas as pd
import ollama

example_files = {
    "Patient Panel": "data/patient_panel.csv",
    "Priority Rules": "data/priority_rules_updated.csv",
    "Training Data - Labeled Tasks": "data/curated_examples.csv",
    "Panel Action List to Prioritize": "data/unlabeled_tasks_2025-04-25.csv",
    "Event Triggered Tasks": "data/event_triggered_tasks.csv"
}

# --- Helper Functions ---
from main import build_prompt, apply_operator, rank_task, PRIORITY_LABELS

# --- App UI ---
# === Sidebar Navigation ===
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📝 Edit Priority Rules"])

# === Page: Home ===
if page == "🏠 Home":
    st.title("🧠 Patient Task Prioritization Demo")

    st.markdown("""
    ## 🧠 About This App
    This app demonstrates how tasks from a patient panel can be prioritized based on business logic and patient-specific information.  
   
    Users can upload their own patient panels with patient characteristics, tasks from the panel, and desired biz priority rules — or use default sample data.  
    
    After uploading, the app uses a local LLM to categorize each task (based on the training set) and then applies the prioritization rules to the full set of tasks.

    You can edit the prioritization rules to weight certain task categories or patient characteristics differently (ops strategies!), and immediately see how the panel action list changes.
  
    """)


    # === Upload CSVs ===
    uploaded_files = {}
    for label, default_path in example_files.items():
        uploaded_file = st.sidebar.file_uploader(f"{label} CSV", type=["csv"], key=label)
        if uploaded_file is not None:
            uploaded_files[label] = pd.read_csv(uploaded_file)
        else:
            uploaded_files[label] = pd.read_csv(default_path)
    #Load and tag the two task sources

    freeform_tasks = uploaded_files["Panel Action List to Prioritize"].copy()
    freeform_tasks["task_source"] = "patient_freeform"

    event_tasks = uploaded_files["Event Triggered Tasks"].copy()
    event_tasks["task_source"] = "event_triggered"

# Merge into one task list
    all_tasks = pd.concat([freeform_tasks, event_tasks], ignore_index=True)


    # === Show Uploaded Data (Preview only, not editable) ===
    st.header("📄 Uploaded Data Preview")

    for label, df in uploaded_files.items():
        if label != "Priority Rules":
            with st.expander(f"View {label} ({len(df)} rows)"):
                st.dataframe(df, use_container_width=True)

    # === Run Prioritization ===
    st.header("🚀 Run Prioritization")

    if "edited_priority_rules" in st.session_state:
        st.success("✅ Edited Priority Rules detected — will use them for prioritization!")

    if st.button("Run Categorization & Prioritization"):
        with st.spinner("Running..."):

            # Load datasets
            patient_panel_df = uploaded_files["Patient Panel"]
            example_sample = uploaded_files["Training Data - Labeled Tasks"]
            unlabeled_df = uploaded_files["Panel Action List to Prioritize"]

            # 🛠 Use edited rules if available
            priority_rules = st.session_state.get("edited_priority_rules", uploaded_files["Priority Rules"])

            results = []

            for idx, row in all_tasks.iterrows():
                patient_id = row["patient_id"]
                patient_name = row["patient_name"]
                task = row["TASK"]
                task_source = row["task_source"]

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
                    "Task Source": task_source,  # NEW field
                    "Predicted Category": predicted_category,
                    "Priority Rank": priority_rank,
                    "Priority Label": PRIORITY_LABELS[priority_rank],
                    "Priority Score": score,
                    "Patient Factors": "\n".join(f"• {reason}" for reason in point_reasons) if point_reasons else ""
                })


            # Build output DataFrame
            output_df = pd.DataFrame(results)
            output_df = output_df.sort_values(by=["Priority Rank", "Priority Score"], ascending=[True, False])

            # === Highlight Critical/High Priority Tasks ===
            def highlight_priority(row):
                if row["Priority Label"] == "Critical":
                    return ['background-color: #ffcccc'] * len(row)
                elif row["Priority Label"] == "High":
                    return ['background-color: #fff5cc'] * len(row)
                else:
                    return [''] * len(row)

            styled_df = output_df.style.apply(highlight_priority, axis=1)

            st.success("✅ Categorization and prioritization complete!")

            st.dataframe(styled_df, use_container_width=True)

            # === Download Button for Output ===
            csv = output_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Prioritized Tasks",
                data=csv,
                file_name="categorized_tasks_with_ranking.csv",
                mime="text/csv",
            )

# === Page: Edit Priority Rules ===
elif page == "📝 Edit Priority Rules":
    st.title("📝 Priority Rules Editor")

    st.header("📚 Priority Rules Reference Guide")

    # --- Hardcoded Task Categories ---
    st.subheader("Possible Task Categories")
    st.markdown("""
    - Individual Agency
    - Social Stability
    - Clinical Stability
    - External Clinicians
    - Medication Adherence
    """)

    # --- Dynamically pulled Patient Fields from Patient Panel ---
    patient_panel_example = pd.read_csv(example_files["Patient Panel"])
    patient_fields = patient_panel_example.columns.tolist()

    st.subheader("Example Patient Field Values")
    for field in patient_fields:
        # Skip weird fields like patient_id or patient_name if you want
        if field not in ["patient_id", "patient_name"]:
            unique_values = patient_panel_example[field].dropna().unique()
            sample_values = unique_values[:5]  # Just show 5 examples to avoid overload

            with st.expander(f"Field: {field} ({len(unique_values)} unique values)"):
                for val in sample_values:
                    st.markdown(f"- `{val}`")


    # --- Hardcoded Operators ---
    st.subheader("Supported Operators")
    st.markdown("""
    - `==` (equal to)
    - `!=` (not equal to)
    - `<` (less than)
    - `>` (greater than)
    - `<=` (less than or equal)
    - `>=` (greater than or equal)
    - `in` (for list membership)
    """)


    uploaded_priority_rules = st.file_uploader("Upload Priority Rules CSV", type=["csv"], key="priority_rules_upload")

    if uploaded_priority_rules is not None:
        priority_rules_df = pd.read_csv(uploaded_priority_rules)
    else:
        priority_rules_df = pd.read_csv(example_files["Priority Rules"])

    st.info("✏️ You can edit the rules live below. Changes are kept only during this session.")

    # Editable Data Editor
    edited_priority_rules = st.data_editor(priority_rules_df, use_container_width=True, num_rows="dynamic")

    # 🛠 Save to session state for use in Home page
    st.session_state["edited_priority_rules"] = edited_priority_rules

    # (Optional) Download Button
    csv = edited_priority_rules.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Edited Priority Rules",
        data=csv,
        file_name="edited_priority_rules.csv",
        mime="text/csv",
    )
