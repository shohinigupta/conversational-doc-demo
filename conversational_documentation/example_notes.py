"""
Sample visit notes for testing the documentation assistant.
Each note is paired with a comment indicating which structured fields are missing.
"""

example_notes = {
    "Tony J. — First visit after recent hospitalization":
        "Tony and I met for the first time since his hospitalization. He seemed tired but open, and we talked about how he's been trying to get back into a routine. He said mornings are hardest but he's making it through. I shared a bit about what helped me after I came home from the hospital and he appreciated that.",
        # ❌ Missing: housing_status, social_support

    "Maria L. — Low mood but stable on medication":
        "Maria said her energy has been low lately and she’s been struggling to stay motivated. She said she’s still taking her meds but sometimes forgets her morning dose. We spent time talking about her old journaling habit and how that used to help her reflect. She seemed open to trying that again.",
        # ❌ Missing: wellness_goals, lived_experience

    "James K. — Recent discharge and safety planning":
        "James said he’s been out of the hospital for two weeks and has mostly stayed inside. He said he’s been sleeping better but still gets overwhelmed easily. He agreed to check in again next week. I reminded him about calling the crisis line if things get too heavy, and he said he has the number saved.",
        # ❌ Missing: reason_for_visit, crisis_plan

    "Sarah M. — Managing anxiety with structure":
        "Sarah shared that she’s been keeping a strict morning routine to manage her anxiety and that it helps her stay focused during the day. We talked about how she used to cook meals for herself and how she might get back into that. She said she’d make a list of a few simple things to cook this week.",
        # ❌ Missing: medication_changes, lived_experience

    "David R. — Trust-building conversation":
        "David opened up a bit more this visit. He said he doesn’t feel like anyone really listens to him, but said it felt different today. I told him about a time I had to rebuild trust after a bad experience and he said he could relate. He didn’t go into specifics about his living situation but said he’s figuring it out.",
        # ❌ Missing: housing_status, reason_for_visit
}