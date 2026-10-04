from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfessionalProfile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    user_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    role: str | None = Field(default=None, max_length=200)
    industry: str | None = Field(default=None, max_length=150)
    skills: list[str] = Field(default_factory=list, max_length=100)
    experience_years: float | None = Field(default=None, ge=0, le=80, allow_inf_nan=False)
    interests: list[str] = Field(default_factory=list, max_length=100)
    professional_summary: str | None = Field(default=None, max_length=3000)

    @field_validator("role", "industry", "professional_summary")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        return value or None

    @field_validator("skills", "interests")
    @classmethod
    def clean_list(cls, values: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(v.strip() for v in values if v.strip()))
        if any(len(v) > 150 for v in cleaned):
            raise ValueError("Each skill or interest must contain at most 150 characters")
        return cleaned
