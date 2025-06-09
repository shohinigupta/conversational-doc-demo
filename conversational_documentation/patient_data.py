"""
Patient data for the documentation assistant.
Includes patient information and phase display mappings.
"""

# Phase display mapping
PHASE_DISPLAY = {
    "newly_engaged": "Newly Engaged",
    "ongoing": "Ongoing Care",
    "at_risk": "At Risk"
}

# Patient data
PATIENTS = [
    {
        "name": "Tony J.",
        "engagement_phase": "newly_engaged",
        "primary_diagnosis": "Schizoaffective disorder",
        "flags": ["recent_hospitalization"]
    },
    {
        "name": "Maria L.",
        "engagement_phase": "ongoing",
        "primary_diagnosis": "Major depressive disorder",
        "flags": []
    },
    {
        "name": "James K.",
        "engagement_phase": "ongoing",
        "primary_diagnosis": "Bipolar disorder",
        "flags": ["recent_hospitalization"]
    },
    {
        "name": "Sarah M.",
        "engagement_phase": "ongoing",
        "primary_diagnosis": "Generalized anxiety disorder",
        "flags": []
    },
    {
        "name": "David R.",
        "engagement_phase": "newly_engaged",
        "primary_diagnosis": "Post-traumatic stress disorder",
        "flags": []
    }
] 