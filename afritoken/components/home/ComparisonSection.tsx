import { Check, X } from "lucide-react";
import { COMPARISON_TABLE } from "@/data/mockData";

export function ComparisonSection() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="text-center mb-12">
          <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
            Pourquoi Afritoken
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl lg:text-5xl">
            Banque vs Afritoken
          </h2>
          <p className="mt-4 text-neutral-light/60 max-w-2xl mx-auto">
            Une alternative concrète au financement bancaire traditionnel,
            taillée pour les PME africaines.
          </p>
        </div>

        <div className="card max-w-4xl mx-auto p-0 overflow-hidden">
          <div className="grid grid-cols-3 gap-px bg-white/5">
            <div className="bg-dark px-6 py-4 text-xs uppercase tracking-[0.18em] text-neutral-light/50">
              Critère
            </div>
            <div className="bg-dark px-6 py-4 text-xs uppercase tracking-[0.18em] text-neutral-light/50 text-center">
              Banque
            </div>
            <div className="bg-dark px-6 py-4 text-xs uppercase tracking-[0.18em] text-accent text-center font-semibold">
              Afritoken
            </div>
            {COMPARISON_TABLE.map((row, i) => (
              <div key={i} className="contents">
                <div className="bg-dark/60 px-6 py-4 text-sm text-neutral-light/80 font-medium">
                  {row.criterion}
                </div>
                <div className="bg-dark/60 px-6 py-4 text-sm text-center flex items-center justify-center gap-2">
                  <span className="text-neutral-light/70 font-mono">{row.banque}</span>
                  <X className="w-4 h-4 text-danger" />
                </div>
                <div className="bg-accent/[0.04] px-6 py-4 text-sm text-center flex items-center justify-center gap-2">
                  <span className="text-accent font-mono font-semibold">{row.afritoken}</span>
                  <Check className="w-4 h-4 text-success" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
