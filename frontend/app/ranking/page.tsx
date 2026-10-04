"use client";
import { useState } from "react";
import { ArrowRight, Radar } from "lucide-react";
import { ProfileSelector } from "@/components/profile-card";
import { RankingResults } from "@/components/ranking-results";
import { ErrorNotice, Loading, PageTitle } from "@/components/common";
import { Button } from "@/components/ui/button";
import { rank } from "@/lib/api";
import { useProfiles } from "@/lib/use-profiles";
import type { Profile, Ranking } from "@/lib/types";

export default function RankingPage() {
  const { profiles, error: loadError, loading } = useProfiles();
  const [source, setSource] = useState<Profile | null>(null), [pool, setPool] = useState("demo");
  const [limit, setLimit] = useState(20), [result, setResult] = useState<Ranking | null>(null);
  const [error, setError] = useState(""), [busy, setBusy] = useState(false);
  const selected = source || profiles[3] || null;
  async function analyze(e: React.FormEvent) {
    e.preventDefault(); if (!selected) return;
    setBusy(true); setResult(null); setError("");
    try { setResult(await rank(selected, pool === "demo" ? profiles : null, limit)); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  return <><PageTitle eyebrow="DISCOVER YOUR NEXT CONNECTION" title="Find your people." description="One professional. A world of potential. Rank the connections that make sense for you." />
    <ErrorNotice message={loadError || error} />{loading ? <Loading /> : <form onSubmit={analyze}><fieldset disabled={busy} className="ranking-config"><ProfileSelector label="Source professional" profiles={profiles} value={selected} onChange={p => { setSource(p); setResult(null); }} /><section className="panel ranking-options"><div className="eyebrow">MATCHING PREFERENCES</div><h2>Make room for possibility.</h2><p>We look for shared expertise and complementary strengths across your candidate pool.</p><label>Candidate pool<select aria-label="Candidate pool" value={pool} onChange={e => { setPool(e.target.value); setResult(null); }}><option value="demo">Demo professionals · {profiles.length} profiles</option><option value="stored">Stored PostgreSQL profiles</option></select></label><label>Results to show<select aria-label="Results to show" value={limit} onChange={e => { setLimit(Number(e.target.value)); setResult(null); }}>{[5, 10, 20, 50, 100].map(n => <option key={n}>{n}</option>)}</select></label><Button type="submit" disabled={busy || !selected?.name.trim()}><Radar size={17} />{busy ? "Finding connections…" : "Find Best Matches"}<ArrowRight size={17} /></Button><p className="small-text muted">Your own profile is automatically excluded.</p></section></fieldset></form>}
    {busy && <Loading label="Evaluating the candidate pool and ranking matches…" />}
    {result && <RankingResults result={result} />}
  </>;
}
