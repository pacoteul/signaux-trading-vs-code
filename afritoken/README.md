# Afritoken — MVP

Plateforme de tokenisation d'actifs productifs pour les PME africaines.
Démonstration destinée à la BCEAO (Banque Centrale des États d'Afrique de l'Ouest).

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts (graphiques)
- Framer Motion (transitions)
- Lucide React (icônes)

## Démarrage

```bash
cd afritoken
npm install
npm run dev
```

Ouvrez http://localhost:3000.

## Pages

| Route | Description |
| --- | --- |
| `/` | Site vitrine (accueil) |
| `/conformite` | Conformité réglementaire BCEAO |
| `/investor` | Dashboard investisseur (Moussa Diallo) |
| `/investor/calculator` | Calculateur de rendement interactif |
| `/entreprise` | Dashboard entreprise (Green Mobility) |
| `/entreprise/candidature` | Formulaire candidature + scoring |
| `/admin` | Dashboard administrateur (démo BCEAO) |

## Données

Toutes les données de la démonstration sont fictives et centralisées dans
`data/mockData.ts`.

## Build production

```bash
npm run build
npm start
```
