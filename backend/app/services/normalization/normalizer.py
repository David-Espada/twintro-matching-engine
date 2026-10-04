import re
from dataclasses import dataclass
from functools import lru_cache

from app.schemas.profile import ProfessionalProfile
from app.services.normalization.taxonomy import ALIASES, INDUSTRY_ALIASES, ROLE_FAMILIES, SKILL_DOMAINS


@lru_cache(maxsize=10000)
def canonical(value: str) -> str:
    value = " ".join(value.lower().strip().split())
    return ALIASES.get(value, value)


@lru_cache(maxsize=4096)
def role_family(role: str | None) -> str:
    if not role:
        return "other"
    for family, phrases in ROLE_FAMILIES.items():
        if any(re.search(r"\b" + re.escape(term) + r"\b", role) for term in phrases):
            return family
    return "other"


@lru_cache(maxsize=10000)
def skill_domain(skill: str) -> str:
    return next((domain for domain, terms in SKILL_DOMAINS.items() if skill in terms), "other")


@dataclass(frozen=True)
class NormalizedProfile:
    original: ProfessionalProfile
    role: str | None
    family: str
    industry: str | None
    skills: tuple[str, ...]
    domains: tuple[str, ...]
    interests: tuple[str, ...]

    @property
    def completeness(self) -> float:
        return (
            sum(
                (
                    bool(self.role),
                    bool(self.industry),
                    bool(self.skills),
                    self.original.experience_years is not None,
                    bool(self.interests),
                )
            )
            / 5
        )

    def embedding_text(self) -> str:
        return (
            f"Role: {self.role or ''}\nIndustry: {self.industry or ''}\n"
            f"Skills: {', '.join(self.skills)}\nExperience: {self.original.experience_years}\n"
            f"Professional interests: {', '.join(self.interests)}"
        )


def normalize(profile: ProfessionalProfile) -> NormalizedProfile:
    role = canonical(profile.role) if profile.role else None
    industry = canonical(profile.industry) if profile.industry else None
    skills = tuple(sorted({canonical(s) for s in profile.skills}))
    return NormalizedProfile(
        profile,
        role,
        role_family(role),
        INDUSTRY_ALIASES.get(industry, industry),
        skills,
        tuple(sorted({skill_domain(s) for s in skills} - {"other"})),
        tuple(sorted({canonical(s) for s in profile.interests})),
    )
