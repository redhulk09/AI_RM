"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "../lib/api";

export function DemoButton() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const seed = async () => {
    setBusy(true);
    setError("");
    try {
      await apiFetch("/demo/seed", { method: "POST" });
      router.push("/dashboard");
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load demo");
    } finally {
      setBusy(false);
    }
  };
  return (
    <span className="relative inline-flex items-center gap-2">
      <button onClick={seed} disabled={busy} className="rounded-full bg-[#c8ff32] px-4 py-2.5 text-sm font-bold text-black transition hover:-translate-y-0.5 disabled:opacity-50">{busy ? "Loading demo…" : "Load demo"}</button>
      {error && <span role="alert" className="absolute right-0 top-full mt-2 w-64 rounded-xl bg-black px-3 py-2 text-xs text-white shadow-xl">{error}</span>}
    </span>
  );
}
