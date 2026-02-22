"""
Populate Seraphe's reference profile with numerology data.
Run this whenever the profile needs refreshing.

Usage:
    python3 populate_seraphe_profile.py
"""

import json
from datetime import date
from numerology import build_profile, analyze_date, analyze_name

PROFILE_PATH = "seraphe_reference_profile.json"


def populate():
    # Load existing profile
    with open(PROFILE_PATH, "r") as f:
        profile_data = json.load(f)

    # Birth date
    birth_date = date(1988, 10, 18)

    # Build full numerology profile for birth name
    birth_name_profile = build_profile(
        name="Rebecca Lydia Denkers",
        birth_date=birth_date,
    )

    # Also build for spiritual name
    spiritual_name_profile = build_profile(
        name="Seraphe Valemira",
        birth_date=birth_date,
    )

    # Populate numerology section
    profile_data["numerology"]["birth_date_profile"] = birth_name_profile.birth_date_profile.to_dict()
    profile_data["numerology"]["name_profile_birth"] = birth_name_profile.name_profile.to_dict()
    profile_data["numerology"]["name_profile_spiritual"] = spiritual_name_profile.name_profile.to_dict()

    # Add significant dates if known
    # (expand this list as more dates become significant)
    significant_dates = {
        # "wedding_date": date(YYYY, MM, DD),
        # "fitz_birth": date(YYYY, MM, DD),
    }
    profile_data["numerology"]["significant_dates"] = []
    for label, d in significant_dates.items():
        dp = analyze_date(d, label_prefix=label)
        profile_data["numerology"]["significant_dates"].append(dp.to_dict())

    # Update metadata
    from datetime import datetime
    profile_data["meta"]["last_updated"] = datetime.now().isoformat()

    # Write back
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile_data, f, indent=2, default=str)

    print(f"✓ Profile updated: {PROFILE_PATH}")
    print(f"  Birth name expression: {birth_name_profile.name_profile.expression_stack.root} "
          f"({'master ' + str(birth_name_profile.name_profile.expression_stack.steps[1].value) if any(s.is_master for s in birth_name_profile.name_profile.expression_stack.steps) else ''})")
    print(f"  Spiritual name expression: {spiritual_name_profile.name_profile.expression_stack.root}")
    print(f"  Life path: {birth_name_profile.birth_date_profile.life_path_stack.root}")
    print(f"  Full tarot signature (birth name): {', '.join(birth_name_profile.full_tarot_signature())}")
    print(f"  Full tarot signature (spiritual): {', '.join(spiritual_name_profile.full_tarot_signature())}")


if __name__ == "__main__":
    populate()
