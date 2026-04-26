import { Sparkles } from "lucide-react";

export function DemoBanner() {
  return (
    <div className="w-full bg-accent text-primary-700 text-xs sm:text-sm font-medium">
      <div className="container-x flex items-center justify-center gap-2 px-4 py-2 text-center">
        <Sparkles className="w-4 h-4 flex-shrink-0" />
        <span>
          <span className="font-bold">PLATEFORME DE DÉMONSTRATION</span> — Données
          simulées — Afritoken est en cours de soumission de dossier d'agrément
          auprès de la BCEAO
          <span className="hidden sm:inline"> | Version Pilote Avril 2026</span>
        </span>
      </div>
    </div>
  );
}
