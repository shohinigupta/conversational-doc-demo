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
        "phase": "newly_engaged",
        "primary_diagnosis": "Schizoaffective disorder",
        "recent_hospitalization": True
    },
    {
        "name": "Maria L.",
        "phase": "ongoing",
        "primary_diagnosis": "Major depressive disorder",
        "recent_hospitalization": False
    },
    {
        "name": "James K.",
        "phase": "at_risk",
        "primary_diagnosis": "Bipolar disorder",
        "recent_hospitalization": True
    },
    {
        "name": "Sarah M.",
        "phase": "ongoing",
        "primary_diagnosis": "Generalized anxiety disorder",
        "recent_hospitalization": False
    },
    {
        "name": "David R.",
        "phase": "newly_engaged",
        "primary_diagnosis": "Post-traumatic stress disorder",
        "recent_hospitalization": False
    }
] 