"use client";
import { BriefcaseBusiness, Building2, PencilLine, UserRound } from "lucide-react";
import { useId, useState } from "react";
import type { Profile } from "@/lib/types";
import { initials } from "@/lib/utils";
import { Tags } from "./common";
import { Button } from "./ui/button";
import { groupDemoProfiles } from "@/lib/demo";

export function ProfileCard({ profile, compact = false }: { profile: Profile; compact?: boolean }) {
  return <div className={compact ? "profile-summary compact" : "profile-summary"}>
    <div className="profile-identity"><span className="avatar">{initials(profile.name)}</span><div><h3>{profile.name}</h3><p>{profile.role || "Role not provided"}</p></div></div>
    <div className="profile-facts"><span><Building2 size={14} />{profile.industry || "Industry not provided"}</span><span><BriefcaseBusiness size={14} />{profile.experience_years == null ? "Experience not provided" : `${profile.experience_years} years experience`}</span></div>
    <div className="field-caption">SKILLS</div><Tags values={profile.skills} empty="No skills provided" />
    {!compact && <><div className="field-caption">PROFESSIONAL INTERESTS</div><Tags values={profile.interests} empty="No interests provided" /></>}
  </div>;
}
export function ProfileSelector({ profiles, value, onChange, label, startManual = false }: { profiles: Profile[]; value: Profile | null; onChange: (p: Profile) => void; label: string; startManual?: boolean }) {
  const [manual, setManual] = useState(startManual);
  const id = useId();
  const { recommended, remaining } = groupDemoProfiles(profiles);
  const update = (key: keyof Profile, val: unknown) => onChange({ user_id: `manual-${id}`, name: "", role: null, industry: null, skills: [], interests: [], experience_years: null, ...value, [key]: val });
  return <section className="panel profile-selector"><div className="panel-heading"><h2><UserRound size={17} />{label}</h2><Button type="button" variant="ghost" size="sm" onClick={() => setManual(!manual)}><PencilLine size={14} />{manual ? "Use demo profile" : "Enter manually"}</Button></div>
    {!manual ? <><label className="sr-only" htmlFor={id}>{label}</label><select id={id} value={value?.user_id || ""} onChange={e => { const p = profiles.find(p => p.user_id === e.target.value); if (p) onChange(p); }}><option value="" disabled>Select a professional</option>{recommended.length > 0 && <optgroup label="Recommended demo profiles">{recommended.map(p => <option key={p.user_id} value={p.user_id}>{p.name} · {p.role}</option>)}</optgroup>}<optgroup label={recommended.length ? "More professionals" : "Professionals"}>{remaining.map(p => <option key={p.user_id} value={p.user_id}>{p.name} · {p.role}</option>)}</optgroup></select>{value && <ProfileCard profile={value} />}</> :
    <div className="manual-form">
      <label>Name<input required maxLength={150} value={value?.name || ""} onChange={e => update("name", e.target.value)} placeholder="Alex Rivera" /></label>
      <label>Professional role<input maxLength={200} value={value?.role || ""} onChange={e => update("role", e.target.value || null)} placeholder="AI Engineer" /></label>
      <div className="form-row"><label>Industry<input maxLength={150} value={value?.industry || ""} onChange={e => update("industry", e.target.value || null)} placeholder="Technology" /></label><label>Experience (years)<input type="number" min="0" max="80" step="0.5" value={value?.experience_years ?? ""} onChange={e => update("experience_years", e.target.value === "" ? null : Number(e.target.value))} /></label></div>
      <label>Skills <span className="muted">(comma separated)</span><input value={value?.skills.join(",") || ""} onChange={e => update("skills", e.target.value.split(","))} placeholder="Python, FastAPI, Machine Learning" /></label>
      <label>Interests <span className="muted">(comma separated)</span><input value={value?.interests.join(",") || ""} onChange={e => update("interests", e.target.value.split(","))} placeholder="Startups, AI products" /></label>
      <p className="small-text muted">Only name is required. Missing dimensions reduce confidence and are excluded from affinity scoring.</p>
    </div>}
  </section>;
}
