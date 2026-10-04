"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowUpRight, BookOpen, GitCompareArrows, LayoutDashboard, Network, Radar, Users, Workflow } from "lucide-react";
import { cn } from "@/lib/utils";
import { API_URL } from "@/lib/api";
import { DEMO_MODE } from "@/lib/demo";

const links = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/match", label: "1-to-1 Match", icon: GitCompareArrows },
  { href: "/ranking", label: "1-to-N Ranking", icon: Radar },
  { href: "/profiles", label: "Professional Profiles", icon: Users },
  { href: "/engine", label: "Engine Explanation", icon: Workflow },
];
export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return <div className="app-shell">
    <aside className="sidebar">
      <Link className="brand" href="/"><span className="brand-icon"><Network size={23} /></span>twintro<span className="brand-dot">.</span></Link>
      <div className="workspace"><span className="workspace-symbol">T</span><div>Professional matching<small>Hackathon workspace</small></div><span className="version">01</span></div>
      <span className="nav-caption">WORKSPACE</span>
      <nav aria-label="Main navigation">{links.map(({ href, label, icon: Icon }) => <Link key={href} href={href} className={cn("nav-item", path === href && "active")}><Icon size={18} /><span>{label}</span>{path === href && <span className="active-dot" />}</Link>)}</nav>
      <div className="sidebar-bottom"><div className="engine-card"><span className="eyebrow"><span className="status-dot" /> HYBRID DECISION ENGINE</span><strong>Built for meaningful<br />connections.</strong><p>Six dimensions. One explainable score.</p><Link href="/engine">Explore the engine <ArrowUpRight size={15} /></Link></div>
      <a className="docs-link" href={`${API_URL}/docs`} target="_blank" rel="noreferrer"><BookOpen size={16} /> API documentation <ArrowUpRight size={14} /></a>
      <div className="user"><span className="avatar small">TW</span><div>Twintro workspace<small>THDE-1.0 · Local-first</small></div></div></div>
    </aside>
    <div className="main-shell"><header className="topbar"><span>Workspace <span className="slash">/</span> <strong>{links.find(l => l.href === path)?.label || "Professional matching"}</strong></span><div className="topbar-badges">{DEMO_MODE && <span className="demo-badge">Hackathon Demo</span>}<span className="topbar-tag"><span className="status-dot" /> Deterministic scoring</span></div></header><main>{children}</main><footer>Designed for professional possibility.<span>TWINTRO / THDE-1.0</span></footer></div>
  </div>;
}
