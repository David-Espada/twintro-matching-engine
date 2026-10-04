import { AlertCircle, LoaderCircle } from "lucide-react";
export function PageTitle({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>;
}
export function ErrorNotice({ message }: { message: string }) { return message ? <div role="alert" className="error-notice"><AlertCircle size={18} />{message}</div> : null; }
export function Loading({ label = "Loading professional profiles…" }: { label?: string }) { return <div role="status" className="loading"><LoaderCircle className="animate-spin" size={20} />{label}</div>; }
export function Tags({ values, empty = "None identified" }: { values: string[]; empty?: string }) { return values.length ? <div className="tags">{values.map(v => <span key={v}>{v.replaceAll("_", " ")}</span>)}</div> : <p className="muted small-text">{empty}</p>; }
