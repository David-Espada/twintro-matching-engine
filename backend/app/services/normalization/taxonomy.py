"""Curated, symmetric relationships. Unknown concepts are never inferred as complements."""

ALIASES = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "js": "javascript",
    "ts": "typescript",
    "ux": "user experience",
    "ui": "user interface",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "aws": "amazon web services",
    "nlp": "natural language processing",
    "biz dev": "business development",
    "saas": "software as a service",
    "fintech": "financial technology",
}
ROLE_FAMILIES = {
    "security": ["cybersecurity", "security engineer", "security analyst", "ciso"],
    "leadership": ["founder", "chief", "ceo", "cto", "coo", "vp engineering"],
    "ai_data": [
        "ai engineer",
        "artificial intelligence",
        "machine learning",
        "data scientist",
        "data engineer",
        "data analyst",
        "research scientist",
    ],
    "product": ["product manager", "product owner", "product lead", "business analyst"],
    "design": ["designer", "design lead", "user experience", "user interface"],
    "marketing": ["marketing", "growth", "content strategist", "seo"],
    "sales_business": ["sales", "business development", "account executive", "partnership"],
    "finance_investment": ["investment", "finance", "financial", "accountant", "venture capital"],
    "operations": ["operations", "supply chain", "logistics", "project manager"],
    "engineering": ["engineer", "developer", "architect", "programmer"],
    "other": [],
}
SKILL_DOMAINS = {
    "software_engineering": [
        "python",
        "javascript",
        "typescript",
        "react",
        "next.js",
        "fastapi",
        "django",
        "java",
        "go",
        "node.js",
        "backend development",
        "api design",
    ],
    "ai_machine_learning": [
        "machine learning",
        "artificial intelligence",
        "tensorflow",
        "pytorch",
        "deep learning",
        "natural language processing",
        "computer vision",
        "mlops",
    ],
    "data": ["sql", "postgresql", "data modeling", "data analysis", "statistics", "pandas", "spark", "dbt"],
    "product": ["product strategy", "roadmapping", "agile", "user research", "a/b testing", "analytics"],
    "design": [
        "figma",
        "prototyping",
        "user experience",
        "user interface",
        "design systems",
        "visual design",
    ],
    "marketing_growth": ["seo", "content marketing", "growth strategy", "copywriting", "campaign management"],
    "sales_business": ["negotiation", "sales strategy", "crm", "business development", "partnerships"],
    "devops_cloud": ["docker", "kubernetes", "amazon web services", "azure", "terraform", "ci/cd", "linux"],
    "cybersecurity": ["threat modeling", "penetration testing", "security auditing", "incident response"],
    "finance": ["financial modeling", "valuation", "investment analysis", "risk management", "accounting"],
    "leadership": [
        "leadership",
        "team management",
        "fundraising",
        "strategic planning",
        "operations management",
    ],
    "other": [],
}
INDUSTRY_ALIASES = {
    "tech": "technology",
    "it": "technology",
    "information technology": "technology",
    "software": "technology",
    "banking": "finance",
    "financial services": "finance",
    "health care": "healthcare",
    "edtech": "education technology",
    "e-commerce": "ecommerce",
}


def symmetric(pairs: list[tuple[str, str, float]]) -> dict[tuple[str, str], float]:
    return {(x, y): score for a, b, score in pairs for x, y in [(a, b), (b, a)]}


ROLE_RELATIONS = symmetric(
    [
        ("engineering", "ai_data", 85),
        ("engineering", "security", 70),
        ("product", "design", 70),
        ("marketing", "sales_business", 75),
        ("leadership", "product", 65),
        ("finance_investment", "sales_business", 60),
        ("operations", "leadership", 65),
    ]
)
INDUSTRY_RELATIONS = symmetric(
    [
        ("technology", "financial technology", 85),
        ("finance", "financial technology", 90),
        ("technology", "education technology", 80),
        ("education", "education technology", 90),
        ("technology", "ecommerce", 75),
        ("retail", "ecommerce", 90),
        ("healthcare", "biotechnology", 85),
        ("manufacturing", "logistics", 65),
    ]
)
ROLE_COMPLEMENTS = symmetric(
    [
        ("engineering", "product", 95),
        ("engineering", "design", 90),
        ("ai_data", "product", 95),
        ("ai_data", "engineering", 90),
        ("marketing", "sales_business", 95),
        ("product", "design", 95),
        ("leadership", "finance_investment", 95),
        ("security", "operations", 90),
        ("ai_data", "sales_business", 85),
        ("engineering", "security", 85),
    ]
)
DOMAIN_COMPLEMENTS = symmetric(
    [
        ("software_engineering", "product", 95),
        ("software_engineering", "design", 90),
        ("ai_machine_learning", "product", 95),
        ("ai_machine_learning", "software_engineering", 90),
        ("marketing_growth", "sales_business", 95),
        ("product", "design", 95),
        ("leadership", "finance", 95),
        ("cybersecurity", "devops_cloud", 90),
        ("data", "sales_business", 90),
        ("data", "product", 90),
        ("software_engineering", "devops_cloud", 85),
    ]
)
