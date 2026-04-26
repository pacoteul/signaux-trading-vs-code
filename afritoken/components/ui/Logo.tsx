import { cn } from "@/lib/cn";

export function Logo({ size = 36, className }: { size?: number; className?: string }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="afri-gold" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#F9A825" />
            <stop offset="0.5" stopColor="#FFCA28" />
            <stop offset="1" stopColor="#C77800" />
          </linearGradient>
          <linearGradient id="afri-green" x1="0" y1="0" x2="0" y2="64" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#1B5E20" />
            <stop offset="1" stopColor="#0D1B0F" />
          </linearGradient>
        </defs>
        <path
          d="M32 2 L58 17 L58 47 L32 62 L6 47 L6 17 Z"
          fill="url(#afri-green)"
          stroke="url(#afri-gold)"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />
        {/* Stylized Africa silhouette */}
        <path
          d="M28 16 C24 18 22 22 23 26 L25 31 L24 36 L26 41 L29 45 L33 47 L37 45 L40 41 L41 36 L43 31 L43 26 C43 22 41 18 37 16 L33 15 Z"
          fill="url(#afri-gold)"
          opacity="0.95"
        />
        <circle cx="32" cy="32" r="2.5" fill="#0D1B0F" />
      </svg>
      <div className="flex flex-col leading-none">
        <span className="font-display font-bold text-lg tracking-tight text-white">
          AFRITOKEN
        </span>
        <span className="text-[9px] uppercase tracking-[0.2em] text-accent/80">
          Tokenize Africa
        </span>
      </div>
    </div>
  );
}

export function LogoMark({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
      <defs>
        <linearGradient id="afri-gold-mark" x1="0" y1="0" x2="64" y2="64">
          <stop offset="0" stopColor="#F9A825" />
          <stop offset="1" stopColor="#FFCA28" />
        </linearGradient>
      </defs>
      <path d="M32 2 L58 17 L58 47 L32 62 L6 47 L6 17 Z" fill="#0D1B0F" stroke="url(#afri-gold-mark)" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M28 16 C24 18 22 22 23 26 L25 31 L24 36 L26 41 L29 45 L33 47 L37 45 L40 41 L41 36 L43 31 L43 26 C43 22 41 18 37 16 L33 15 Z" fill="url(#afri-gold-mark)" />
    </svg>
  );
}
