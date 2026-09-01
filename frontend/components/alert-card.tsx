"use client";

import Link from "next/link";
import type { TransactionSummary } from "../lib/api";
import { GlassCard } from "./glass-card";
import { RiskBadge } from "./risk-badge";

export function AlertCard({ transaction }: { transaction?: TransactionSummary }) {
  if (!transaction) return <GlassCard className="bg-black text-white"><p className="text-xs uppercase tracking-[.18em] text-white/40">Risk alert</p><h2 className="serif mt-3 text-4xl">No high-risk payment in the current queue.</h2><Link href="/analyze" className="mt-8 inline-flex rounded-full bg-[#c8ff32] px-5 py-3 text-sm font-bold text-black">Analyze a payment</Link></GlassCard>;
  return <GlassCard className="bg-black text-white glow"><div className="flex items-center justify-between"><p className="text-xs uppercase tracking-[.18em] text-white/45">High risk detected</p><RiskBadge level="HIGH"/></div><div className="mt-8 flex items-end justify-between gap-6"><div><p className="text-4xl font-semibold tracking-[-.04em]">₹{transaction.amount.toLocaleString("en-IN")}</p><p className="mt-2 text-sm text-white/45">{transaction.transaction_id}</p></div><div className="text-right"><p className="text-xs uppercase tracking-[.16em] text-white/35">Risk score</p><p className="text-5xl font-semibold text-[#c8ff32]">{transaction.risk_score}</p></div></div><div className="mt-7 flex flex-wrap gap-2">{transaction.reasons.slice(0,3).map((reason) => <span key={reason} className="rounded-full bg-white/8 px-3 py-2 text-xs text-white/75">{reason.replace("Transaction ", "")}</span>)}</div><div className="mt-8 flex gap-2"><Link href={`/transactions/${transaction.transaction_id}`} className="rounded-full bg-[#c8ff32] px-4 py-2.5 text-sm font-bold text-black">Review transaction</Link><Link href={`/transactions/${transaction.transaction_id}`} className="rounded-full border border-white/12 px-4 py-2.5 text-sm">View details</Link></div></GlassCard>;
}
