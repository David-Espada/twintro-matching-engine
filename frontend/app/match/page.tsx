"use client";
import { useState } from "react";
import { ArrowRight, GitCompareArrows, LoaderCircle } from "lucide-react";
import { ProfileSelector } from "@/components/profile-card";
import { MatchResult } from "@/components/match-result";
import { ErrorNotice, Loading, PageTitle } from "@/components/common";
import { Button } from "@/components/ui/button";
import { compare } from "@/lib/api";
import { useProfiles } from "@/lib/use-profiles";
import type { Match, Profile } from "@/lib/types";

export default function MatchPage() {
  const { profiles, error: loadError, loading } = useProfiles();
  const [a, setA] = useState<Profile | null>(null), [b, setB] = useState<Profile | null>(null);
  const [result, setResult] = useState<Match | null>(null), [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const source = a || profiles[3] || null, target = b || profiles[7] || null;
  async function analyze(e: React.FormEvent) {
    e.preventDefault(); if (!source || !target) return;
    setBusy(true); setError(""); setResult(null);
    try { setResult(await compare(source, target)); } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  return <><PageTitle eyebrow="FIND YOUR PROFESSIONAL SYNERGY" title="Better together." description="Discover the shared expertise and different strengths behind a meaningful connection." />
    <ErrorNotice message={loadError || error} />{loading ? <Loading /> : <form onSubmit={analyze}>
    <fieldset disabled={busy} className="comparison-inputs"><div className="two-columns"><ProfileSelector label="Professional A" profiles={profiles} value={source} onChange={p => { setA(p); setResult(null); }} /><ProfileSelector label="Professional B" profiles={profiles} value={target} onChange={p => { setB(p); setResult(null); }} /></div>
    <div className="analyze-action"><span><GitCompareArrows size={16} /> Six dimensions. One transparent comparison.</span><Button disabled={!source?.name.trim() || !target?.name.trim() || busy} type="submit">{busy ? <LoaderCircle size={17} className="animate-spin" /> : <GitCompareArrows size={17} />}{busy ? "Analyzing profiles…" : "Analyze Match"}<ArrowRight size={17} /></Button></div></fieldset></form>}
    {busy && <Loading label="Comparing professional concepts with the local semantic model…" />}
    {result && <MatchResult result={result} />}
    {!result && !busy && <div className="empty-state"><div className="empty-icon"><GitCompareArrows size={26} /></div><h3>A great connection starts with understanding.</h3><p>Select two professionals to reveal their affinity, shared skills, and complementary strengths.</p></div>}
  </>;
}
