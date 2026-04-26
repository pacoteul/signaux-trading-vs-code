import { LogoMark } from "@/components/ui/Logo";

export default function Loading() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center gap-6">
      <div className="animate-pulse-slow">
        <LogoMark size={64} />
      </div>
      <div className="flex flex-col items-center gap-1">
        <p className="font-display font-bold text-lg gold-text">AFRITOKEN</p>
        <p className="text-xs text-neutral-light/50 uppercase tracking-[0.18em]">
          Chargement…
        </p>
      </div>
    </div>
  );
}
