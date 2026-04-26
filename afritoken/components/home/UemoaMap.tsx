"use client";

import { UEMOA_COUNTRIES } from "@/data/mockData";

export function UemoaMap() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="text-center mb-12">
          <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
            L'écosystème UEMOA
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl lg:text-5xl">
            8 pays, un agrément
          </h2>
          <p className="mt-4 text-neutral-light/60 max-w-2xl mx-auto">
            Un agrément AMF-UMOA donne accès aux 8 pays de la zone — soit plus
            de <span className="text-accent font-semibold">130 millions d'habitants</span>.
          </p>
        </div>

        <div className="card max-w-5xl mx-auto p-6 lg:p-10">
          <div className="grid lg:grid-cols-[1fr_320px] gap-8 items-center">
            <div className="relative aspect-[5/4] rounded-2xl bg-gradient-to-br from-primary/10 via-dark to-accent/5 border border-white/5 overflow-hidden">
              <svg
                viewBox="0 0 100 100"
                className="absolute inset-0 w-full h-full"
                preserveAspectRatio="none"
              >
                {/* simplified West Africa silhouette */}
                <path
                  d="M5 30 L20 25 L35 28 L50 24 L65 28 L80 30 L75 45 L80 55 L70 70 L55 78 L45 82 L35 80 L25 72 L15 65 L8 50 Z"
                  fill="rgba(27, 94, 32, 0.25)"
                  stroke="rgba(249, 168, 37, 0.4)"
                  strokeWidth="0.4"
                />
                {UEMOA_COUNTRIES.map((c, i) => (
                  <g key={c.code}>
                    <circle
                      cx={c.x}
                      cy={c.y}
                      r="1.6"
                      fill="#F9A825"
                      className="animate-pulse-slow"
                      style={{ animationDelay: `${i * 0.2}s` }}
                    />
                    <circle
                      cx={c.x}
                      cy={c.y}
                      r="3.5"
                      fill="rgba(249, 168, 37, 0.2)"
                      className="animate-pulse-slow"
                      style={{ animationDelay: `${i * 0.2}s` }}
                    />
                    <text
                      x={c.x + 3}
                      y={c.y + 1.2}
                      fill="rgba(232, 245, 233, 0.9)"
                      fontSize="2.4"
                      fontFamily="monospace"
                    >
                      {c.code}
                    </text>
                  </g>
                ))}
              </svg>
            </div>

            <div>
              <h3 className="font-display font-semibold text-lg mb-4">
                Pays couverts
              </h3>
              <ul className="space-y-2">
                {UEMOA_COUNTRIES.map((c) => (
                  <li
                    key={c.code}
                    className="flex items-center justify-between text-sm border-b border-white/5 pb-2"
                  >
                    <span className="flex items-center gap-2">
                      <span className="text-accent font-mono text-xs">{c.code}</span>
                      <span className="text-neutral-light/80">{c.name}</span>
                    </span>
                    <span className="text-neutral-light/40 text-xs">{c.capital}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
