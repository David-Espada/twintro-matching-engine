"""Generate reproducible, role-coherent synthetic professionals (standard library only)."""

import argparse
import json
import random
from pathlib import Path

from demo_profiles import curated_profiles

ARCHETYPES = [
    ("Software Engineer", ["Python", "Java", "SQL", "Docker", "API design"], ["Technology", "Finance"]),
    (
        "Frontend Developer",
        ["React", "TypeScript", "JavaScript", "Next.js", "Design systems"],
        ["Technology", "Ecommerce"],
    ),
    (
        "Backend Developer",
        ["Python", "FastAPI", "PostgreSQL", "Docker", "API design"],
        ["Technology", "Financial technology"],
    ),
    (
        "AI Engineer",
        ["Python", "Machine Learning", "PyTorch", "FastAPI", "Natural language processing"],
        ["Technology", "Healthcare"],
    ),
    (
        "Machine Learning Engineer",
        ["Python", "TensorFlow", "Deep learning", "MLOps", "Docker"],
        ["Technology", "Biotechnology"],
    ),
    (
        "Data Scientist",
        ["Python", "Statistics", "Machine Learning", "SQL", "Pandas"],
        ["Healthcare", "Finance"],
    ),
    ("Data Engineer", ["Python", "SQL", "Spark", "dbt", "Data modeling"], ["Technology", "Retail"]),
    (
        "Product Manager",
        ["Product strategy", "Roadmapping", "User research", "Agile", "Analytics"],
        ["Technology", "Education technology"],
    ),
    (
        "UX Designer",
        ["Figma", "User experience", "Prototyping", "User research", "Design systems"],
        ["Technology", "Healthcare"],
    ),
    (
        "UI Designer",
        ["Figma", "User interface", "Visual design", "Prototyping", "Design systems"],
        ["Technology", "Ecommerce"],
    ),
    (
        "Marketing Manager",
        ["Content marketing", "SEO", "Campaign management", "Copywriting", "Analytics"],
        ["Retail", "Education"],
    ),
    (
        "Growth Manager",
        ["Growth strategy", "A/B testing", "Analytics", "SEO", "Campaign management"],
        ["Technology", "Ecommerce"],
    ),
    (
        "Sales Manager",
        ["Sales strategy", "CRM", "Negotiation", "Team management", "Partnerships"],
        ["Technology", "Manufacturing"],
    ),
    (
        "Business Development Manager",
        ["Business development", "Partnerships", "Negotiation", "CRM", "Strategic planning"],
        ["Finance", "Technology"],
    ),
    (
        "Founder",
        ["Leadership", "Fundraising", "Product strategy", "Strategic planning", "Team management"],
        ["Technology", "Financial technology"],
    ),
    (
        "CTO",
        ["Leadership", "Python", "API design", "Team management", "Amazon Web Services"],
        ["Technology", "Financial technology"],
    ),
    (
        "Cybersecurity Engineer",
        ["Threat modeling", "Penetration testing", "Security auditing", "Incident response", "Linux"],
        ["Finance", "Technology"],
    ),
    (
        "DevOps Engineer",
        ["Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"],
        ["Technology", "Healthcare"],
    ),
    (
        "Cloud Engineer",
        ["Amazon Web Services", "Azure", "Terraform", "Docker", "Linux"],
        ["Technology", "Finance"],
    ),
    (
        "Business Analyst",
        ["SQL", "Data analysis", "Analytics", "Agile", "Roadmapping"],
        ["Finance", "Logistics"],
    ),
    (
        "Investment Analyst",
        ["Financial modeling", "Valuation", "Investment analysis", "Risk management", "Accounting"],
        ["Finance", "Financial technology"],
    ),
    (
        "Operations Manager",
        ["Operations management", "Team management", "Strategic planning", "Risk management"],
        ["Logistics", "Manufacturing"],
    ),
]
FIRST = [
    "Alex",
    "Morgan",
    "Jordan",
    "Taylor",
    "Sam",
    "Avery",
    "Riley",
    "Cameron",
    "Sofia",
    "Mateo",
    "Priya",
    "Noah",
    "Amara",
    "Leo",
    "Nadia",
    "Kai",
    "Isabel",
    "Omar",
    "Lucia",
    "Elena",
]
LAST = [
    "Rivera",
    "Chen",
    "Patel",
    "Okafor",
    "Silva",
    "Kim",
    "Martinez",
    "Santos",
    "Bennett",
    "Ali",
    "Reyes",
    "Costa",
    "Torres",
    "Singh",
    "Park",
    "Wilson",
    "Garcia",
    "Lopez",
    "Nguyen",
    "Vega",
]


def generate(count: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    result = []
    for i in range(count):
        role, skills, industries = ARCHETYPES[i % len(ARCHETYPES)]
        years = rng.randint(10, 24) if role in ("CTO", "Founder") else rng.randint(1, 18)
        industry = rng.choice(industries)
        result.append(
            {
                "user_id": f"usr_{i + 1:05d}",
                "name": f"{FIRST[i % len(FIRST)]} {LAST[(i // len(FIRST) + i) % len(LAST)]}",
                "role": role,
                "industry": industry,
                "skills": rng.sample(skills, rng.randint(3, len(skills))),
                "experience_years": years,
                "interests": [
                    rng.choice(["Startups", "Mentorship", "Sustainable innovation"]),
                    f"Innovation in {industry.lower()}",
                    skills[0],
                ],
                "professional_summary": f"{role} with {years} years of experience in {industry.lower()}, "
                f"focused on {skills[0].lower()} and cross-functional collaboration.",
            }
        )
    for index, profile in enumerate(curated_profiles(), start=80):
        if index < len(result):
            result[index] = profile
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, choices=[100, 1000, 10000, 25000, 50000], default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dataset/professional_profiles.json",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(generate(args.count, args.seed), indent=2), encoding="utf-8")
    print(f"Wrote {args.count} synthetic profiles to {args.output}")
