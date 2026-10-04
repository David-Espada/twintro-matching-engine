"""Validate and measure the actual demo dataset, then generate presentation cases."""

import json
from pathlib import Path

from app.api.dependencies import get_matcher
from app.schemas.profile import ProfessionalProfile
from demo_profiles import DEMO_CASES


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    profiles = [
        ProfessionalProfile.model_validate(p)
        for p in json.loads((root / "dataset/professional_profiles.json").read_text(encoding="utf-8"))
    ]
    assert len(profiles) == 100
    indexed = {p.user_id: p for p in profiles}
    assert len(indexed) == 100
    assert all(
        p.role and p.industry and p.skills and p.interests and p.experience_years is not None
        for p in profiles
    )
    matcher = get_matcher()
    matcher.prepare(profiles)
    results = []
    lines = [
        "# Recommended hackathon demo cases",
        "",
        "All 100 profiles pass schema validation, have unique IDs, and contain all five confidence fields. "
        "Twelve profiles (IDs 81–92) are hand-authored synthetic examples; the remaining 88 retain the seeded generator output. "
        "The generator preserves these cases at all supported dataset sizes.",
        "",
        "Use the following relationship expectations, not memorized percentages. Actual MiniLM observations "
        "are captured separately in `demo-audit.json`; they are not hardcoded into scoring. "
        "High means ≥80 for the deterministic insight. Good (70–79.9) is not classified as high.",
        "",
        "| Case | Profile A | Profile B | Expected relationship | Presentation value |",
        "| --- | --- | --- | --- | --- |",
    ]
    for title, aid, bid, expected, why in DEMO_CASES:
        a, b = indexed[aid], indexed[bid]
        result = matcher.compare(a, b)
        lines.append(
            f"| {title} | {a.name} — {a.role} (`{aid}`) | {b.name} — {b.role} (`{bid}`) | {expected} | {why} |"
        )
        results.append(
            {
                "case": title,
                "profile_a": aid,
                "profile_b": bid,
                "affinity": result.affinity_percentage,
                "complementarity": result.score_breakdown.complementarity,
                "match_level": result.match_level,
                "complementarity_level": result.complementarity_level,
                "insight": result.connection_insight,
            }
        )
    lines += [
        "",
        "## Presentation notes",
        "",
        "Enable `NEXT_PUBLIC_DEMO_MODE=true` to surface these profiles in a Recommended demo profiles "
        "selector group. The badge and ordering are presentation conveniences; every comparison still calls the backend.",
        "",
        "Start with AI meets product to show Affinity ≠ Complementarity. Next compare the near-identical pair, "
        "then the unrelated pair. The moderate case helps explain that the six dimensions can pull in different directions.",
        "",
        "Restaurant-specific skills and Hospitality are intentionally outside the initial taxonomy. "
        "The engine uses semantic evidence and does not infer useful complementarity just from unfamiliar terms.",
        "",
    ]
    (root / "docs/demo-cases.md").write_text("\n".join(lines), encoding="utf-8")
    (root / "docs/demo-audit.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
