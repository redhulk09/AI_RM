export function ConfusionMatrix({ matrix }: { matrix: number[][] }) {
  const [[tn, fp], [fn, tp]] = matrix;
  const cell = (value: number, label: string, strong = false) => <div className={`rounded-3xl p-6 ${strong ? "bg-black text-white" : "bg-black/4"}`}><div className="text-xs uppercase tracking-[.14em] text-black/38">{label}</div><div className={`mt-3 text-5xl font-semibold tracking-[-.05em] ${strong ? "text-[#c8ff32]" : ""}`}>{value.toLocaleString()}</div></div>;
  return <div><div className="mb-3 text-center text-xs font-bold uppercase tracking-[.15em] text-black/35">Predicted</div><div className="grid grid-cols-2 gap-3"><div className="text-center text-xs text-black/35">Legitimate</div><div className="text-center text-xs text-black/35">Fraud</div>{cell(tn, "True negative")}{cell(fp, "False positive")}{cell(fn, "False negative")}{cell(tp, "True positive", true)}</div></div>;
}
