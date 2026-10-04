"use client";
import { useMemo, useState } from "react";
import { Search, Users, Check, Plus, LoaderCircle } from "lucide-react";
import { ErrorNotice, Loading, PageTitle } from "@/components/common";
import { ProfileCard, ProfileSelector } from "@/components/profile-card";
import { Button } from "@/components/ui/button";
import { useProfiles } from "@/lib/use-profiles";
import { request } from "@/lib/api";
import type { Profile } from "@/lib/types";

export default function ProfilesPage() {
  const { profiles, error: loadError, loading } = useProfiles();
  const [query, setQuery] = useState(""), [industry, setIndustry] = useState("");
  const [mode, setMode] = useState("demo"), [stored, setStored] = useState<Profile[]>([]), [total, setTotal] = useState(0);
  const [error, setError] = useState(""), [busy, setBusy] = useState(false), [saved, setSaved] = useState("");
  const [editing, setEditing] = useState(false), [draft, setDraft] = useState<Profile | null>(null);
  const pool = mode === "demo" ? profiles : stored;
  const industries = [...new Set(pool.map(p => p.industry).filter(Boolean))].sort();
  const filtered = useMemo(() => pool.filter(p => (!industry || p.industry === industry) &&
    [p.name, p.role, ...p.skills].join(" ").toLowerCase().includes(query.toLowerCase())), [pool, query, industry]);
  async function fetchStored(append = false) {
    setBusy(true); setError("");
    try { const data = await request<{items: Profile[]; total: number}>(`/profiles?limit=100&offset=${append ? stored.length : 0}`); setStored(append ? [...stored, ...data.items] : data.items); setTotal(data.total); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function save(e: React.FormEvent) {
    e.preventDefault(); if (!draft) return; setBusy(true); setError(""); setSaved("");
    try { await request<Profile>("/profiles", draft); setSaved(`${draft.name} saved to PostgreSQL.`); setEditing(false); if (mode === "stored") await fetchStored(); }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  return <><PageTitle eyebrow="THE PEOPLE BEHIND THE POSSIBILITIES" title="Professional network." description="Explore expertise, discover perspectives, and get to know your potential collaborators." action={<Button onClick={() => { setDraft({ user_id: `usr_${crypto.randomUUID()}`, name: "", role: null, industry: null, skills: [], interests: [], experience_years: null }); setEditing(!editing); }}><Plus size={17} />{editing ? "Close editor" : "Add profile"}</Button>} />
    <ErrorNotice message={loadError || error} />{saved && <p role="status" className="success-message"><Check size={17} />{saved}</p>}
    {editing && <form className="profile-editor" onSubmit={save}><ProfileSelector startManual label="Profile editor" profiles={profiles} value={draft} onChange={setDraft} /><Button disabled={busy || !draft?.name.trim()}>{busy ? <LoaderCircle className="animate-spin" size={17} /> : <Check size={17} />}Save profile to database</Button></form>}
    <div className="profile-toolbar"><label className="search-field"><Search size={18} /><input aria-label="Search professionals" placeholder="Search name, role, or skill…" value={query} onChange={e => setQuery(e.target.value)} /></label><select aria-label="Filter by industry" value={industry} onChange={e => setIndustry(e.target.value)}><option value="">All industries</option>{industries.map(i => <option key={i!}>{i}</option>)}</select><select aria-label="Profile source" value={mode} onChange={e => { setMode(e.target.value); setIndustry(""); if (e.target.value === "stored") void fetchStored(); }}><option value="demo">Demo network</option><option value="stored">Stored profiles</option></select></div>
    <div className="section-heading"><span className="small-text muted"><Users size={15} /> {filtered.length} professionals{mode === "stored" ? ` shown · ${total} stored` : " · Synthetic demo dataset"}</span></div>
    {loading || busy ? <Loading /> : <div className="profiles-grid">{filtered.map(p => <article key={p.user_id} className="panel directory-card"><ProfileCard profile={p} /><div className="directory-footer"><span>{p.user_id}</span><span className="mini-badge">{mode === "demo" ? "Demo profile" : "Stored profile"}</span></div></article>)}</div>}
    {!loading && !busy && !filtered.length && <div className="empty-state"><Users size={28} /><h3>No professionals found</h3><p>Try another search or add a profile to this network.</p></div>}
    {mode === "stored" && stored.length < total && <Button className="load-more" variant="outline" disabled={busy} onClick={() => fetchStored(true)}>Load more profiles</Button>}
  </>;
}
