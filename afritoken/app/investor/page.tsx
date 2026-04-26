import {
  Calendar,
  CheckCircle2,
  Coins,
  Download,
  FileCheck,
  TrendingUp,
  Wallet,
} from "lucide-react";
import {
  INVESTOR,
  INVESTOR_DIVIDEND_HISTORY,
  INVESTOR_DIVIDEND_TIMELINE,
  INVESTOR_TOKENS,
  PILOT_PROJECT,
  SECONDARY_MARKET_OFFERS,
  formatFCFA,
} from "@/data/mockData";
import { InvestorTimelineChart } from "@/components/charts/InvestorTimelineChart";
import { Footer } from "@/components/navigation/Footer";

export const metadata = {
  title: "Espace Investisseur — Afritoken",
  description: "Tableau de bord investisseur — suivi des dividendes et tokens.",
};

export default function InvestorPage() {
  const today = new Date().toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <>
      <section className="px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
        <div className="container-x">
          {/* Header */}
          <div className="flex items-start justify-between flex-wrap gap-4 mb-10">
            <div>
              <h1 className="font-display font-bold text-3xl lg:text-4xl">
                Bonjour, {INVESTOR.firstName} <span className="inline-block animate-float">👋</span>
              </h1>
              <p className="text-neutral-light/60 mt-1 capitalize">{today}</p>
            </div>
            <span className="badge-success">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Identité vérifiée
            </span>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
            <Kpi
              icon={<Wallet className="w-4 h-4" />}
              label="Capital investi"
              value={`${formatFCFA(INVESTOR.capitalInvested)} FCFA`}
              sub={`Remboursement en janvier 2029`}
              accent
            />
            <Kpi
              icon={<Coins className="w-4 h-4" />}
              label="Dividendes ce mois"
              value={`${formatFCFA(INVESTOR.monthlyDividend)} FCFA`}
              sub="Versé le 01/04/2026"
              ok
            />
            <Kpi
              icon={<TrendingUp className="w-4 h-4" />}
              label="Total reçu"
              value={`${formatFCFA(INVESTOR.totalReceived)} FCFA`}
              sub="+6% du capital initial"
            />
            <Kpi
              icon={<Calendar className="w-4 h-4" />}
              label="Gain projeté total"
              value={`${formatFCFA(INVESTOR.projectedTotalGain)} FCFA`}
              sub="Sur 36 mois"
            />
          </div>

          {/* Mes Tokens */}
          <div className="card p-6 lg:p-8 mb-10">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                  Portefeuille
                </p>
                <h2 className="font-display font-bold text-2xl">Mes tokens</h2>
              </div>
            </div>
            <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
              <table className="w-full text-sm min-w-[700px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                    <th className="font-medium pb-3">Projet</th>
                    <th className="font-medium pb-3 text-right">Tokens</th>
                    <th className="font-medium pb-3 text-right">Capital</th>
                    <th className="font-medium pb-3 text-right">Rendement</th>
                    <th className="font-medium pb-3">Prochain dividende</th>
                    <th className="font-medium pb-3 text-right">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {INVESTOR_TOKENS.map((t, i) => (
                    <tr key={i}>
                      <td className="py-3 font-medium text-neutral-light/90">{t.project}</td>
                      <td className="py-3 text-right font-mono text-accent">{t.tokens}</td>
                      <td className="py-3 text-right font-mono">{formatFCFA(t.capital)} FCFA</td>
                      <td className="py-3 text-right font-mono text-accent">{t.yieldRate}</td>
                      <td className="py-3 font-mono text-neutral-light/70">{t.nextDividend}</td>
                      <td className="py-3 text-right">
                        <span className="badge-success">
                          <span className="pulse-dot" />
                          {t.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Historique + Graphique */}
          <div className="grid lg:grid-cols-5 gap-6 mb-10">
            <div className="lg:col-span-3 card p-6 lg:p-8">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                    Évolution
                  </p>
                  <h2 className="font-display font-bold text-2xl">Dividendes cumulés</h2>
                </div>
                <span className="badge-warning">36 mois</span>
              </div>
              <InvestorTimelineChart data={INVESTOR_DIVIDEND_TIMELINE} />
            </div>
            <div className="lg:col-span-2 card p-6 lg:p-8">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                    Historique
                  </p>
                  <h2 className="font-display font-bold text-2xl">Dividendes reçus</h2>
                </div>
              </div>
              <ul className="space-y-3">
                {INVESTOR_DIVIDEND_HISTORY.map((d, i) => (
                  <li key={i} className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm text-neutral-light/85 font-medium">{d.date}</span>
                      <span className="badge-success">{d.status}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-neutral-light/60">{d.project}</span>
                      <span className="font-mono text-accent font-bold">
                        +{formatFCFA(d.amount)} FCFA
                      </span>
                    </div>
                    <p className="font-mono text-[10px] text-neutral-light/40 mt-1">{d.txn}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Audit */}
          <div className="card p-6 lg:p-8 mb-10 relative overflow-hidden">
            <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-success/10 blur-3xl pointer-events-none" />
            <div className="relative">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                    Audit mensuel
                  </p>
                  <h2 className="font-display font-bold text-2xl">
                    Rapport Avril 2026 — Certifié
                  </h2>
                </div>
                <button className="btn-outline text-sm">
                  <Download className="w-4 h-4" />
                  Télécharger le PDF
                </button>
              </div>
              <ul className="grid sm:grid-cols-2 gap-3">
                <AuditRow ok>Revenus Green Mobility : <span className="font-mono">{formatFCFA(PILOT_PROJECT.monthlyGrossRevenue)} FCFA</span></AuditRow>
                <AuditRow ok>Vérification IoT : Conforme</AuditRow>
                <AuditRow ok>Distribution effectuée : <span className="font-mono">{formatFCFA(PILOT_PROJECT.monthlyDividends)} FCFA</span> ({PILOT_PROJECT.investors} investisseurs)</AuditRow>
                <AuditRow ok>Auditeur : <span className="italic">Cabinet Audit Sénégal</span></AuditRow>
              </ul>
            </div>
          </div>

          {/* Marché secondaire */}
          <div className="card p-6 lg:p-8">
            <div className="flex items-start justify-between mb-6 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                  Marché secondaire
                </p>
                <h2 className="font-display font-bold text-2xl">Offres disponibles</h2>
                <p className="text-sm text-neutral-light/60 mt-1">
                  Vous pouvez revendre vos tokens à d'autres investisseurs.
                </p>
              </div>
              <button className="btn-ghost text-sm" disabled>
                Vendre mes tokens (V2)
              </button>
            </div>

            <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
              <table className="w-full text-sm min-w-[600px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                    <th className="font-medium pb-3">Vendeur</th>
                    <th className="font-medium pb-3">Projet</th>
                    <th className="font-medium pb-3 text-right">Tokens</th>
                    <th className="font-medium pb-3 text-right">Prix unitaire</th>
                    <th className="font-medium pb-3 text-right">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {SECONDARY_MARKET_OFFERS.map((o, i) => (
                    <tr key={i}>
                      <td className="py-3 text-neutral-light/85">{o.seller}</td>
                      <td className="py-3 text-neutral-light/70">{o.project}</td>
                      <td className="py-3 text-right font-mono text-accent">{o.tokens}</td>
                      <td className="py-3 text-right font-mono">{formatFCFA(o.price)} FCFA</td>
                      <td className="py-3 text-right font-mono">{formatFCFA(o.total)} FCFA</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
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
  ok,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub: string;
  accent?: boolean;
  ok?: boolean;
}) {
  return (
    <div className={`card p-6 ${accent ? "border-accent/30 bg-accent/[0.04]" : ""}`}>
      <div className="flex items-center gap-2 text-accent text-[10px] uppercase tracking-[0.18em] mb-3">
        {icon}
        <span>{label}</span>
      </div>
      <p className={`font-mono font-bold text-2xl ${accent ? "gold-text" : "text-white"}`}>
        {value}
      </p>
      <p className="text-xs text-neutral-light/55 mt-2 flex items-center gap-1.5">
        {ok && <CheckCircle2 className="w-3 h-3 text-success" />}
        {sub}
      </p>
    </div>
  );
}

function AuditRow({ children, ok }: { children: React.ReactNode; ok?: boolean }) {
  return (
    <li className="flex items-start gap-2 text-sm rounded-xl bg-white/[0.02] border border-white/5 p-3">
      {ok && <FileCheck className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />}
      <span className="text-neutral-light/85">{children}</span>
    </li>
  );
}
