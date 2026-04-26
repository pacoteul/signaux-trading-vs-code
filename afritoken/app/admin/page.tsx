import {
  Activity,
  Building2,
  CheckCircle2,
  FileText,
  Lock,
  Receipt,
  ShieldCheck,
  TrendingUp,
  Users,
  Wallet,
} from "lucide-react";
import {
  ADMIN_KPIS,
  AUDIT_HISTORY,
  COMPANIES_PIPELINE,
  ESCROW_ACCOUNT,
  KYC_RECENT,
  KYC_STATS,
  RECENT_TRANSACTIONS,
  TOTAL_TRANSACTIONS,
  formatFCFA,
} from "@/data/mockData";
import { FraudSimulator } from "@/components/admin/FraudSimulator";
import { Footer } from "@/components/navigation/Footer";

export const metadata = {
  title: "Dashboard Admin — Afritoken",
  description: "Console de pilotage pour démonstration BCEAO.",
};

export default function AdminPage() {
  return (
    <>
      <section className="px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
        <div className="container-x">
          {/* Header */}
          <div className="flex items-start justify-between flex-wrap gap-4 mb-10">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-accent mb-2">
                Console administrateur
              </p>
              <h1 className="font-display font-bold text-3xl lg:text-4xl">
                Dashboard Administrateur
              </h1>
              <p className="text-neutral-light/60 mt-2">
                Vue d'ensemble — pilotage et conformité
              </p>
            </div>
            <span className="badge-warning">
              <ShieldCheck className="w-3.5 h-3.5" />
              Mode Démo — Données simulées
            </span>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 mb-10">
            <KpiCard icon={<Wallet className="w-4 h-4" />} label="Total AUM" value={`${formatFCFA(ADMIN_KPIS.aum, { compact: true })} FCFA`} accent />
            <KpiCard icon={<Users className="w-4 h-4" />} label="Investisseurs actifs" value={ADMIN_KPIS.activeInvestors.toString()} />
            <KpiCard icon={<Building2 className="w-4 h-4" />} label="Entreprises actives" value={ADMIN_KPIS.activeCompanies.toString()} />
            <KpiCard icon={<Activity className="w-4 h-4" />} label="Distributions" value={`${ADMIN_KPIS.distributionsCount} mois`} sub="Jan, Fév, Mars 26" />
            <KpiCard icon={<Receipt className="w-4 h-4" />} label="Total distribué" value={`${formatFCFA(ADMIN_KPIS.totalDistributed, { compact: true })} FCFA`} />
            <KpiCard icon={<TrendingUp className="w-4 h-4" />} label="Revenus Afritoken" value={`${formatFCFA(ADMIN_KPIS.afritokenRevenue, { compact: true })} FCFA`} />
          </div>

          {/* Traçabilité */}
          <div className="card p-6 lg:p-8 mb-10">
            <div className="flex items-start justify-between mb-6 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                  Traçabilité des transactions
                </p>
                <h2 className="font-display font-bold text-2xl">
                  Chaque franc est traçable — En temps réel
                </h2>
              </div>
              <span className="badge-success">
                <span className="pulse-dot" />
                Stellar Network
              </span>
            </div>

            <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
              <table className="w-full text-sm min-w-[720px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                    <th className="font-medium pb-3">Date / Heure</th>
                    <th className="font-medium pb-3">Investisseur</th>
                    <th className="font-medium pb-3">Type</th>
                    <th className="font-medium pb-3 text-right">Montant</th>
                    <th className="font-medium pb-3">Hash blockchain</th>
                    <th className="font-medium pb-3 text-right">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {RECENT_TRANSACTIONS.map((tx, i) => (
                    <tr key={i} className="hover:bg-white/[0.02]">
                      <td className="py-3 font-mono text-xs text-neutral-light/70">{tx.date}</td>
                      <td className="py-3 text-neutral-light/85">{tx.investor}</td>
                      <td className="py-3 text-neutral-light/70">{tx.type}</td>
                      <td className="py-3 text-right font-mono text-accent font-semibold">
                        {formatFCFA(tx.amount)} FCFA
                      </td>
                      <td className="py-3 font-mono text-xs text-neutral-light/50">{tx.hash}</td>
                      <td className="py-3 text-right">
                        <CheckCircle2 className="inline w-4 h-4 text-success" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-6 text-center">
              <button type="button" className="btn-ghost text-sm">
                Voir toutes les transactions ({TOTAL_TRANSACTIONS.toLocaleString("fr-FR")})
              </button>
            </div>
          </div>

          {/* Anti-fraud */}
          <div className="mb-10">
            <FraudSimulator />
          </div>

          {/* AML/CFT */}
          <div className="grid lg:grid-cols-3 gap-6 mb-10">
            <div className="lg:col-span-1 card p-8">
              <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                Rapport AML / CFT
              </p>
              <h2 className="font-display font-bold text-2xl mb-1">
                Vérification d'identité
              </h2>
              <p className="text-sm text-neutral-light/60 mb-6">
                de tous les investisseurs
              </p>

              <ul className="space-y-3">
                <AmlRow label="Investisseurs vérifiés KYC" value={`${KYC_STATS.verified}`} ok />
                <AmlRow label="Transactions suspectes détectées" value={String(KYC_STATS.suspicious)} ok />
                <AmlRow label="Investisseurs sur liste noire" value={String(KYC_STATS.blacklisted)} ok />
                <AmlRow label="Conformité AML" value={`${KYC_STATS.amlCompliance}%`} ok />
              </ul>
            </div>

            <div className="lg:col-span-2 card p-6 lg:p-8">
              <h3 className="font-display font-semibold text-lg mb-4">
                5 derniers KYC validés
              </h3>
              <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
                <table className="w-full text-sm min-w-[480px]">
                  <thead>
                    <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                      <th className="font-medium pb-3">Investisseur</th>
                      <th className="font-medium pb-3">Date</th>
                      <th className="font-medium pb-3">Document</th>
                      <th className="font-medium pb-3 text-right">Statut</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {KYC_RECENT.map((k, i) => (
                      <tr key={i}>
                        <td className="py-3 text-neutral-light/85">{k.investor}</td>
                        <td className="py-3 font-mono text-xs text-neutral-light/60">{k.date}</td>
                        <td className="py-3 text-neutral-light/70">{k.document}</td>
                        <td className="py-3 text-right">
                          <span className="badge-success">{k.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Escrow */}
          <div className="card p-8 mb-10 relative overflow-hidden">
            <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-accent/10 blur-3xl pointer-events-none" />
            <div className="relative">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                    Compte Escrow — État en temps réel
                  </p>
                  <h2 className="font-display font-bold text-2xl">
                    Banque partenaire :{" "}
                    <span className="gold-text">{ESCROW_ACCOUNT.bank}</span>
                  </h2>
                </div>
                <span className="badge-success">
                  <Lock className="w-3.5 h-3.5" />
                  Double signature requise
                </span>
              </div>

              <div className="rounded-2xl border border-accent/20 bg-accent/[0.04] p-6 mb-5">
                <p className="text-xs uppercase tracking-[0.18em] text-neutral-light/50 mb-1">
                  Solde total
                </p>
                <p className="font-mono font-bold gold-text text-4xl">
                  {formatFCFA(ESCROW_ACCOUNT.totalBalance)} <span className="text-lg text-accent/60 font-display">FCFA</span>
                </p>
              </div>

              <div className="grid sm:grid-cols-3 gap-3 mb-5">
                <EscrowRow label="Disponible Green Mobility" value={ESCROW_ACCOUNT.availableForCompany} />
                <EscrowRow label="Réserve remboursement" value={ESCROW_ACCOUNT.reimbursementReserve} sub="3 mois" locked />
                <EscrowRow label="Réserve d'urgence" value={ESCROW_ACCOUNT.emergencyReserve} locked />
              </div>

              <div className="grid sm:grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl bg-white/[0.02] border border-white/5 p-4">
                  <p className="text-[10px] uppercase tracking-wider text-neutral-light/50 mb-1">
                    Dernier mouvement
                  </p>
                  <p className="text-neutral-light/85">
                    Distribution {ESCROW_ACCOUNT.lastMovement.date} —{" "}
                    <span className="font-mono text-accent">{formatFCFA(ESCROW_ACCOUNT.lastMovement.amount)} FCFA</span>
                  </p>
                </div>
                <div className="rounded-xl bg-white/[0.02] border border-white/5 p-4">
                  <p className="text-[10px] uppercase tracking-wider text-neutral-light/50 mb-1">
                    Prochaine distribution
                  </p>
                  <p className="text-neutral-light/85">{ESCROW_ACCOUNT.nextDistribution}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Audit */}
          <div className="card p-6 lg:p-8 mb-10">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                  Audit mensuel — Historique
                </p>
                <h2 className="font-display font-bold text-2xl">
                  Certifications indépendantes
                </h2>
              </div>
            </div>

            <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
              <table className="w-full text-sm min-w-[700px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                    <th className="font-medium pb-3">Mois</th>
                    <th className="font-medium pb-3">Auditeur</th>
                    <th className="font-medium pb-3 text-right">Revenus vérifiés</th>
                    <th className="font-medium pb-3 text-right">Écart</th>
                    <th className="font-medium pb-3 text-center">Rapport</th>
                    <th className="font-medium pb-3 text-right">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {AUDIT_HISTORY.map((a, i) => (
                    <tr key={i}>
                      <td className="py-3 font-medium text-neutral-light/90">{a.month}</td>
                      <td className="py-3 text-neutral-light/70">{a.auditor}</td>
                      <td className="py-3 text-right font-mono text-accent">
                        {formatFCFA(a.revenue)} FCFA
                      </td>
                      <td className="py-3 text-right font-mono text-success">{a.gap}%</td>
                      <td className="py-3 text-center">
                        <button className="inline-flex items-center gap-1 text-accent text-xs hover:underline">
                          <FileText className="w-3.5 h-3.5" />
                          PDF
                        </button>
                      </td>
                      <td className="py-3 text-right">
                        {a.status === "Certifié" ? (
                          <span className="badge-success">{a.status}</span>
                        ) : (
                          <span className="badge-warning">{a.status}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pipeline candidatures */}
          <div className="card p-6 lg:p-8">
            <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                  Pipeline candidatures
                </p>
                <h2 className="font-display font-bold text-2xl">
                  Validation des entreprises
                </h2>
              </div>
              <div className="flex gap-2 text-xs">
                <span className="badge-warning">3 en analyse</span>
                <span className="badge-success">1 acceptée</span>
                <span className="badge-danger">2 rejetées</span>
              </div>
            </div>

            <div className="overflow-x-auto -mx-6 lg:-mx-8 px-6 lg:px-8">
              <table className="w-full text-sm min-w-[640px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-neutral-light/50 border-b border-white/5">
                    <th className="font-medium pb-3">Entreprise</th>
                    <th className="font-medium pb-3">Secteur</th>
                    <th className="font-medium pb-3 text-right">Score</th>
                    <th className="font-medium pb-3 text-center">Statut</th>
                    <th className="font-medium pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {COMPANIES_PIPELINE.map((c, i) => (
                    <tr key={i}>
                      <td className="py-3 font-medium text-neutral-light/90">{c.name}</td>
                      <td className="py-3 text-neutral-light/70">{c.sector}</td>
                      <td className="py-3 text-right font-mono text-accent">{c.score}/100</td>
                      <td className="py-3 text-center">
                        {c.status === "active" && <span className="badge-success">Active</span>}
                        {c.status === "conditional" && <span className="badge-warning">Conditionnel</span>}
                        {c.status === "rejected" && <span className="badge-danger">Rejeté</span>}
                      </td>
                      <td className="py-3 text-right">
                        <button className="text-accent text-xs hover:underline">
                          {c.status === "rejected" ? "Voir raisons" : "Analyser"}
                        </button>
                      </td>
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

function KpiCard({
  icon,
  label,
  value,
  sub,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <div className={`card p-5 ${accent ? "border-accent/30 bg-accent/[0.03]" : ""}`}>
      <div className="flex items-center gap-2 text-accent text-[10px] uppercase tracking-[0.18em] mb-2">
        {icon}
        <span>{label}</span>
      </div>
      <p className={`font-mono font-bold text-xl ${accent ? "gold-text" : "text-white"}`}>
        {value}
      </p>
      {sub && <p className="text-xs text-neutral-light/50 mt-1">{sub}</p>}
    </div>
  );
}

function EscrowRow({ label, value, sub, locked }: { label: string; value: number; sub?: string; locked?: boolean }) {
  return (
    <div className="rounded-xl bg-dark/40 border border-white/5 p-4">
      <div className="flex items-center justify-between mb-1.5">
        <p className="text-[10px] uppercase tracking-wider text-neutral-light/50">
          {label}
        </p>
        {locked && <Lock className="w-3 h-3 text-accent/70" />}
      </div>
      <p className="font-mono font-bold text-lg text-white">
        {formatFCFA(value)} <span className="text-xs text-neutral-light/50">FCFA</span>
      </p>
      {sub && <p className="text-xs text-neutral-light/50 mt-1">{sub}</p>}
    </div>
  );
}

function AmlRow({ label, value, ok }: { label: string; value: string; ok?: boolean }) {
  return (
    <li className="flex items-center justify-between text-sm py-2 border-b border-white/5 last:border-0">
      <span className="text-neutral-light/70">{label}</span>
      <span className="flex items-center gap-2">
        <span className="font-mono text-white font-semibold">{value}</span>
        {ok && <CheckCircle2 className="w-4 h-4 text-success" />}
      </span>
    </li>
  );
}
