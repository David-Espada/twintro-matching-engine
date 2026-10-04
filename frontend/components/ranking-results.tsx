"use client";
import { useState } from "react";
import { ChevronDown, ChevronUp, Clock3, Users } from "lucide-react";
import type { Ranking } from "@/lib/types";
import { EMPTY_FILTERS, filterRanking } from "@/lib/ranking";
import { initials } from "@/lib/utils";
import { MatchResult } from "./match-result";
import { RankingFilters } from "./ranking-filters";
import { Tags } from "./common";

export function RankingResults({ result }: { result: Ranking }) {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [expanded, setExpanded] = useState<string | null>(null);
  const visible = filterRanking(result.results, filters);
  const metrics = result.metadata;
  const retrievalLabel = metrics.retrieval_mode === "hybrid"
    ? metrics.retrieval_backend === "pgvector" ? "Hybrid pgvector + complementarity" : "Hybrid in-memory semantic + complementarity"
    : "Full candidate evaluation";
  return <>
    <div className="section-heading"><h2>Your strongest connections <span className="count-badge">{visible.length} / {result.results.length}</span></h2><span className="small-text muted"><Users size={14} />{metrics.profiles_fully_scored.toLocaleString()} evaluated <Clock3 size={14} />{metrics.execution_time_ms.toLocaleString()} ms</span></div>
    <p className="small-text muted">{retrievalLabel} · Ranked by affinity. Complementarity is shown separately.</p>
    <details className="panel engine-metrics">
      <summary>Engine metrics</summary>
      <dl>
        <div><dt>Network profiles</dt><dd>{metrics.total_network_size.toLocaleString()}</dd></div>
        <div><dt>Candidates retrieved</dt><dd>{metrics.candidate_pool_size.toLocaleString()}</dd></div>
        <div><dt>Fully evaluated</dt><dd>{metrics.profiles_fully_scored.toLocaleString()}</dd></div>
        <div><dt>Retrieval</dt><dd>{retrievalLabel}</dd></div>
        {metrics.retrieval_mode === "hybrid" && <>
          <div><dt>Semantic / complementary</dt><dd>{metrics.semantic_candidates} / {metrics.complementarity_candidates}</dd></div>
          <div><dt>Vector / complementarity retrieval</dt><dd>{metrics.vector_retrieval_time_ms.toLocaleString()} / {metrics.complementarity_retrieval_time_ms.toLocaleString()} ms</dd></div>
        </>}
        <div><dt>THDE scoring</dt><dd>{metrics.thde_scoring_time_ms.toLocaleString()} ms</dd></div>
        <div><dt>Ranking time</dt><dd>{metrics.execution_time_ms.toLocaleString()} ms</dd></div>
      </dl>
    </details>
    {result.results.length > 0 && <RankingFilters results={result.results} value={filters} onChange={setFilters} />}
    <div className="ranking-list">{visible.map(({match, rank}) => {
      const open = expanded === match.target_user.user_id;
      const complement = match.score_breakdown.complementarity;
      return <article className="panel ranking-card" key={match.target_user.user_id}>
        <button className="ranking-row" onClick={() => setExpanded(open ? null : match.target_user.user_id)} aria-expanded={open} aria-label={`Rank ${rank}: ${match.target_user.name}, view comparison`}>
          <span className="rank-number">{String(rank).padStart(2, "0")}</span>
          <span className="avatar">{initials(match.target_user.name)}</span>
          <span className="rank-person"><strong>{match.target_user.name}</strong><span>{match.target_user.role} <span className="muted">· {match.target_user.industry}</span></span></span>
          <span className="rank-score"><span className="rank-score-label">Affinity</span><strong>{match.metadata.available_weight === 0 ? "—" : <>{match.affinity_percentage.toFixed(1)}<small>%</small></>}</strong><span>{match.metadata.available_weight === 0 ? "Insufficient evidence" : match.match_level}</span></span>
          <span className="rank-complement"><span className="rank-score-label">Complementarity</span><strong>{complement === null ? "—" : <>{complement.toFixed(1)}<small>%</small></>}</strong><span>{match.complementarity_level ?? "Not available"}</span></span>
          {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
        <div className="rank-tags"><Tags values={match.evidence_tags.slice(0, 3)} empty="Open comparison to explore the available evidence" /></div>
        {open && <div className="ranking-detail"><MatchResult result={match} /></div>}
      </article>;
    })}</div>
    {!visible.length && <div className="empty-state"><Users size={30} /><h3>{result.results.length ? "No returned matches meet these filters" : "No candidates in this pool"}</h3><p>{result.results.length ? "Clear a filter or request more results. These filters do not search beyond the returned matches." : "Add stored profiles or switch to the demo pool."}</p></div>}
  </>;
}
