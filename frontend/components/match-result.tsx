import { Clock3, Layers3, Sparkles } from "lucide-react";
import { dimensions, type Match } from "@/lib/types";
import { Tags } from "./common";
import { ScoreSummary } from "./score-summary";

export function MatchResult({ result }: { result: Match }) {
  return <div className="match-result" aria-live="polite">
    <div className="section-heading"><h2>Match analysis</h2><span className="muted small-text"><Clock3 size={13} /> {result.metadata.execution_time_ms.toLocaleString()} ms · {result.metadata.engine_version}</span></div>
    <ScoreSummary result={result} />
    <section className="panel breakdown"><div className="panel-heading"><h2>What makes this match</h2><span className="small-text muted">Score / 100</span></div>
      {dimensions.map(d => { const score = result.score_breakdown[d.key]; return <div className="score-dimension" key={d.key}><div><span>{d.label}<small>{d.weight}% weight</small></span><strong>{score === null ? "Not available" : score.toFixed(1)}</strong></div><div className="bar-track"><div style={{ width: `${score || 0}%`, background: d.color }} /></div></div>; })}
      {result.metadata.available_weight < 1 && <p className="small-text muted">Available weights were normalized. Missing data does not count as zero.</p>}
    </section>
    <section className="panel justification"><div className="justification-icon"><Sparkles size={22} /></div><div><h3>What the evidence says <span className="mini-badge">{result.metadata.justification_provider === "openai" ? "AI explanation" : result.justification ? "Evidence-based explanation" : "Deterministic insight"}</span></h3><p>{result.justification || result.connection_insight}</p></div></section>
    <div className="two-columns"><section className="panel evidence"><h3><Layers3 size={17} /> Shared strengths</h3><div className="field-caption">SKILLS</div><Tags values={result.profile_comparison.shared_skills} /><div className="field-caption">PROFESSIONAL DOMAINS</div><Tags values={result.profile_comparison.shared_domains} /></section><section className="panel evidence"><h3><Sparkles size={17} /> Complementary strengths</h3><p className="small-text muted">Different capabilities with a useful professional relationship.</p><Tags values={result.profile_comparison.complementary_strengths} /></section></div>
    {result.profile_comparison.related_skills.length > 0 && <section className="panel evidence"><h3>Related skill concepts</h3><div className="related-skills">{result.profile_comparison.related_skills.slice(0, 6).map(s => <div key={`${s.source_skill}-${s.target_skill}`}><span>{s.source_skill} <span className="muted">↔</span> {s.target_skill}</span><span className="muted">{s.similarity.toFixed(0)}% semantic similarity</span></div>)}</div></section>}
  </div>;
}
