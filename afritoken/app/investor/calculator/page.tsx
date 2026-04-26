"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Calculator, Lock, Sparkles, TrendingUp } from "lucide-react";
import { Footer } from "@/components/navigation/Footer";
import { formatFCFA } from "@/data/mockData";

export default function CalculatorPage() {
  const [amount, setAmount] = useState(500_000);
  const [duration, setDuration] = useState(36);

  const monthlyRate = 0.02;
  const bankAnnualRate = 0.05;

  const monthlyDividend = Math.round(amount * monthlyRate);
  const totalDividends = monthlyDividend * duration;
  const reimbursed = amount;
  const netGain = totalDividends;
  const annualEquivalent = monthlyRate * 12 * 100;

  const monthlyData = useMemo(() => {
    const reservePerMonth = amount / duration;
    return Array.from({ length: duration }, (_, i) => {
      const m = i + 1;
      return {
        month: `M${m}`,
        dividend: monthlyDividend,
        reserve: Math.round(reservePerMonth * m),
      };
    });
  }, [amount, duration, monthlyDividend]);

  const compareData = useMemo(() => {
    const data: { month: string; afritoken: number; bank: number }[] = [];
    for (let i = 1; i <= duration; i++) {
      const afritokenCum = monthlyDividend * i;
      const bankCum = Math.round(amount * Math.pow(1 + bankAnnualRate / 12, i) - amount);
      data.push({
        month: `M${i}`,
        afritoken: afritokenCum,
        bank: bankCum,
      });
    }
    return data;
  }, [amount, duration, monthlyDividend, bankAnnualRate]);

  const sliderProgress = (val: number, min: number, max: number) =>
    `${((val - min) / (max - min)) * 100}%`;

  return (
    <>
      <section className="px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
        <div className="container-x max-w-6xl">
          <div className="text-center mb-12">
            <Calculator className="w-12 h-12 text-accent mx-auto mb-4" />
            <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
              Calculateur
            </p>
            <h1 className="font-display font-bold text-4xl lg:text-5xl mb-4">
              Simulez votre investissement
            </h1>
            <p className="text-neutral-light/60 max-w-2xl mx-auto">
              Ajustez les paramètres ci-dessous pour visualiser instantanément
              votre rendement potentiel sur Afritoken.
            </p>
          </div>

          <div className="grid lg:grid-cols-5 gap-6 mb-8">
            {/* Form */}
            <div className="lg:col-span-2 card p-6 lg:p-8 space-y-8">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="label !mb-0">Montant investi</label>
                  <span className="font-mono text-accent font-bold">
                    {formatFCFA(amount)} FCFA
                  </span>
                </div>
                <input
                  type="range"
                  min={1000}
                  max={10_000_000}
                  step={1000}
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  style={{ "--slider-progress": sliderProgress(amount, 1000, 10_000_000) } as React.CSSProperties}
                />
                <div className="flex justify-between text-[10px] uppercase tracking-wider text-neutral-light/40 mt-2 font-mono">
                  <span>1k</span>
                  <span>5M</span>
                  <span>10M</span>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="label !mb-0">Durée</label>
                  <span className="font-mono text-accent font-bold">{duration} mois</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[12, 24, 36].map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setDuration(m)}
                      className={`rounded-xl border px-4 py-3 text-sm transition-colors font-medium ${
                        duration === m
                          ? "border-accent/60 bg-accent/10 text-accent"
                          : "border-white/10 text-neutral-light/70 hover:border-white/20"
                      }`}
                    >
                      {m} mois
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">Taux mensuel</label>
                <div className="rounded-xl border border-success/30 bg-success/5 px-4 py-3 flex items-center justify-between">
                  <span className="text-sm text-neutral-light/80">Rendement fixe</span>
                  <span className="font-mono text-success font-bold text-lg">2,00% / mois</span>
                </div>
                <p className="text-xs text-neutral-light/50 mt-2 leading-relaxed">
                  Le taux est fixe pour tous les investisseurs et garanti par smart
                  contract.
                </p>
              </div>
            </div>

            {/* Results */}
            <div className="lg:col-span-3 space-y-4">
              <div className="card p-6 lg:p-8 relative overflow-hidden">
                <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-accent/15 blur-3xl pointer-events-none" />
                <div className="relative">
                  <p className="text-xs uppercase tracking-[0.18em] text-accent mb-2 flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5" />
                    Résultat de la simulation
                  </p>
                  <p className="text-sm text-neutral-light/60 mb-6">Gain net total</p>
                  <p className="font-mono font-bold gold-text text-5xl lg:text-6xl mb-1">
                    {formatFCFA(netGain)}
                    <span className="text-2xl lg:text-3xl text-accent/70 ml-2 font-display">FCFA</span>
                  </p>
                  <p className="text-sm text-neutral-light/60">
                    sur {duration} mois — soit{" "}
                    <span className="text-accent font-semibold">{annualEquivalent.toFixed(0)}%</span> de rendement annuel équivalent
                  </p>
                </div>
              </div>

              <div className="grid sm:grid-cols-3 gap-3">
                <ResultCard label="Rendement mensuel" value={`${formatFCFA(monthlyDividend)} FCFA`} sub="par mois" />
                <ResultCard label="Total dividendes" value={`${formatFCFA(totalDividends)} FCFA`} sub={`sur ${duration} mois`} />
                <ResultCard label="Capital remboursé" value={`${formatFCFA(reimbursed)} FCFA`} sub="à terme" />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-6 mb-8">
            <div className="card p-6 lg:p-8">
              <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                Détail mois par mois
              </p>
              <h3 className="font-display font-bold text-xl mb-6">
                Dividendes & réserve cumulée
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fontSize: 9 }} interval={Math.max(1, Math.floor(duration / 8))} />
                    <YAxis
                      tick={{ fontSize: 10 }}
                      tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0D1B0F",
                        border: "1px solid rgba(249,168,37,0.3)",
                        borderRadius: 12,
                        fontSize: 12,
                      }}
                      formatter={(v: number) => `${v.toLocaleString("fr-FR")} FCFA`}
                    />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Bar dataKey="dividend" name="Dividende mensuel" fill="#F9A825" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="reserve" name="Réserve remboursement" fill="#1B5E20" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card p-6 lg:p-8">
              <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
                Comparaison
              </p>
              <h3 className="font-display font-bold text-xl mb-6">
                Afritoken vs Épargne bancaire (5%/an)
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={compareData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fontSize: 9 }} interval={Math.max(1, Math.floor(duration / 8))} />
                    <YAxis
                      tick={{ fontSize: 10 }}
                      tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0D1B0F",
                        border: "1px solid rgba(249,168,37,0.3)",
                        borderRadius: 12,
                        fontSize: 12,
                      }}
                      formatter={(v: number) => `${Math.round(v).toLocaleString("fr-FR")} FCFA`}
                    />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Line
                      type="monotone"
                      dataKey="afritoken"
                      name="Afritoken (gain cumulé)"
                      stroke="#F9A825"
                      strokeWidth={2.5}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="bank"
                      name="Banque (gain cumulé)"
                      stroke="#C62828"
                      strokeWidth={2}
                      strokeDasharray="6 4"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="card p-8 lg:p-10 text-center max-w-3xl mx-auto">
            <TrendingUp className="w-10 h-10 text-accent mx-auto mb-4" />
            <h3 className="font-display font-bold text-2xl mb-2">Prêt à passer à l'action ?</h3>
            <p className="text-neutral-light/60 mb-6">
              L'investissement sera ouvert dès l'obtention de l'agrément BCEAO.
            </p>
            <button className="btn-accent text-base px-7 py-4" disabled>
              <Lock className="w-4 h-4" />
              Investir maintenant — Agrément BCEAO en cours
            </button>
          </div>
        </div>
      </section>
      <Footer />
    </>
  );
}

function ResultCard({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="card p-5">
      <p className="text-[10px] uppercase tracking-[0.18em] text-neutral-light/50 mb-2">
        {label}
      </p>
      <p className="font-mono font-bold text-lg text-white">{value}</p>
      <p className="text-xs text-neutral-light/50 mt-1">{sub}</p>
    </div>
  );
}
