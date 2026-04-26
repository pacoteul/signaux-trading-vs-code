"use client";

import { useState } from "react";
import { AlertTriangle, CheckCircle2, RotateCw, Siren } from "lucide-react";
import { FRAUD_ALERT, formatFCFA } from "@/data/mockData";

export function FraudSimulator() {
  const [alertActive, setAlertActive] = useState(false);

  return (
    <div className="card p-8">
      <div className="flex items-start justify-between mb-6 flex-wrap gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-accent mb-1">
            Système d'alerte anti-fraude
          </p>
          <h2 className="font-display font-bold text-2xl text-white">
            Protection automatique des investisseurs
          </h2>
          <p className="text-sm text-neutral-light/60 mt-1">
            Testez notre système de détection en simulant une anomalie.
          </p>
        </div>
        {!alertActive ? (
          <button
            type="button"
            onClick={() => setAlertActive(true)}
            className="btn bg-danger text-white hover:bg-red-700"
          >
            <Siren className="w-4 h-4" />
            Simuler une anomalie
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setAlertActive(false)}
            className="btn bg-success text-white hover:bg-green-700"
          >
            <RotateCw className="w-4 h-4" />
            Résoudre l'alerte
          </button>
        )}
      </div>

      {!alertActive ? (
        <div className="rounded-2xl border border-success/20 bg-success/5 p-6 flex items-center gap-4">
          <CheckCircle2 className="w-8 h-8 text-success flex-shrink-0" />
          <div>
            <p className="font-display font-semibold text-white">
              Système opérationnel
            </p>
            <p className="text-sm text-neutral-light/60">
              Aucune anomalie détectée. Tous les flux sont validés en temps réel.
            </p>
          </div>
        </div>
      ) : (
        <div className="rounded-2xl border border-danger/40 bg-danger/10 p-6 animate-fade-in">
          <div className="flex items-start gap-4 mb-5">
            <div className="w-11 h-11 rounded-xl bg-danger/20 border border-danger/40 flex items-center justify-center flex-shrink-0 animate-pulse">
              <AlertTriangle className="w-5 h-5 text-danger" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-danger font-semibold mb-1">
                Alerte détectée — {FRAUD_ALERT.date}
              </p>
              <p className="font-display font-semibold text-white text-lg">
                Anomalie de revenus déclarés
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-3 gap-3 mb-5">
            <div className="rounded-xl bg-dark/60 border border-white/5 p-4">
              <p className="text-[10px] uppercase tracking-wider text-neutral-light/50">
                Déclaré entreprise
              </p>
              <p className="font-mono font-bold text-lg mt-1 text-white">
                {formatFCFA(FRAUD_ALERT.declared)} <span className="text-xs text-neutral-light/50">FCFA</span>
              </p>
            </div>
            <div className="rounded-xl bg-dark/60 border border-white/5 p-4">
              <p className="text-[10px] uppercase tracking-wider text-neutral-light/50">
                Mesuré IoT
              </p>
              <p className="font-mono font-bold text-lg mt-1 text-accent">
                {formatFCFA(FRAUD_ALERT.measured)} <span className="text-xs text-neutral-light/50">FCFA</span>
              </p>
            </div>
            <div className="rounded-xl bg-danger/10 border border-danger/30 p-4">
              <p className="text-[10px] uppercase tracking-wider text-red-300">
                Écart détecté
              </p>
              <p className="font-mono font-bold text-lg mt-1 text-red-300">
                +{FRAUD_ALERT.gapPercent}% 🚨
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-dark/40 border border-white/5 p-5">
            <p className="text-xs uppercase tracking-[0.18em] text-accent mb-3">
              Action automatique déclenchée
            </p>
            <ul className="space-y-2">
              {FRAUD_ALERT.actions.map((action, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-neutral-light/85">
                  <span className="text-accent font-mono text-xs">→</span>
                  {action}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
