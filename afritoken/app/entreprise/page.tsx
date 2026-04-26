"use client";

import { useState } from "react";
import {
  Activity,
  Calendar,
  CheckCircle2,
  Coins,
  Radio,
  Send,
  Upload,
  Users,
} from "lucide-react";
import {
  COMPANY,
  COMPANY_IOT,
  COMPANY_REVENUE_HISTORY,
  PILOT_PROJECT,
  formatFCFA,
} from "@/data/mockData";
import { FundUsagePie } from "@/components/charts/FundUsagePie";
import { Footer } from "@/components/navigation/Footer";

export default function EntreprisePage() {
  const [revenue, setRevenue] = useState("");
  const [submitted, setSubmitted] = useState(false);

  return (
    <>
      <section className="px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
        <div className="container-x">
          {/* Header */}
          <div className="flex items-start justify-between flex-wrap gap-4 mb-10">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-accent mb-1">
                Espace entreprise
              </p>
              <h1 className="font-display font-bold text-3xl lg:text-4xl">
                Tableau de bord {COMPANY.shortName}
              </h1>
              <p className="text-neutral-light/60 mt-1">
                Dirigeant : {COMPANY.director} · NINEA {COMPANY.ninea} · {COMPANY.sector}
              </p>
            </div>
            <span className="badge-success">
              <span className="pulse-dot" />
              Collecte active
            </span>
          </div>

          {/* KPIs */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
            <Kpi
              icon={<Coins className="w-4 h-4" />}
              label="Montant levé"
              value={`${formatFCFA(PILOT_PROJECT.raised, { compact: true })} / ${formatFCFA(PILOT_PROJECT.totalRaise, { compact: true })} FCFA`}
              sub={`${PILOT_PROJECT.progressPercent}% atteint`}
              accent
            />
            <Kpi
              icon={<Users className="w-4 h-4" />}
              label="Investisseurs"
              value={`${PILOT_PROJECT.investorsCurrent} / ${PILOT_PROJECT.investors}`}
              sub="objectif"
            />
            <Kpi
              icon={<Calendar className="w-4 h-4" />}
              label="Jours restants"
              value={String(PILOT_PROJECT.daysLeft)}
              sub="avant clôture"
            />
            <Kpi
              icon={<Send className="w-4 h-4" />}
              label="Prochain versement"
              value="01/05/2026"
              sub={`${formatFCFA(PILOT_PROJECT.monthlyDividends)} FCFA`}
            />
          </div>

          {/* Progress */}
          <div className="card p-8 mb-10 relative overflow-hidden">
            <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-accent/10 blur-3xl pointer-events-none" />
            <div className="relative">
              <div className="flex items-baseline justify-between flex-wrap gap-2 mb-3">
                <h2 className="font-display font-bold text-2xl">Progression de la levée</h2>
                <span className="font-mono text-accent font-bold text-2xl">
                  {PILOT_PROJECT.progressPercent}%
                </span>
              </div>
              <div className="relative h-4 rounded-full bg-white/5 overflow-hidden mb-3">
                <div
                  className="absolute inset-y-0 left-0 bg-gold-gradient rounded-full"
                  style={{ width: `${PILOT_PROJECT.progressPercent}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-neutral-light/70 font-mono">
                  {formatFCFA(PILOT_PROJECT.raised)} / {formatFCFA(PILOT_PROJECT.totalRaise)} FCFA
                </span>
                <span className="text-neutral-light/50">
                  Il manque{" "}
                  <span className="text-accent font-semibold">
                    {formatFCFA(PILOT_PROJECT.totalRaise - PILOT_PROJECT.raised)} FCFA
                  </span>{" "}
                  pour atteindre l'objectif
                </span>
              </div>
            </div>
          </div>

          {/* Déclaration revenus */}
          <div className="grid lg:grid-cols-3 gap-6 mb-10">
            <div className="lg:col-span-2 card p-6 lg:p-8">
              <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                Déclaration mensuelle
              </p>
              <h2 className="font-display font-bold text-2xl mb-1">
                Revenus — Avril 2026
              </h2>
              <p className="text-sm text-neutral-light/60 mb-6">
                Soumettez vos revenus du mois pour validation par l'auditeur.
              </p>

              {submitted ? (
                <div className="rounded-2xl border border-success/30 bg-success/5 p-6 flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-display font-semibold text-white mb-1">
                      Déclaration soumise
                    </p>
                    <p className="text-sm text-neutral-light/70">
                      Votre déclaration est en cours d'analyse par le cabinet d'audit.
                      Vous serez notifié sous 48h.
                    </p>
                  </div>
                </div>
              ) : (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    setSubmitted(true);
                  }}
                  className="space-y-4"
                >
                  <div>
                    <label className="label">Mois concerné</label>
                    <input className="input" defaultValue="Avril 2026" readOnly />
                  </div>
                  <div>
                    <label className="label">Revenus bruts déclarés (FCFA)</label>
                    <input
                      className="input font-mono"
                      type="number"
                      placeholder="71 500 000"
                      value={revenue}
                      onChange={(e) => setRevenue(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="label">Relevé bancaire (PDF)</label>
                    <label className="flex items-center justify-center gap-2 input cursor-pointer hover:border-accent/40">
                      <Upload className="w-4 h-4" />
                      <span className="text-sm text-neutral-light/60">
                        Cliquez pour téléverser
                      </span>
                      <input type="file" className="hidden" accept=".pdf" />
                    </label>
                  </div>
                  <button type="submit" className="btn-accent w-full justify-center">
                    <Send className="w-4 h-4" />
                    Soumettre la déclaration
                  </button>
                </form>
              )}
            </div>

            <div className="card p-6 lg:p-8 relative overflow-hidden">
              <div className="absolute -top-24 -right-24 w-48 h-48 rounded-full bg-accent/15 blur-3xl pointer-events-none" />
              <div className="relative">
                <div className="flex items-center gap-2 mb-4">
                  <Radio className="w-4 h-4 text-accent animate-pulse" />
                  <p className="text-xs uppercase tracking-[0.18em] text-accent">
                    Données IoT en direct
                  </p>
                </div>
                <h3 className="font-display font-semibold text-lg mb-5">
                  Capteurs véhicules
                </h3>
                <div className="space-y-4">
                  <IotRow label="Voitures actives" value={String(COMPANY_IOT.activeVehicles)} unit="/ 55" />
                  <IotRow label="Trajets détectés" value={COMPANY_IOT.detectedTrips.toLocaleString("fr-FR")} unit="trajets" />
                  <div className="rounded-xl border border-accent/30 bg-accent/[0.04] p-4">
                    <p className="text-[10px] uppercase tracking-wider text-neutral-light/50 mb-1">
                      Revenus IoT estimés
                    </p>
                    <p className="font-mono font-bold gold-text text-2xl">
                      {formatFCFA(COMPANY_IOT.estimatedRevenue)}
                    </p>
                    <p className="text-xs text-neutral-light/50 mt-1">FCFA / mois</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Historique */}
          <div className="card p-6 lg:p-8 mb-10">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                  Historique
                </p>
                <h2 className="font-display font-bold text-2xl">
                  Versements et déclarations
                </h2>
              </div>
              <span className="badge-success">
                <Activity className="w-3.5 h-3.5" />
                Écart 0% — 4 mois consécutifs
              </span>
            </div>

            <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
              <table className="w-full text-sm min-w-[760px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                    <th className="font-medium pb-3">Mois</th>
                    <th className="font-medium pb-3 text-right">Revenus déclarés</th>
                    <th className="font-medium pb-3 text-right">Revenus IoT</th>
                    <th className="font-medium pb-3 text-right">Écart</th>
                    <th className="font-medium pb-3 text-right">Dividendes versés</th>
                    <th className="font-medium pb-3 text-right">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {COMPANY_REVENUE_HISTORY.map((r, i) => (
                    <tr key={i}>
                      <td className="py-3 font-medium text-neutral-light/90">{r.month}</td>
                      <td className="py-3 text-right font-mono">
                        {formatFCFA(r.declared, { compact: true })} FCFA
                      </td>
                      <td className="py-3 text-right font-mono">
                        {formatFCFA(r.iot, { compact: true })} FCFA
                      </td>
                      <td className="py-3 text-right font-mono text-success">{r.gap}%</td>
                      <td className="py-3 text-right font-mono text-accent">
                        {formatFCFA(r.dividends, { compact: true })} FCFA
                      </td>
                      <td className="py-3 text-right">
                        {r.status === "Versé" ? (
                          <span className="badge-success">Versé</span>
                        ) : (
                          <span className="badge-warning">En cours</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Plan d'utilisation */}
          <div className="card p-6 lg:p-8">
            <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
              Plan d'utilisation
            </p>
            <h2 className="font-display font-bold text-2xl mb-6">
              Allocation des fonds levés
            </h2>
            <FundUsagePie />
          </div>
        </div>
      </section>
      <Footer />
    </>
  );
}

function Kpi({
  icon,
  label,
  value,
  sub,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub: string;
  accent?: boolean;
}) {
  return (
    <div className={`card p-5 ${accent ? "border-accent/30 bg-accent/[0.04]" : ""}`}>
      <div className="flex items-center gap-2 text-accent text-[10px] uppercase tracking-[0.18em] mb-3">
        {icon}
        <span>{label}</span>
      </div>
      <p className={`font-mono font-bold text-base ${accent ? "gold-text" : "text-white"}`}>
        {value}
      </p>
      <p className="text-xs text-neutral-light/55 mt-1.5">{sub}</p>
    </div>
  );
}

function IotRow({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="flex items-baseline justify-between border-b border-white/5 pb-3">
      <span className="text-sm text-neutral-light/70">{label}</span>
      <span className="font-mono">
        <span className="font-bold text-white text-lg">{value}</span>
        <span className="text-xs text-neutral-light/50 ml-1.5">{unit}</span>
      </span>
    </div>
  );
}
