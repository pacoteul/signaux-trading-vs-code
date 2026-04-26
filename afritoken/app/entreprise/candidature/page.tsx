"use client";

import { useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  CheckCircle2,
  CircleDot,
  FileText,
  Send,
  Upload,
  Wallet,
  XCircle,
} from "lucide-react";
import { ELIGIBLE_SECTORS, formatFCFA } from "@/data/mockData";
import { Footer } from "@/components/navigation/Footer";

const STEPS = [
  { id: 1, label: "Informations légales", icon: Building2 },
  { id: 2, label: "Informations financières", icon: Wallet },
  { id: 3, label: "Plan d'utilisation", icon: FileText },
  { id: 4, label: "Score d'éligibilité", icon: CheckCircle2 },
];

type FormState = {
  // Étape 1
  legalName: string;
  legalForm: string;
  ninea: string;
  creationDate: string;
  sector: string;
  address: string;
  director: string;
  phone: string;
  email: string;
  // Étape 2
  amount: number;
  durationMonths: number;
  monthlyRevenue: number;
  hasBankStatements: boolean;
  hasNinea: boolean;
  hasRcs: boolean;
  hasCriminalRecord: boolean;
  hasDebt: boolean;
  // Étape 3
  projectDescription: string;
  fundsUsage: string;
  traceableRevenue: boolean;
  paymentChannel: string;
  acceptsAudit: boolean;
  acceptsVisits: boolean;
  // Helpers
  ageMonths: number;
};

const INITIAL: FormState = {
  legalName: "",
  legalForm: "SARL",
  ninea: "",
  creationDate: "",
  sector: "",
  address: "",
  director: "",
  phone: "",
  email: "",
  amount: 50_000_000,
  durationMonths: 36,
  monthlyRevenue: 0,
  hasBankStatements: false,
  hasNinea: false,
  hasRcs: false,
  hasCriminalRecord: false,
  hasDebt: false,
  projectDescription: "",
  fundsUsage: "",
  traceableRevenue: false,
  paymentChannel: "",
  acceptsAudit: true,
  acceptsVisits: true,
  ageMonths: 24,
};

export default function CandidaturePage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormState>(INITIAL);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((s) => ({ ...s, [key]: value }));

  const score = useMemo(() => {
    let total = 0;
    if (form.ageMonths > 12) total += 15;
    const monthlyObligation = form.amount * 0.02;
    if (form.monthlyRevenue > monthlyObligation * 3) total += 20;
    if (form.traceableRevenue) total += 15;
    const sectorObj = ELIGIBLE_SECTORS.find((s) => s.value === form.sector);
    if (sectorObj?.priority === "A") total += 20;
    else if (sectorObj?.priority === "B") total += 10;
    if (form.hasBankStatements && form.hasNinea && form.hasRcs && form.hasCriminalRecord)
      total += 15;
    if (!form.hasDebt) total += 15;
    return Math.min(100, total);
  }, [form]);

  const eligibility = useMemo(() => {
    if (score >= 85) return { label: "ÉLIGIBLE — Fast Track (5 jours)", tone: "success" as const };
    if (score >= 70) return { label: "ÉLIGIBLE — Standard (10 jours)", tone: "success" as const };
    if (score >= 55)
      return { label: "ÉLIGIBLE CONDITIONNEL — Montant réduit", tone: "warning" as const };
    return { label: "NON ÉLIGIBLE", tone: "danger" as const };
  }, [score]);

  return (
    <>
      <section className="px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
        <div className="container-x max-w-4xl">
          <div className="text-center mb-10">
            <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
              Candidature
            </p>
            <h1 className="font-display font-bold text-3xl lg:text-4xl mb-3">
              Devenez la prochaine entreprise tokenisée
            </h1>
            <p className="text-neutral-light/60 max-w-2xl mx-auto">
              Remplissez ce dossier — analyse en 5 à 10 jours ouvrables.
            </p>
          </div>

          {/* Stepper */}
          <div className="card p-4 mb-6">
            <div className="grid grid-cols-4 gap-2">
              {STEPS.map((s) => {
                const active = step === s.id;
                const done = step > s.id;
                return (
                  <div
                    key={s.id}
                    className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs ${
                      active
                        ? "bg-accent/15 text-accent border border-accent/30"
                        : done
                        ? "text-success"
                        : "text-neutral-light/50"
                    }`}
                  >
                    <span className="flex items-center justify-center w-5 h-5 rounded-full border border-current">
                      {done ? <CheckCircle2 className="w-3.5 h-3.5" /> : s.id}
                    </span>
                    <span className="hidden md:inline truncate">{s.label}</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-3 h-1 rounded-full bg-white/5 overflow-hidden">
              <div
                className="h-full bg-gold-gradient transition-all"
                style={{ width: `${(step / 4) * 100}%` }}
              />
            </div>
          </div>

          <div className="card p-6 lg:p-8 space-y-6">
            {step === 1 && <Step1 form={form} update={update} />}
            {step === 2 && <Step2 form={form} update={update} />}
            {step === 3 && <Step3 form={form} update={update} />}
            {step === 4 && <Step4 score={score} eligibility={eligibility} />}

            <div className="flex justify-between pt-4 border-t border-white/5">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setStep((s) => Math.max(1, s - 1))}
                disabled={step === 1}
              >
                <ArrowLeft className="w-4 h-4" />
                Précédent
              </button>
              {step < 4 ? (
                <button
                  type="button"
                  className="btn-accent"
                  onClick={() => setStep((s) => Math.min(4, s + 1))}
                >
                  Suivant
                  <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button type="button" className="btn-accent">
                  <Send className="w-4 h-4" />
                  Soumettre ma candidature
                </button>
              )}
            </div>
          </div>
        </div>
      </section>
      <Footer />
    </>
  );
}

function Step1({
  form,
  update,
}: {
  form: FormState;
  update: <K extends keyof FormState>(key: K, value: FormState[K]) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="font-display font-bold text-xl">Informations légales</h2>
      <div className="grid sm:grid-cols-2 gap-4">
        <Field label="Raison sociale">
          <input className="input" value={form.legalName} onChange={(e) => update("legalName", e.target.value)} />
        </Field>
        <Field label="Forme juridique">
          <select className="input" value={form.legalForm} onChange={(e) => update("legalForm", e.target.value)}>
            <option>SARL</option>
            <option>SA</option>
            <option>SAS</option>
          </select>
        </Field>
        <Field label="NINEA">
          <input className="input font-mono" value={form.ninea} onChange={(e) => update("ninea", e.target.value)} />
        </Field>
        <Field label="Date de création">
          <input type="date" className="input" value={form.creationDate} onChange={(e) => update("creationDate", e.target.value)} />
        </Field>
        <Field label="Secteur d'activité" full>
          <select className="input" value={form.sector} onChange={(e) => update("sector", e.target.value)}>
            <option value="">Sélectionner un secteur</option>
            {ELIGIBLE_SECTORS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label} (priorité {s.priority})
              </option>
            ))}
          </select>
        </Field>
        <Field label="Adresse siège social" full>
          <input className="input" value={form.address} onChange={(e) => update("address", e.target.value)} />
        </Field>
        <Field label="Dirigeant principal">
          <input className="input" value={form.director} onChange={(e) => update("director", e.target.value)} />
        </Field>
        <Field label="Téléphone">
          <input className="input" value={form.phone} onChange={(e) => update("phone", e.target.value)} />
        </Field>
        <Field label="Email" full>
          <input type="email" className="input" value={form.email} onChange={(e) => update("email", e.target.value)} />
        </Field>
      </div>
    </div>
  );
}

function Step2({
  form,
  update,
}: {
  form: FormState;
  update: <K extends keyof FormState>(key: K, value: FormState[K]) => void;
}) {
  return (
    <div className="space-y-5">
      <h2 className="font-display font-bold text-xl">Informations financières</h2>
      <Field label={
        <span className="flex justify-between">
          <span>Montant souhaité</span>
          <span className="font-mono text-accent">{formatFCFA(form.amount)} FCFA</span>
        </span>
      } full>
        <input
          type="range"
          min={5_000_000}
          max={500_000_000}
          step={1_000_000}
          value={form.amount}
          onChange={(e) => update("amount", Number(e.target.value))}
          style={{
            "--slider-progress": `${((form.amount - 5_000_000) / (500_000_000 - 5_000_000)) * 100}%`,
          } as React.CSSProperties}
        />
        <div className="flex justify-between text-[10px] uppercase tracking-wider text-neutral-light/40 mt-2 font-mono">
          <span>5M</span>
          <span>500M</span>
        </div>
      </Field>

      <Field label="Durée souhaitée" full>
        <div className="grid grid-cols-2 gap-2">
          {[24, 36].map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => update("durationMonths", m)}
              className={`rounded-xl border px-4 py-3 text-sm transition-colors font-medium ${
                form.durationMonths === m
                  ? "border-accent/60 bg-accent/10 text-accent"
                  : "border-white/10 text-neutral-light/70 hover:border-white/20"
              }`}
            >
              {m} mois
            </button>
          ))}
        </div>
      </Field>

      <Field label="Revenus mensuels moyens (6 derniers mois — FCFA)" full>
        <input
          type="number"
          className="input font-mono"
          value={form.monthlyRevenue || ""}
          onChange={(e) => update("monthlyRevenue", Number(e.target.value))}
          placeholder="ex: 71 500 000"
        />
      </Field>

      <div className="grid sm:grid-cols-2 gap-3">
        <FileToggle label="Relevés bancaires 12 mois" checked={form.hasBankStatements} onToggle={(v) => update("hasBankStatements", v)} />
        <FileToggle label="NINEA" checked={form.hasNinea} onToggle={(v) => update("hasNinea", v)} />
        <FileToggle label="Registre du commerce" checked={form.hasRcs} onToggle={(v) => update("hasRcs", v)} />
        <FileToggle label="Casier judiciaire dirigeant" checked={form.hasCriminalRecord} onToggle={(v) => update("hasCriminalRecord", v)} />
      </div>

      <YesNo
        label="Dettes en cours ?"
        value={form.hasDebt}
        onChange={(v) => update("hasDebt", v)}
      />
    </div>
  );
}

function Step3({
  form,
  update,
}: {
  form: FormState;
  update: <K extends keyof FormState>(key: K, value: FormState[K]) => void;
}) {
  return (
    <div className="space-y-5">
      <h2 className="font-display font-bold text-xl">Plan d'utilisation</h2>
      <Field label="Description du projet de développement" full>
        <textarea
          rows={4}
          className="input"
          value={form.projectDescription}
          onChange={(e) => update("projectDescription", e.target.value)}
          placeholder="Présentez votre projet en quelques phrases…"
        />
      </Field>
      <Field label="Comment les fonds seront utilisés" full>
        <textarea
          rows={4}
          className="input"
          value={form.fundsUsage}
          onChange={(e) => update("fundsUsage", e.target.value)}
          placeholder="ex: 91% achat de véhicules, 5% fonds de roulement, 4% réserve…"
        />
      </Field>
      <YesNo
        label="Vos revenus actuels sont-ils traçables ?"
        value={form.traceableRevenue}
        onChange={(v) => update("traceableRevenue", v)}
      />
      <Field label="Via quel canal ?" full>
        <select
          className="input"
          value={form.paymentChannel}
          onChange={(e) => update("paymentChannel", e.target.value)}
        >
          <option value="">Sélectionner</option>
          <option>Wave</option>
          <option>Orange Money</option>
          <option>TPE bancaire</option>
          <option>Yango</option>
          <option>Mixte</option>
        </select>
      </Field>
      <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4 space-y-2 text-sm">
        <p className="text-xs uppercase tracking-[0.18em] text-accent">Engagements obligatoires</p>
        <p className="text-neutral-light/80">
          ✅ L'entreprise accepte un audit mensuel indépendant (obligatoire)
        </p>
        <p className="text-neutral-light/80">
          ✅ L'entreprise accepte des visites surprise (obligatoire)
        </p>
      </div>
    </div>
  );
}

function Step4({
  score,
  eligibility,
}: {
  score: number;
  eligibility: { label: string; tone: "success" | "warning" | "danger" };
}) {
  const angle = (score / 100) * 360;
  return (
    <div>
      <h2 className="font-display font-bold text-xl mb-2">Score d'éligibilité</h2>
      <p className="text-sm text-neutral-light/60 mb-6">
        Calculé automatiquement à partir des informations renseignées.
      </p>

      <div className="grid lg:grid-cols-2 gap-8 items-center mb-6">
        <div className="flex justify-center">
          <div
            className="relative w-52 h-52 rounded-full"
            style={{
              background: `conic-gradient(${
                eligibility.tone === "success"
                  ? "#2E7D32"
                  : eligibility.tone === "warning"
                  ? "#F9A825"
                  : "#C62828"
              } ${angle}deg, rgba(255,255,255,0.08) ${angle}deg)`,
            }}
          >
            <div className="absolute inset-3 rounded-full bg-dark border border-white/5 flex flex-col items-center justify-center">
              <span className="font-display font-bold text-5xl text-white">{score}</span>
              <span className="text-xs text-neutral-light/50 mt-1">/ 100</span>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div
            className={`rounded-2xl border p-5 ${
              eligibility.tone === "success"
                ? "border-success/30 bg-success/5"
                : eligibility.tone === "warning"
                ? "border-accent/30 bg-accent/5"
                : "border-danger/30 bg-danger/5"
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              {eligibility.tone === "success" && <CheckCircle2 className="w-5 h-5 text-success" />}
              {eligibility.tone === "warning" && <CircleDot className="w-5 h-5 text-accent" />}
              {eligibility.tone === "danger" && <XCircle className="w-5 h-5 text-danger" />}
              <p className="font-display font-semibold text-white">Verdict</p>
            </div>
            <p
              className={`font-mono text-lg ${
                eligibility.tone === "success"
                  ? "text-success"
                  : eligibility.tone === "warning"
                  ? "text-accent"
                  : "text-red-300"
              }`}
            >
              {eligibility.label}
            </p>
          </div>

          <ScoreBreakdown />
        </div>
      </div>
    </div>
  );
}

function ScoreBreakdown() {
  const items = [
    { label: "Ancienneté > 12 mois", points: 15 },
    { label: "Revenus > 3× obligations", points: 20 },
    { label: "Revenus traçables", points: 15 },
    { label: "Secteur prioritaire A", points: 20 },
    { label: "Documents complets", points: 15 },
    { label: "Zéro dette critique", points: 15 },
  ];
  return (
    <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-accent mb-3">Barème</p>
      <ul className="space-y-2 text-sm">
        {items.map((it) => (
          <li key={it.label} className="flex items-center justify-between">
            <span className="text-neutral-light/70">{it.label}</span>
            <span className="font-mono text-accent">+{it.points} pts</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Field({
  label,
  children,
  full,
}: {
  label: React.ReactNode;
  children: React.ReactNode;
  full?: boolean;
}) {
  return (
    <div className={full ? "sm:col-span-2" : ""}>
      <div className="label">{label}</div>
      {children}
    </div>
  );
}

function YesNo({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div>
      <div className="label">{label}</div>
      <div className="grid grid-cols-2 gap-2">
        {[
          { v: true, label: "Oui" },
          { v: false, label: "Non" },
        ].map((o) => (
          <button
            key={String(o.v)}
            type="button"
            onClick={() => onChange(o.v)}
            className={`rounded-xl border px-4 py-3 text-sm font-medium transition-colors ${
              value === o.v
                ? "border-accent/60 bg-accent/10 text-accent"
                : "border-white/10 text-neutral-light/70 hover:border-white/20"
            }`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function FileToggle({
  label,
  checked,
  onToggle,
}: {
  label: string;
  checked: boolean;
  onToggle: (v: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onToggle(!checked)}
      className={`rounded-xl border px-4 py-3 text-sm flex items-center gap-3 text-left transition-colors ${
        checked
          ? "border-success/40 bg-success/5 text-green-200"
          : "border-white/10 text-neutral-light/70 hover:border-white/20"
      }`}
    >
      {checked ? (
        <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
      ) : (
        <Upload className="w-4 h-4 flex-shrink-0" />
      )}
      <span className="flex-1 truncate">{label}</span>
    </button>
  );
}
