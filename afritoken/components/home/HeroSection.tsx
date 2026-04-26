"use client";

import Link from "next/link";
import { ArrowRight, ShieldCheck, TrendingUp } from "lucide-react";
import { Particles } from "@/components/ui/Particles";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-hero-radial" aria-hidden="true" />
      <Particles count={28} />

      <div className="container-x px-4 sm:px-6 lg:px-8 pt-20 pb-24 lg:pt-32 lg:pb-36 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 mb-6 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5 text-accent text-xs font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            Dossier agrément BCEAO en cours
          </div>

          <h1 className="font-display font-bold text-5xl sm:text-6xl lg:text-7xl tracking-tight leading-[1.05] mb-6 animate-slide-up">
            <span className="gold-text">Tokenize Africa's</span>
            <br />
            <span className="text-white">Future.</span>
          </h1>

          <p className="text-lg sm:text-xl text-neutral-light/70 max-w-2xl mx-auto mb-10 leading-relaxed">
            La première plateforme de tokenisation d'actifs productifs pour
            les PME africaines.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href="/investor" className="btn-primary text-base px-7 py-4">
              <TrendingUp className="w-5 h-5" />
              Je veux investir
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/entreprise" className="btn-outline text-base px-7 py-4">
              Lever des fonds
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="mt-14 flex items-center justify-center gap-8 text-xs text-neutral-light/40 uppercase tracking-[0.18em]">
            <span>Stellar Blockchain</span>
            <span className="hidden sm:inline">•</span>
            <span>Zone UEMOA</span>
            <span className="hidden sm:inline">•</span>
            <span>Droit OHADA</span>
          </div>
        </div>
      </div>
    </section>
  );
}
