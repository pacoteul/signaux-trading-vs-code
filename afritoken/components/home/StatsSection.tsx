"use client";

import { AnimatedCounter } from "@/components/ui/AnimatedCounter";
import { HERO_STATS } from "@/data/mockData";

export function StatsSection() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {HERO_STATS.map((s, i) => (
            <div
              key={i}
              className="card text-center group card-hover"
            >
              <div className="font-mono">
                <span className="stat-number gold-text">
                  {s.value === 300_000_000 ? (
                    <AnimatedCounter value={300} format={(n) => `${Math.round(n)}M`} />
                  ) : (
                    <AnimatedCounter value={s.value} />
                  )}
                </span>
                {s.suffix && (
                  <span className="ml-1 font-display text-xl text-accent/80">
                    {s.suffix}
                  </span>
                )}
              </div>
              <p className="mt-3 text-xs text-neutral-light/60 leading-relaxed">
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
