import type { Match } from "@/lib/types";
import { EMPTY_FILTERS, type RankingFilters as Filters } from "@/lib/ranking";
import { Button } from "./ui/button";

export function RankingFilters({ results, value, onChange }: { results: Match[]; value: Filters; onChange: (filters: Filters) => void }) {
  const families = [...new Set(results.map(m => m.target_role_family))].sort();
  const industries = [...new Set(results.flatMap(m => m.target_normalized_industry ? [m.target_normalized_industry] : []))].sort();
  function threshold(key: "minimumAffinity" | "minimumComplementarity", text: string) {
    const number = Number(text);
    onChange({ ...value, [key]: Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 0 });
  }
  return <section className="panel ranking-filter-panel" aria-label="Filter returned matches">
    <div className="panel-heading"><h2>Refine these results</h2><Button type="button" variant="ghost" size="sm" onClick={() => onChange(EMPTY_FILTERS)}>Clear filters</Button></div>
    <div className="ranking-filter-fields">
      <label>Minimum affinity (%)<input type="number" min={0} max={100} step={1} value={value.minimumAffinity} onChange={e => threshold("minimumAffinity", e.target.value)} /></label>
      <label>Minimum complementarity (%)<input type="number" min={0} max={100} step={1} value={value.minimumComplementarity} onChange={e => threshold("minimumComplementarity", e.target.value)} /></label>
      <label>Role family<select aria-label="Role family" value={value.roleFamily} onChange={e => onChange({...value, roleFamily: e.target.value})}><option value="">All returned families</option>{families.map(f => <option key={f} value={f}>{f.replaceAll("_", " ")}</option>)}</select></label>
      <label>Industry<select aria-label="Industry" value={value.industry} onChange={e => onChange({...value, industry: e.target.value})}><option value="">All returned industries</option>{industries.map(i => <option key={i} value={i}>{i}</option>)}</select></label>
    </div>
    <p className="small-text muted">Filters apply to the returned top results only, preserving backend rank. Increase “Results to show” and rerun to search more results. No scores are recalculated.</p>
  </section>;
}
