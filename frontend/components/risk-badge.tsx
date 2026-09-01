export function RiskBadge({ level }: { level: string }) {
  const tone = level === "HIGH" ? "bg-[#151714] text-[#c8ff32]" : level === "MEDIUM" ? "bg-black/7 text-black" : "bg-[#dcecc3] text-[#263314]";
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-bold tracking-[.12em] ${tone}`}>{level}</span>;
}
