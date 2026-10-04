export interface Profile {
  user_id: string; name: string; role: string | null; industry: string | null; skills: string[];
  experience_years: number | null; interests: string[]; professional_summary?: string | null;
}
export type Dimension = "skills" | "role" | "industry" | "experience" | "interests" | "complementarity";
export interface Match {
  match_mode: string; source_user: Profile; target_user: Profile; affinity_percentage: number;
  match_level: string; confidence: number; score_breakdown: Record<Dimension, number | null>;
  complementarity_level: string | null; connection_insight: string;
  target_role_family: string; target_normalized_industry: string | null; evidence_tags: string[];
  profile_comparison: { shared_domains: string[]; shared_skills: string[];
    related_skills: { source_skill: string; target_skill: string; similarity: number }[]; complementary_strengths: string[] };
  justification: string | null;
  metadata: { execution_time_ms: number; engine_version: string; available_weight: number; justification_provider: string };
}
export interface Ranking {
  results: Match[];
  metadata: {
    profiles_evaluated: number; total_network_size: number; candidate_pool_size: number;
    profiles_fully_scored: number; semantic_candidates: number; complementarity_candidates: number;
    retrieval_backend: "none" | "pgvector" | "numpy";
    vector_retrieval_time_ms: number; complementarity_retrieval_time_ms: number; thde_scoring_time_ms: number;
    execution_time_ms: number; ranking_limit: number; retrieval_mode: string;
  };
}
export const dimensions: { key: Dimension; label: string; weight: number; color: string }[] = [
  { key: "skills", label: "Skills", weight: 30, color: "#5be3a6" },
  { key: "role", label: "Role", weight: 20, color: "#83bdf6" },
  { key: "industry", label: "Industry", weight: 15, color: "#b5a0ed" },
  { key: "experience", label: "Experience", weight: 10, color: "#e6c57e" },
  { key: "interests", label: "Interests", weight: 10, color: "#e59fbb" },
  { key: "complementarity", label: "Complementarity", weight: 15, color: "#75d4d5" },
];
