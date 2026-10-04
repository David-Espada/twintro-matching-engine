import { describe, expect, it } from "vitest";
import { EMPTY_FILTERS, filterRanking } from "./ranking";
import type { Match } from "./types";

// This fixture contains only fields used by the filtering helper; it is not a scorer.
const results = [
  {affinity_percentage: 91, score_breakdown: {complementarity: 40}, target_role_family: "ai_data", target_normalized_industry: "technology"},
  {affinity_percentage: 75, score_breakdown: {complementarity: 95}, target_role_family: "product", target_normalized_industry: "technology"},
  {affinity_percentage: 60, score_breakdown: {complementarity: 80}, target_role_family: "product", target_normalized_industry: "finance"},
  {affinity_percentage: 0, score_breakdown: {complementarity: null}, target_role_family: "other", target_normalized_industry: null},
] as Match[];

describe("post-ranking filters", () => {
  it("preserves server ordering and does not modify the result", () => {
    const before = structuredClone(results);
    const filtered = filterRanking(results, {...EMPTY_FILTERS, minimumComplementarity: 80});
    expect(filtered.map(r => r.rank)).toEqual([2, 3]);
    expect(results).toEqual(before);
  });
  it("combines all four filters", () => {
    expect(filterRanking(results, { minimumAffinity: 70, minimumComplementarity: 90, roleFamily: "product", industry: "technology" }).map(r => r.rank)).toEqual([2]);
  });
  it("handles inclusive boundaries and unavailable components", () => {
    expect(filterRanking(results, EMPTY_FILTERS)).toHaveLength(4);
    expect(filterRanking(results, {...EMPTY_FILTERS, minimumAffinity: 60, minimumComplementarity: 80}).map(r => r.rank)).toEqual([2, 3]);
    expect(filterRanking(results, {...EMPTY_FILTERS, minimumComplementarity: 100})).toEqual([]);
    expect(filterRanking([], EMPTY_FILTERS)).toEqual([]);
  });
});
