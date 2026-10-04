import { ArrowDown, BrainCircuit, GitMerge, Layers3 } from "lucide-react";

export function EngineFlow() {
  return <section className="panel engine-flow" aria-label="How the decision engine works">
    <div className="flow-step"><h3>Professional Profiles</h3><p>Roles, industry, skills, experience, interests</p></div><ArrowDown aria-hidden="true" />
    <div className="flow-step"><h3>Normalization</h3><p>Clean concepts, deduplicate, map professional families</p></div><ArrowDown aria-hidden="true" />
    <div className="flow-branches">
      <div className="flow-step"><Layers3 size={21} /><h3>Structured Matching</h3><p>Exact overlap, families, industries and experience</p></div><span aria-hidden="true">+</span>
      <div className="flow-step"><BrainCircuit size={21} /><h3>Semantic Matching</h3><p>Sentence Transformers generate semantic representations.</p></div><span aria-hidden="true">+</span>
      <div className="flow-step"><GitMerge size={21} /><h3>Complementarity Analysis</h3><p>Useful relationships between different strengths</p></div>
    </div><ArrowDown aria-hidden="true" />
    <div className="flow-step flow-decision"><h3>Deterministic Weighted Decision</h3><p>The Twintro Decision Engine makes the decision.</p></div><ArrowDown aria-hidden="true" />
    <div className="flow-outputs"><span>Affinity</span><b>+</b><span>Complementarity</span><b>+</b><span>Confidence</span></div><ArrowDown aria-hidden="true" />
    <div className="flow-step"><h3>Optional AI Explanation</h3><p>The explanation layer narrates the result. A deterministic template works without OpenAI.</p></div>
    <p className="language-model-rule">The AI language model does not calculate the score.</p>
  </section>;
}
