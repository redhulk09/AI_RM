import Link from "next/link";

export default function Home() {
  return (
    <main className="overflow-hidden">
      <section className="relative mx-auto max-w-7xl px-5 pb-24 pt-16 lg:px-8 lg:pt-24">
        <div className="hero-orb left-[8%] top-20 h-40 w-40 bg-[#c8ff32]/55" />
        <div className="hero-orb right-[8%] top-32 h-64 w-64 bg-white/80" />
        <div className="relative grid items-center gap-14 lg:grid-cols-[1.05fr_.95fr]">
          <div className="fade-up max-w-3xl">
            <div className="mb-7 inline-flex rounded-full border border-black/8 bg-white/45 px-4 py-2 text-xs font-semibold tracking-[.18em] text-black/52 backdrop-blur">
              DEFENSE-ONLY AI RISK INTELLIGENCE
            </div>
            <h1 className="serif text-[clamp(4rem,8vw,8.5rem)] leading-[.84] tracking-[-.07em]">
              Stop fraud<br /><span className="italic">before</span> it becomes a loss.
            </h1>
            <p className="mt-8 max-w-xl text-lg leading-8 text-black/52">
              AI-powered transaction risk intelligence that helps merchants detect suspicious payments before they become costly losses.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link href="/analyze" className="rounded-full bg-black px-6 py-3.5 text-sm font-semibold text-white transition hover:-translate-y-1">Analyze transactions</Link>
              <Link href="/dashboard" className="rounded-full bg-white/65 px-6 py-3.5 text-sm font-semibold text-black transition hover:bg-white">View live demo</Link>
            </div>
            <div id="about" className="mt-14 grid max-w-2xl grid-cols-3 gap-7 border-t border-black/8 pt-7 text-xs text-black/45">
              <div><strong className="block text-2xl text-black">Synthetic</strong>demo transactions</div>
              <div><strong className="block text-2xl text-black">Held-out</strong>evaluation</div>
              <div><strong className="block text-2xl text-black">0</strong>payment credentials stored</div>
            </div>
          </div>
          <div className="relative min-h-[520px]">
            <div className="absolute inset-0 grid-lines rounded-[40px] opacity-50" />
            <div className="absolute inset-[9%] rounded-[36px] bg-[#10120f] shadow-2xl shadow-black/20" />
            <div className="float absolute left-[9%] top-[13%] w-[72%] rounded-[28px] border border-white/10 bg-white/8 p-5 text-white backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-[.18em] text-white/45">Demo risk score</span>
                <span className="rounded-full bg-[#c8ff32] px-2.5 py-1 text-[10px] font-black text-black">HIGH</span>
              </div>
              <div className="mt-8 text-7xl font-semibold tracking-[-.06em]">87<span className="text-3xl text-white/25"> / 100</span></div>
              <div className="mt-9 h-2 rounded-full bg-white/8"><div className="h-full w-[87%] rounded-full bg-[#c8ff32]" /></div>
            </div>
            <div className="absolute right-[2%] top-[43%] w-[54%] rounded-[28px] border border-black/8 bg-white/78 p-5 backdrop-blur-xl shadow-xl">
              <div className="text-xs uppercase tracking-[.18em] text-black/40">Demo transaction</div>
              <div className="mt-3 text-4xl font-semibold tracking-[-.04em]">₹42,850</div>
              <div className="mt-5 grid grid-cols-3 gap-2 text-xs"><span className="rounded-full bg-black/5 px-3 py-2">New device</span><span className="rounded-full bg-black/5 px-3 py-2">High velocity</span><span className="rounded-full bg-[#c8ff32] px-3 py-2">Unusual amount</span></div>
            </div>
            <div className="absolute bottom-[7%] left-[4%] w-[65%] rounded-[28px] border border-white/10 bg-white/6 p-5 text-white backdrop-blur-xl shadow-2xl">
              <div className="text-xs uppercase tracking-[.18em] text-white/45">Recommended action</div>
              <div className="mt-3 text-xl font-semibold">Review transaction</div>
              <div className="mt-2 text-sm text-white/45">Decision support, not automatic rejection.</div>
            </div>
          </div>
        </div>
      </section>
      <section className="border-y border-black/6 bg-white/35 py-7">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-5 px-5 text-xs uppercase tracking-[.16em] text-black/38 lg:px-8">
          <span>Razorpay Hackathon Track</span>
          <span>Fraud · Returns · Chargebacks</span>
          <span>Synthetic demo data</span>
          <span>Held-out evaluation</span>
        </div>
      </section>
    </main>
  );
}
