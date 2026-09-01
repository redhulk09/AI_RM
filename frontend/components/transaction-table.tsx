import Link from "next/link";
import { RiskBadge } from "./risk-badge";
import type { TransactionSummary } from "../lib/api";

export function TransactionTable({ rows }: { rows: TransactionSummary[] }) {
  return <div className="overflow-x-auto"><table className="min-w-full text-left text-sm"><thead><tr className="text-xs uppercase tracking-[.14em] text-black/38"><th className="px-3 py-3">Transaction</th><th className="px-3 py-3">Amount</th><th className="px-3 py-3">Risk</th><th className="px-3 py-3">Signal</th><th className="px-3 py-3">Action</th></tr></thead><tbody>{rows.map((row) => <tr key={row.transaction_id} className="border-t border-black/6"><td className="px-3 py-4 font-semibold">{row.transaction_id}<span className="block text-xs font-normal text-black/40">{row.customer_id}</span></td><td className="px-3 py-4">₹{row.amount.toLocaleString("en-IN")}</td><td className="px-3 py-4"><div className="flex items-center gap-2"><span className="font-semibold">{row.risk_score}</span><RiskBadge level={row.risk_level} /></div></td><td className="max-w-xs px-3 py-4 text-black/55">{row.reasons?.[0] || "Multiple signals"}</td><td className="px-3 py-4"><Link href={`/transactions/${row.transaction_id}`} className="rounded-full bg-black px-3 py-2 text-xs font-semibold text-white transition hover:-translate-y-0.5">Review</Link></td></tr>)}</tbody></table></div>;
}
