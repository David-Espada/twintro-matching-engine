import { CheckCheck, GitMerge } from "lucide-react";
import type { Match } from "@/lib/types";

export function ScoreSummary({ result }: { result: Match }) {
  const noEvidence = result.metadata.available_weight === 0;
  const complement = result.score_breakdown.complementarity;
  return <>
    <div className="result-scorecards">
      <section className="panel affinity-panel" aria-label="Professional Affinity">
        <h3 className="eyebrow">Professional Affinity</h3>
        <div className="score-ring" style={{ background: `conic-gradient(var(--accent) ${result.affinity_percentage}%, #22332b 0)` }}>
          <div><strong>{noEvidence ? "—" : result.affinity_percentage.toFixed(1)}{!noEvidence && <small>%</small>}</strong><span>{noEvidence ? "Insufficient evidence" : "weighted affinity score"}</span></div>
        </div>
        <span className="match-level">{noEvidence ? "Add profile information" : result.match_level}</span>
        <p className="score-helper">Overall professional alignment across all six weighted dimensions.</p>
      </section>
      <section className="panel affinity-panel collaboration-panel" aria-label="Collaboration Potential">
        <h3 className="eyebrow">Collaboration Potential</h3>
        <div className="score-ring" style={{ background: `conic-gradient(#83bdf6 ${complement ?? 0}%, #24333f 0)` }}>
          <div><strong>{complement === null ? "—" : complement.toFixed(1)}{complement !== null && <small>%</small>}</strong><span>{complement === null ? "Not enough evidence" : "complementarity score"}</span></div>
        </div>
        <span className="match-level">{result.complementarity_level ?? "Complementarity unavailable"}</span>
        <p className="score-helper">Useful relationships between different strengths. This contributes 15% to affinity when all dimensions are present.</p>
      </section>
    </div>
    <div className="score-context"><p className="confidence"><CheckCheck size={15} /> {(result.confidence * 100).toFixed(0)}% confidence</p><p className="small-text muted">Confidence reflects available profile information, not guaranteed collaboration success.</p></div>
    <section className="panel connection-insight" aria-label="Professional Connection Insight">
      <GitMerge size={23} /><div><h3>Professional Connection Insight</h3><p>{result.connection_insight}</p><p className="small-text muted">Affinity and complementarity answer different questions. High collaboration potential does not mean high affinity.</p>{result.confidence < .8 && <p className="small-text muted">Some evidence is missing. Complete both profiles before drawing strong conclusions.</p>}</div>
    </section>
  </>;
}
