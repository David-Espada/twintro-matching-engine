"""Hand-authored synthetic profiles, with stable IDs, for repeatable presentation cases."""

DEMO_PROFILES = [
    (
        "Avery Quinn",
        "AI Engineer",
        "Technology",
        8,
        ["Python", "Machine Learning", "PyTorch", "FastAPI"],
        ["AI Products", "Startups"],
    ),
    (
        "Casey Lin",
        "AI Engineer",
        "Technology",
        8,
        ["Python", "Machine Learning", "PyTorch", "FastAPI"],
        ["AI Products", "Startups"],
    ),
    (
        "Rowan Patel",
        "Machine Learning Engineer",
        "Technology",
        7,
        ["Python", "Machine Learning", "PyTorch", "TensorFlow"],
        ["AI Products", "Startups"],
    ),
    (
        "Jordan Reyes",
        "Product Manager",
        "Technology",
        8,
        ["Product strategy", "Roadmapping", "User research", "Analytics"],
        ["AI Products", "Startups"],
    ),
    (
        "Maya Costa",
        "Marketing Manager",
        "Ecommerce",
        6,
        ["Content marketing", "SEO", "Campaign management", "Analytics"],
        ["Customer experience", "Business growth"],
    ),
    (
        "Noah Bennett",
        "Sales Manager",
        "Ecommerce",
        8,
        ["Sales strategy", "CRM", "Negotiation", "Partnerships"],
        ["Customer experience", "Business growth"],
    ),
    (
        "Sofia Park",
        "UX Designer",
        "Technology",
        7,
        ["Figma", "User research", "Product strategy", "Analytics"],
        ["AI Products", "Startups"],
    ),
    (
        "Omar Vega",
        "Cybersecurity Engineer",
        "Technology",
        9,
        ["Threat modeling", "Security auditing", "Incident response", "Linux"],
        ["Cloud security", "Reliable systems"],
    ),
    (
        "Elena Singh",
        "DevOps Engineer",
        "Technology",
        8,
        ["Docker", "Kubernetes", "Terraform", "Linux"],
        ["Cloud security", "Reliable systems"],
    ),
    (
        "Mateo Santos",
        "Restaurant Operations Manager",
        "Hospitality",
        16,
        ["Food safety", "Menu planning", "Kitchen scheduling", "Restaurant service"],
        ["Culinary arts", "Local cuisine"],
    ),
    (
        "Priya Chen",
        "Backend Developer",
        "Technology",
        8,
        ["Python", "FastAPI", "PostgreSQL", "API design"],
        ["AI Products", "Startups"],
    ),
    (
        "Leo Rivera",
        "Backend Developer",
        "Technology",
        4,
        ["Java", "SQL", "API design", "Docker"],
        ["Payment systems", "Reliable systems"],
    ),
]


def curated_profiles() -> list[dict]:
    return [
        {
            "user_id": f"usr_{81 + i:05d}",
            "name": name,
            "role": role,
            "industry": industry,
            "experience_years": years,
            "skills": skills.copy(),
            "interests": interests.copy(),
            "professional_summary": f"Synthetic {role.lower()} with {years} years in {industry.lower()}, "
            f"focused on {skills[0].lower()} and {interests[0].lower()}.",
        }
        for i, (name, role, industry, years, skills, interests) in enumerate(DEMO_PROFILES)
    ]


DEMO_CASES = [
    (
        "Nearly identical peers",
        "usr_00081",
        "usr_00082",
        "Very high affinity; lower complementarity",
        "Same professional evidence, different people. Demonstrates peer collaboration without a cross-functional bonus.",
    ),
    (
        "Related AI specialties",
        "usr_00081",
        "usr_00083",
        "High affinity; lower complementarity",
        "Related titles and shared skills remain similar even when one framework differs.",
    ),
    (
        "AI meets product",
        "usr_00004",
        "usr_00008",
        "Lower affinity; exceptional complementarity",
        "The original default pair: different industries and skills can coexist with valuable role and domain relationships.",
    ),
    (
        "Marketing meets sales",
        "usr_00085",
        "usr_00086",
        "Lower affinity; strong or exceptional complementarity",
        "Demonstrates business collaboration without needing identical skills.",
    ),
    (
        "Design meets product",
        "usr_00087",
        "usr_00084",
        "Good or stronger affinity and high complementarity",
        "Shared product research and analytics support affinity; design and product strengths support collaboration.",
    ),
    (
        "Security meets DevOps",
        "usr_00088",
        "usr_00089",
        "Lower affinity; strong complementarity",
        "Security plus infrastructure is professionally useful. Shared Linux and interests are separate evidence.",
    ),
    (
        "Different professional worlds",
        "usr_00081",
        "usr_00090",
        "Low affinity and low complementarity",
        "An intentional negative control: AI engineering and restaurant operations are not automatically complementary.",
    ),
    (
        "Backend across toolsets",
        "usr_00091",
        "usr_00092",
        "Moderate affinity; lower complementarity",
        "Shared role, industry and API design provide alignment, while tools, experience and interests differ.",
    ),
    (
        "AI meets backend engineering",
        "usr_00081",
        "usr_00091",
        "Good affinity and strong complementarity",
        "Shows shared Python/FastAPI expertise alongside useful AI and software engineering relationships.",
    ),
]
