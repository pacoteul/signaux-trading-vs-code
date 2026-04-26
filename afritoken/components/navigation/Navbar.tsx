"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Lock, Menu, X } from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { cn } from "@/lib/cn";

const NAV_LINKS = [
  { href: "/", label: "Accueil" },
  { href: "/investor", label: "Investisseurs" },
  { href: "/entreprise", label: "Entreprises" },
  { href: "/conformite", label: "Conformité" },
];

export function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-dark/80 border-b border-white/[0.06]">
      <div className="container-x px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center" onClick={() => setOpen(false)}>
            <Logo />
          </Link>

          <nav className="hidden lg:flex items-center gap-1">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    active
                      ? "text-accent bg-accent/10"
                      : "text-neutral-light/70 hover:text-white hover:bg-white/5"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          <div className="hidden lg:flex items-center gap-3">
            <span className="badge-warning">
              <Lock className="w-3 h-3" />
              Agrément BCEAO en cours
            </span>
            <button className="btn-ghost text-sm" disabled>
              Se connecter
            </button>
            <Link href="/admin" className="btn-accent text-sm">
              Démo Admin
            </Link>
          </div>

          <button
            type="button"
            className="lg:hidden p-2 rounded-lg text-neutral-light hover:bg-white/5"
            onClick={() => setOpen((v) => !v)}
            aria-label="Menu"
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {open && (
          <div className="lg:hidden pb-4 space-y-2">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "block px-4 py-2 rounded-lg text-sm font-medium",
                    active ? "text-accent bg-accent/10" : "text-neutral-light/80 hover:bg-white/5"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
            <div className="pt-2 flex flex-col gap-2">
              <span className="badge-warning self-start">
                <Lock className="w-3 h-3" /> Agrément BCEAO en cours
              </span>
              <Link href="/admin" onClick={() => setOpen(false)} className="btn-accent text-sm">
                Démo Admin
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
