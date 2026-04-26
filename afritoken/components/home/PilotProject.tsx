import Link from "next/link";
import {
  ArrowRight,
  Calendar,
  MapPin,
  TrendingUp,
  Users,
} from "lucide-react";
import { PILOT_PROJECT, formatFCFA } from "@/data/mockData";

export function PilotProject() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="text-center mb-12">
          <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
            Projet pilote
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl lg:text-5xl">
            Green Mobility
          </h2>
        </div>

        <div className="card-hover card relative overflow-hidden p-0 max-w-5xl mx-auto">
          <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-accent/10 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-64 h-64 rounded-full bg-primary/20 blur-3xl pointer-events-none" />
          <div className="relative grid lg:grid-cols-2 gap-0">
            <div className="p-8 lg:p-10 border-b lg:border-b-0 lg:border-r border-white/5">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-xl bg-gold-gradient flex items-center justify-center font-display font-bold text-dark text-xl shadow-glow">
                    GM
                  </div>
                  <div>
                    <h3 className="font-display font-bold text-2xl text-white">
                      {PILOT_PROJECT.shortName}
                    </h3>
                    <p className="flex items-center gap-1.5 text-sm text-neutral-light/60 mt-1">
                      <MapPin className="w-3.5 h-3.5" />
                      {PILOT_PROJECT.sector}
                    </p>
                  </div>
                </div>
                <span className="badge-success">
                  <span className="pulse-dot" />
                  {PILOT_PROJECT.status}
                </span>
              </div>

              <div className="space-y-3 mb-8">
                <div className="flex items-baseline justify-between">
                  <span className="text-xs uppercase tracking-wider text-neutral-light/50">
                    Montant levé
                  </span>
                  <span className="font-mono text-sm text-neutral-light/70">
                    {formatFCFA(PILOT_PROJECT.raised)} / {formatFCFA(PILOT_PROJECT.totalRaise)} FCFA
                  </span>
                </div>
                <div className="relative h-3 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className="absolute inset-y-0 left-0 bg-gold-gradient rounded-full"
                    style={{ width: `${PILOT_PROJECT.progressPercent}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-accent font-mono font-semibold">
                    {PILOT_PROJECT.progressPercent}% atteint
                  </span>
                  <span className="text-neutral-light/50">
                    {PILOT_PROJECT.daysLeft} jours restants
                  </span>
                </div>
              </div>

              <Link href="/investor" className="btn-accent w-full justify-center">
                Voir le projet
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="p-8 lg:p-10 grid grid-cols-2 gap-4 content-center bg-white/[0.02]">
              <Metric icon={<TrendingUp className="w-4 h-4" />} label="Rendement" value="2%" sub="par mois" />
              <Metric icon={<Calendar className="w-4 h-4" />} label="Durée" value="36" sub="mois" />
              <Metric icon={<Users className="w-4 h-4" />} label="Investisseurs" value={String(PILOT_PROJECT.investorsCurrent)} sub={`/ ${PILOT_PROJECT.investors} cible`} />
              <Metric icon={<TrendingUp className="w-4 h-4" />} label="Rendement annuel" value="24%" sub="équivalent" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Metric({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub: string }) {
  return (
    <div className="rounded-xl border border-white/5 p-4">
      <div className="flex items-center gap-2 text-accent text-xs uppercase tracking-wider mb-2">
        {icon}
        <span>{label}</span>
      </div>
      <div className="font-mono">
        <span className="font-display font-bold text-2xl text-white">{value}</span>
        <span className="text-xs text-neutral-light/50 ml-1.5">{sub}</span>
      </div>
    </div>
  );
}
