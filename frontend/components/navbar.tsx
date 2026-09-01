"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const links = [
  ["Dashboard", "/dashboard"],
  ["Transactions", "/transactions"],
  ["Analyze", "/analyze"],
  ["Model", "/model"],
  ["About", "/#about"],
] as const;

export function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  return (
    <header className="sticky top-0 z-50 border-b border-black/5 bg-[#f6f4ed]/72 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
        <Link href="/" onClick={() => setOpen(false)} className="flex items-center gap-3 text-sm font-bold tracking-tight">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-black text-[#c8ff32]">R</span>
          <span>RiskLens</span>
        </Link>
        <nav className="hidden items-center gap-7 md:flex">
          {links.map(([label, href]) => (
            <Link key={label} href={href} className={`text-sm transition ${pathname === href ? "font-semibold" : "text-black/48 hover:text-black"}`}>
              {label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <Link href="/dashboard" className="hidden rounded-full px-4 py-2 text-sm text-black/60 transition hover:bg-black/5 sm:inline-flex">Demo</Link>
          <Link href="/analyze" className="rounded-full bg-black px-5 py-2.5 text-sm font-semibold text-white transition hover:-translate-y-0.5">Get started</Link>
          <button aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen((value) => !value)} className="grid h-10 w-10 place-items-center rounded-full bg-black/5 md:hidden">
            <span className="text-lg">{open ? "×" : "☰"}</span>
          </button>
        </div>
      </div>
      {open && (
        <nav className="border-t border-black/5 px-5 py-4 md:hidden">
          <div className="mx-auto grid max-w-7xl gap-1">
            {links.map(([label, href]) => (
              <Link key={label} href={href} onClick={() => setOpen(false)} className="rounded-2xl px-4 py-3 text-sm font-semibold hover:bg-black/5">
                {label}
              </Link>
            ))}
          </div>
        </nav>
      )}
    </header>
  );
}
