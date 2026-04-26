import {
  Building2,
  Hexagon,
  Smartphone,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { HOW_IT_WORKS } from "@/data/mockData";

const ICON_MAP = { Building2, Hexagon, Smartphone, ShieldCheck, Zap };

export function HowItWorks() {
  return (
    <section className="section">
      <div className="container-x">
        <div className="text-center mb-14">
          <p className="text-sm uppercase tracking-[0.2em] text-accent mb-3">
            Le fonctionnement
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl lg:text-5xl">
            Comment ça marche
          </h2>
          <p className="mt-4 text-neutral-light/60 max-w-2xl mx-auto">
            5 étapes simples, contrôlées et transparentes — de la candidature
            de l'entreprise au versement des dividendes.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
          {HOW_IT_WORKS.map((step) => {
            const Icon = ICON_MAP[step.icon as keyof typeof ICON_MAP];
            return (
              <div key={step.step} className="card relative card-hover group">
                <div className="absolute -top-3 -left-3 w-9 h-9 rounded-full bg-accent text-dark font-display font-bold text-sm flex items-center justify-center shadow-glow">
                  {step.step}
                </div>
                <div className="w-12 h-12 rounded-xl bg-primary/20 border border-primary/30 flex items-center justify-center mb-4 mt-1 group-hover:border-accent/40 transition-colors">
                  <Icon className="w-5 h-5 text-accent" />
                </div>
                <h3 className="font-display font-semibold text-base mb-2 text-white">
                  {step.title}
                </h3>
                <p className="text-sm text-neutral-light/60 leading-relaxed">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
