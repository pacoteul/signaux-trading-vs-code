import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { LogoMark } from "@/components/ui/Logo";

export default function NotFound() {
  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="flex justify-center mb-6">
          <LogoMark size={56} />
        </div>
        <p className="font-mono font-bold gold-text text-7xl mb-4">404</p>
        <h1 className="font-display font-bold text-2xl mb-3">Page introuvable</h1>
        <p className="text-neutral-light/60 mb-8">
          Cette page n'existe pas ou a été déplacée. Retournez à l'accueil pour
          continuer votre exploration d'Afritoken.
        </p>
        <Link href="/" className="btn-accent">
          <ArrowLeft className="w-4 h-4" />
          Retour à l'accueil
        </Link>
      </div>
    </div>
  );
}
