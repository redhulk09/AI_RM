import { GlassCard } from "./glass-card";

export function MetricCard({ label, value, detail, accent = false }: { label: string; value: string; detail: string; accent?: boolean }) {
  return <GlassCard className={accent ? "glow" : ""}><p className="text-xs uppercase tracking-[.18em] text-black/42">{label}</p><p className="mt-5 text-4xl font-semibold tracking-[-.05em]">{value}</p><p className="mt-2 text-sm text-black/48">{detail}</p></GlassCard>;
}
