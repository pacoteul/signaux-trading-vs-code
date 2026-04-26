import Link from "next/link";
import { Logo } from "@/components/ui/Logo";

export function Footer() {
  return (
    <footer className="border-t border-white/5 mt-12">
      <div className="container-x px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <Logo />
            <p className="mt-4 text-sm text-neutral-light/60 max-w-xs">
              Tokenize Africa's Future. La première plateforme de tokenisation
              d'actifs productifs pour les PME africaines.
            </p>
          </div>
          <FooterCol
            title="Produit"
            links={[
              { href: "/investor", label: "Espace Investisseur" },
              { href: "/investor/calculator", label: "Calculateur" },
              { href: "/entreprise", label: "Espace Entreprise" },
              { href: "/entreprise/candidature", label: "Candidature" },
            ]}
          />
          <FooterCol
            title="Conformité"
            links={[
              { href: "/conformite", label: "Conformité BCEAO" },
              { href: "/conformite", label: "Sécurité des fonds" },
              { href: "/conformite", label: "AML / CFT" },
              { href: "/admin", label: "Démo Admin" },
            ]}
          />
          <FooterCol
            title="Contact"
            links={[
              { href: "#", label: "contact@afritoken.africa" },
              { href: "#", label: "Dakar — Sénégal" },
              { href: "#", label: "Zone UEMOA" },
            ]}
          />
        </div>
        <div className="mt-12 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-neutral-light/50">
          <p>© 2026 Afritoken — Dossier agrément BCEAO en cours</p>
          <p>Plateforme de démonstration — Version pilote</p>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({
  title,
  links,
}: {
  title: string;
  links: { href: string; label: string }[];
}) {
  return (
    <div>
      <h4 className="font-display font-semibold text-sm text-white mb-4">{title}</h4>
      <ul className="space-y-2">
        {links.map((l, i) => (
          <li key={`${l.href}-${i}`}>
            <Link href={l.href} className="text-sm text-neutral-light/60 hover:text-accent transition-colors">
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
