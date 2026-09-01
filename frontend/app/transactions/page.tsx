"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { GlassCard } from "../../components/glass-card";
import { RiskBadge } from "../../components/risk-badge";
import { apiFetch, type TransactionSummary } from "../../lib/api";

export default function TransactionsPage() {
  const [rows, setRows] = useState<TransactionSummary[]>([]);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("ALL");
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<TransactionSummary[]>("/transactions?limit=100").then(setRows).catch((e) => setError(e.message)); }, []);
  const filtered = rows.filter((row) => (level === "ALL" || row.risk_level === level) && row.transaction_id.toLowerCase().includes(query.toLowerCase()));
  return <main className="mx-auto max-w-7xl px-5 pb-20 pt-14 lg:px-8"><div className="flex flex-wrap items-end justify-between gap-5"><div><p className="text-xs font-bold uppercase tracking-[.2em] text-black/38">Transaction register</p><h1 className="serif mt-2 text-6xl tracking-[-.05em]">Review the signal.</h1><p className="mt-4 max-w-xl text-sm leading-6 text-black/50">Search recent analyzed transactions and open a complete decision-support view. No card numbers, CVVs or OTPs are stored.</p></div><Link href="/analyze" className="rounded-full bg-black px-5 py-3 text-sm font-bold text-white">Analyze new</Link></div>{error && <div className="mt-6 rounded-2xl bg-black p-4 text-sm text-white">{error}</div>}<GlassCard className="mt-8"><div className="flex flex-wrap gap-3"><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search transaction ID" className="input max-w-sm"/><div className="flex rounded-full bg-black/5 p-1">{["ALL","HIGH","MEDIUM","LOW"].map((item) => <button key={item} onClick={() => setLevel(item)} className={`rounded-full px-3 py-2 text-xs font-bold ${level === item ? "bg-black text-white" : "text-black/45"}`}>{item}</button>)}</div></div><div className="mt-6 overflow-x-auto"><table className="min-w-full text-left text-sm"><thead><tr className="text-xs uppercase tracking-[.14em] text-black/35"><th className="px-3 py-3">Transaction</th><th className="px-3 py-3">Amount</th><th className="px-3 py-3">Risk</th><th className="px-3 py-3">Reason</th><th className="px-3 py-3">Review</th></tr></thead><tbody>{filtered.map((row) => <tr key={row.transaction_id} className="border-t border-black/6"><td className="px-3 py-4 font-semibold">{row.transaction_id}<span className="block text-xs font-normal text-black/40">{new Date(row.created_at).toLocaleString()}</span></td><td className="px-3 py-4">₹{row.amount.toLocaleString("en-IN")}</td><td className="px-3 py-4"><div className="flex items-center gap-2"><strong>{row.risk_score}</strong><RiskBadge level={row.risk_level}/></div></td><td className="max-w-md px-3 py-4 text-black/50">{row.reasons[0]}</td><td className="px-3 py-4"><Link href={`/transactions/${row.transaction_id}`} className="font-semibold underline underline-offset-4">Open</Link></td></tr>)}{filtered.length === 0 && <tr><td colSpan={5} className="px-3 py-10 text-center text-black/40">No transactions match this view.</td></tr>}</tbody></table></div></GlassCard></main>;
}
