from app.services.matching.scoring import weighted_score
from app.services.normalization.normalizer import NormalizedProfile
from app.services.normalization.taxonomy import DOMAIN_COMPLEMENTS, ROLE_COMPLEMENTS


def relation(a: str, b: str, matrix: dict[tuple[str, str], float]) -> float:
    return matrix.get((a, b), 40.0 if a == b != "other" else 10.0)


def complementarity(a: NormalizedProfile, b: NormalizedProfile) -> tuple[float | None, list[str]]:
    role = relation(a.family, b.family, ROLE_COMPLEMENTS) if a.role and b.role else None
    if a.role and a.role == b.role:
        role = 40.0  # Exact same titles provide same-role evidence, including unclassified professions.
    domain = None
    strengths: list[str] = []
    if role is not None and (a.family, b.family) in ROLE_COMPLEMENTS:
        strengths.append(f"{a.family.replace('_', ' ')} + {b.family.replace('_', ' ')}")
    if a.domains and b.domains:
        forward = [max(relation(x, y, DOMAIN_COMPLEMENTS) for y in b.domains) for x in a.domains]
        reverse = [max(relation(x, y, DOMAIN_COMPLEMENTS) for x in a.domains) for y in b.domains]
        domain = (sum(forward) / len(forward) + sum(reverse) / len(reverse)) / 2
        strengths += [
            f"{x.replace('_', ' ')} + {y.replace('_', ' ')}"
            for x in a.domains
            for y in b.domains
            if (x, y) in DOMAIN_COMPLEMENTS
        ]
    # No recognized domains means no evidence for the domain subcomponent.
    if role is None and domain is None:
        return None, []
    return weighted_score({"role": role, "domain": domain}, {"role": 0.7, "domain": 0.3}), strengths
