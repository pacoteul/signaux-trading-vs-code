import {
  Check,
  Clock,
  CircleDot,
  ArrowDown,
  Download,
  FileText,
  ShieldCheck,
} from "lucide-react";
import { NINE_SHIELDS, REGULATORY_DOCS, REGULATORY_TIMELINE } from "@/data/mockData";
import { Footer } from "@/components/navigation/Footer";

export const metadata = {
  title: "Conformité — Afritoken",
  description: "Notre engagement de conformité réglementaire BCEAO, AMF-UMOA, AML/CFT.",
};

export default function CompliancePage() {
  return (
    <>
      <section className="section">
        <div className="container-x max-w-6xl">
          <div className="text-center mb-16">
            <ShieldCheck className="w-12 h-12 text-accent mx-auto mb-5" />
            <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
              Conformité réglementaire
            </p>
            <h1 className="font-display font-bold text-4xl sm:text-5xl lg:text-6xl mb-4">
              Notre Engagement de Conformité
            </h1>
            <p className="text-neutral-light/60 max-w-3xl mx-auto">
              Afritoken s'inscrit dans le cadre réglementaire de la zone UEMOA.
              Notre architecture juridique et technique est conçue dès l'origine
              pour répondre aux exigences des régulateurs bancaires.
            </p>
          </div>

          {/* Statut réglementaire — Timeline */}
          <div className="card p-8 lg:p-10 mb-16">
            <h2 className="font-display font-bold text-2xl mb-2">
              Statut réglementaire
            </h2>
            <p className="text-sm text-neutral-light/60 mb-8">
              Suivi en temps réel des étapes d'agrément.
            </p>
            <ol className="relative border-l border-white/10 ml-3 space-y-6">
              {REGULATORY_TIMELINE.map((item, i) => (
                <li key={i} className="ml-6 pb-2">
                  <span className="absolute -left-[11px] flex items-center justify-center w-5 h-5 rounded-full bg-dark border border-white/10">
                    {item.status === "done" && (
                      <Check className="w-3 h-3 text-success" />
                    )}
                    {item.status === "in-progress" && (
                      <CircleDot className="w-3 h-3 text-accent animate-pulse" />
                    )}
                    {item.status === "pending" && (
                      <Clock className="w-3 h-3 text-neutral-light/50" />
                    )}
                  </span>
                  <div className="flex items-center gap-3 flex-wrap">
                    <h3 className="font-display font-semibold text-base text-white">
                      {item.label}
                    </h3>
                    {item.status === "done" && (
                      <span className="badge-success">Terminé</span>
                    )}
                    {item.status === "in-progress" && (
                      <span className="badge-warning">En cours</span>
                    )}
                    {item.status === "pending" && (
                      <span className="badge-neutral">À venir</span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-neutral-light/60">{item.detail}</p>
                </li>
              ))}
            </ol>
          </div>

          {/* Les 9 Boucliers */}
          <div className="mb-16">
            <div className="text-center mb-10">
              <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
                Sécurité des fonds
              </p>
              <h2 className="font-display font-bold text-3xl lg:text-4xl mb-3">
                Comment Afritoken protège les investisseurs
              </h2>
              <p className="text-neutral-light/60 max-w-2xl mx-auto">
                9 mécanismes de protection complémentaires — les "9 Boucliers".
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {NINE_SHIELDS.map((s) => (
                <div key={s.n} className="card card-hover relative pt-12">
                  <div className="absolute -top-4 left-6 w-10 h-10 rounded-xl bg-gold-gradient text-dark font-display font-bold flex items-center justify-center text-sm shadow-glow">
                    {s.n}
                  </div>
                  <h3 className="font-display font-semibold text-base text-white mb-2">
                    {s.title}
                  </h3>
                  <p className="text-sm text-neutral-light/65 leading-relaxed">
                    {s.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Flux des fonds */}
          <div className="mb-16">
            <div className="text-center mb-10">
              <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
                Traçabilité
              </p>
              <h2 className="font-display font-bold text-3xl lg:text-4xl mb-3">
                Flux des fonds
              </h2>
              <p className="text-neutral-light/60 max-w-2xl mx-auto">
                Chaque mouvement est tracé, contrôlé et signé. Aucun fonds
                ne transite par Afritoken.
              </p>
            </div>

            <div className="card p-8 space-y-2">
              <FlowRow steps={["Investisseur", "Wave / Orange Money", "Compte Escrow Banque", "Entreprise"]} sub="Collecte des fonds (double signature)" />
              <div className="flex items-center justify-center text-accent/40 my-4">
                <ArrowDown className="w-6 h-6" />
              </div>
              <FlowRow steps={["Revenus Entreprise", "Compte Escrow", "Audit mensuel", "Distribution Investisseurs"]} sub="Distribution des dividendes (smart contract)" reverse />
            </div>
          </div>

          {/* Documents */}
          <div>
            <div className="text-center mb-10">
              <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
                Bibliothèque réglementaire
              </p>
              <h2 className="font-display font-bold text-3xl lg:text-4xl">
                Documents réglementaires
              </h2>
            </div>

            <div className="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto">
              {REGULATORY_DOCS.map((doc, i) => (
                <button
                  key={i}
                  type="button"
                  className="card card-hover text-left flex items-start gap-4 group"
                >
                  <div className="w-11 h-11 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-accent" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-display font-semibold text-white mb-1">
                      {doc.title}
                    </h3>
                    <p className="text-sm text-neutral-light/60">{doc.description}</p>
                    <span className="badge-neutral mt-3">{doc.type}</span>
                  </div>
                  <Download className="w-4 h-4 text-neutral-light/40 group-hover:text-accent transition-colors flex-shrink-0 mt-1" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>
      <Footer />
    </>
  );
}

function FlowRow({ steps, sub, reverse }: { steps: string[]; sub: string; reverse?: boolean }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-[0.18em] text-accent/80 mb-3 text-center">
        {sub}
      </p>
      <div className="flex flex-col md:flex-row items-stretch gap-3">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-3 flex-1">
            <div className={`flex-1 rounded-xl border p-4 text-center ${
              i === 0 || i === steps.length - 1
                ? "border-accent/40 bg-accent/5"
                : "border-white/10 bg-white/[0.02]"
            }`}>
              <p className="text-sm text-white font-medium">{s}</p>
            </div>
            {i < steps.length - 1 && (
              <span className="hidden md:flex text-accent/60 select-none">
                {reverse ? "←" : "→"}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
