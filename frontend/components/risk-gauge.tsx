export function RiskGauge({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 76;
  const circumference = Math.PI * radius;
  const dash = (clamped / 100) * circumference;
  const level = clamped >= 70 ? "HIGH RISK" : clamped >= 40 ? "MEDIUM RISK" : "LOW RISK";
  return <div className="relative mx-auto h-44 w-72"><svg viewBox="0 0 180 100" className="h-full w-full"><path d="M 14 90 A 76 76 0 0 1 166 90" fill="none" stroke="rgba(16,18,15,.08)" strokeWidth="12" strokeLinecap="round" /><path d="M 14 90 A 76 76 0 0 1 166 90" fill="none" stroke="#c8ff32" strokeWidth="12" strokeLinecap="round" strokeDasharray={`${dash} ${circumference}`} /></svg><div className="absolute inset-x-0 bottom-2 text-center"><div className="text-5xl font-semibold tracking-[-.06em]">{clamped}</div><div className="mt-1 text-xs font-bold tracking-[.16em] text-black/45">{level}</div></div></div>;
}
