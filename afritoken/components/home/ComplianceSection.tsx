import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { COMPLIANCE_BADGES } from "@/data/mockData";

export function ComplianceSection() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="card max-w-5xl mx-auto p-10 lg:p-12 text-center">
          <ShieldCheck className="w-12 h-12 text-accent mx-auto mb-5" />
          <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
            Conformité réglementaire
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl mb-4">
            Construit pour la BCEAO
          </h2>
          <p className="text-neutral-light/60 max-w-2xl mx-auto mb-10">
            Afritoken s'inscrit dans le cadre réglementaire de la zone UEMOA.
            Notre architecture juridique et technique est conçue dès l'origine
            pour répondre aux exigences des régulateurs.
          </p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-10">
            {COMPLIANCE_BADGES.map((b, i) => (
              <div
                key={i}
                className="flex items-center gap-2 rounded-xl border border-success/30 bg-success/5 px-4 py-3 text-sm text-green-200 justify-center"
              >
                <span className="text-success">✓</span>
                <span>{b}</span>
              </div>
            ))}
          </div>

          <Link href="/conformite" className="btn-outline">
            Voir notre page conformité
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}
