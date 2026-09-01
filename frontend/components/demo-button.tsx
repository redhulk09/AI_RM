"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "../lib/api";

export function DemoButton() {
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  const seed = async () => { setBusy(true); try { await apiFetch("/demo/seed", { method: "POST" }); router.refresh(); window.location.reload(); } catch (e) { window.alert(e instanceof Error ? e.message : "Unable to load demo"); } finally { setBusy(false); } };
  return <button onClick={seed} disabled={busy} className="rounded-full bg-[#c8ff32] px-4 py-2.5 text-sm font-bold text-black transition hover:-translate-y-0.5 disabled:opacity-50">{busy ? "Loading demo…" : "Load demo"}</button>;
}
