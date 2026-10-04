import type { Match } from "./types";

export interface RankingFilters {
  minimumAffinity: number;
  minimumComplementarity: number;
  roleFamily: string;
  industry: string;
}
export const EMPTY_FILTERS: RankingFilters = { minimumAffinity: 0, minimumComplementarity: 0, roleFamily: "", industry: "" };

/** Filter already-ranked API results; keep their original order and rank. */
export function filterRanking(results: Match[], filters: RankingFilters) {
  return results.map((match, index) => ({ match, rank: index + 1 })).filter(({match}) =>
    match.affinity_percentage >= filters.minimumAffinity &&
    (filters.minimumComplementarity === 0 || (match.score_breakdown.complementarity !== null &&
      match.score_breakdown.complementarity >= filters.minimumComplementarity)) &&
    (!filters.roleFamily || match.target_role_family === filters.roleFamily) &&
    (!filters.industry || match.target_normalized_industry === filters.industry)
  );
}
