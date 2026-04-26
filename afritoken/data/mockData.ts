// =============================================================
// AFRITOKEN — Données de démonstration (MVP BCEAO)
// Toutes les données ci-dessous sont fictives et destinées
// uniquement à la présentation de la plateforme pilote.
// =============================================================

export const PLATFORM = {
  name: "Afritoken",
  tagline: "Tokenize Africa's Future",
  subTagline:
    "La première plateforme de tokenisation d'actifs productifs pour les PME africaines",
  version: "Version Pilote — Avril 2026",
  agrement: "Dossier agrément BCEAO en cours",
};

export const HERO_STATS = [
  {
    value: 300_000_000,
    suffix: "FCFA",
    label: "Volume de la première levée pilote",
    formatted: "300M FCFA",
  },
  {
    value: 654,
    suffix: "",
    label: "Investisseurs sur la plateforme pilote",
    formatted: "654",
  },
  {
    value: 2,
    suffix: "%",
    label: "Rendement mensuel fixe garanti",
    formatted: "2%",
  },
  {
    value: 36,
    suffix: "mois",
    label: "Mois de durée de contrat",
    formatted: "36",
  },
];

export const HOW_IT_WORKS = [
  {
    step: 1,
    icon: "Building2",
    title: "L'entreprise candidate",
    description:
      "Green Mobility dépose son dossier. Nous vérifions 12 critères d'éligibilité en 10 jours ouvrables.",
  },
  {
    step: 2,
    icon: "Hexagon",
    title: "Émission des tokens",
    description:
      "300M FCFA = 300 000 tokens à 1 000 FCFA. Chaque token est enregistré sur la blockchain Stellar.",
  },
  {
    step: 3,
    icon: "Smartphone",
    title: "Les investisseurs achètent",
    description:
      "Via l'app Afritoken, à partir de 1 000 FCFA, via Wave ou Orange Money.",
  },
  {
    step: 4,
    icon: "ShieldCheck",
    title: "Fonds sécurisés en escrow",
    description:
      "L'argent va directement dans un compte bancaire séquestre. Ni Afritoken ni l'entreprise ne peut y accéder seul.",
  },
  {
    step: 5,
    icon: "Zap",
    title: "Distribution automatique",
    description:
      "Le smart contract distribue les dividendes le 1er de chaque mois. Automatiquement. Sans intervention humaine.",
  },
];

export const PILOT_PROJECT = {
  name: "Green Mobility Sénégal SARL",
  shortName: "Green Mobility",
  sector: "VTC Électrique — Dakar, Sénégal",
  totalRaise: 300_000_000,
  raised: 195_000_000,
  progressPercent: 65,
  monthlyYield: 2,
  durationMonths: 36,
  investors: 654,
  investorsTarget: 654,
  investorsCurrent: 423,
  daysLeft: 18,
  status: "Collecte en cours",
  vehicles: 55,
  monthlyGrossRevenue: 71_500_000,
  monthlyNetRevenue: 49_275_000,
  monthlyDividends: 6_000_000,
  monthlyReimbursementReserve: 8_333_333,
};

export const COMPARISON_TABLE = [
  { criterion: "Garanties requises", banque: "OUI", afritoken: "NON", banqueOk: false, afritokenOk: true },
  { criterion: "Délai", banque: "6 mois", afritoken: "6 semaines", banqueOk: false, afritokenOk: true },
  { criterion: "Capital minimum", banque: "100M FCFA", afritoken: "5M FCFA", banqueOk: false, afritokenOk: true },
  { criterion: "Rendement investisseur", banque: "4-6%/an", afritoken: "24%/an", banqueOk: false, afritokenOk: true },
  { criterion: "Remboursement capital", banque: "Non", afritoken: "Oui", banqueOk: false, afritokenOk: true },
  { criterion: "Traçabilité", banque: "Faible", afritoken: "Blockchain", banqueOk: false, afritokenOk: true },
];

export const COMPLIANCE_BADGES = [
  "Instruction N°001-01-2024 BCEAO",
  "Réglementation AMF-UMOA",
  "Normes AML/CFT GAFI",
  "Droit OHADA — Zone UEMOA",
];

export const UEMOA_COUNTRIES = [
  { code: "SN", name: "Sénégal", capital: "Dakar", x: 12, y: 36 },
  { code: "ML", name: "Mali", capital: "Bamako", x: 30, y: 35 },
  { code: "BF", name: "Burkina Faso", capital: "Ouagadougou", x: 48, y: 50 },
  { code: "CI", name: "Côte d'Ivoire", capital: "Yamoussoukro", x: 42, y: 70 },
  { code: "TG", name: "Togo", capital: "Lomé", x: 58, y: 75 },
  { code: "BJ", name: "Bénin", capital: "Porto-Novo", x: 64, y: 73 },
  { code: "NE", name: "Niger", capital: "Niamey", x: 60, y: 38 },
  { code: "GW", name: "Guinée-Bissau", capital: "Bissau", x: 8, y: 48 },
];

// =============================================================
// CONFORMITÉ
// =============================================================

export const REGULATORY_TIMELINE = [
  {
    status: "done",
    label: "Instruction N°001-01-2024 BCEAO",
    detail: "Analysée et intégrée dans la conception de la plateforme",
  },
  {
    status: "done",
    label: "Réglementation AMF-UMOA",
    detail: "Cadre Appel public à l'épargne pris en compte",
  },
  {
    status: "done",
    label: "Normes AML/CFT GAFI",
    detail: "Procédure KYC intégrée et auditée",
  },
  {
    status: "in-progress",
    label: "Dossier Sandbox BCEAO",
    detail: "En cours de soumission au comité d'innovation",
  },
  {
    status: "in-progress",
    label: "Agrément Établissement de Paiement",
    detail: "Dossier en préparation auprès de la BCEAO",
  },
  {
    status: "pending",
    label: "Agrément AMF-UMOA (SGP)",
    detail: "Étape suivante — agrément Société de Gestion de Portefeuille",
  },
];

export const NINE_SHIELDS = [
  {
    n: 1,
    title: "Compte Escrow Bancaire",
    description:
      "Tous les fonds sont logés sur un compte séquestre bancaire à double signature. Ni Afritoken ni l'entreprise ne peut y accéder seul.",
  },
  {
    n: 2,
    title: "Capteurs IoT en Temps Réel",
    description:
      "Les revenus de l'entreprise sont mesurés directement par capteurs IoT (GPS, compteurs, terminaux). Aucune déclaration manuelle.",
  },
  {
    n: 3,
    title: "Audit Mensuel Indépendant",
    description:
      "Un cabinet d'audit certifié certifie chaque mois les revenus avant distribution des dividendes.",
  },
  {
    n: 4,
    title: "Smart Contract Automatique",
    description:
      "La distribution des dividendes est exécutée par un smart contract sur Stellar — aucune intervention humaine possible.",
  },
  {
    n: 5,
    title: "Réserve d'Urgence Bloquée",
    description:
      "10M FCFA bloqués en permanence pour couvrir un mois de dividendes en cas d'incident.",
  },
  {
    n: 6,
    title: "Réserve Progressive de Remboursement",
    description:
      "Chaque mois, l'entreprise alimente une réserve dédiée au remboursement du capital à l'échéance des 36 mois.",
  },
  {
    n: 7,
    title: "Assurance Responsabilité Civile",
    description:
      "Couverture de l'activité par une police d'assurance professionnelle souscrite auprès d'un assureur agréé.",
  },
  {
    n: 8,
    title: "Droit de Vote Collectif",
    description:
      "Les détenteurs de tokens votent les décisions stratégiques (audit complémentaire, suspension, etc.) à la majorité simple.",
  },
  {
    n: 9,
    title: "Contrat Légal Contraignant",
    description:
      "Chaque investisseur signe un contrat conforme au droit OHADA, exécutoire devant les juridictions UEMOA.",
  },
];

export const REGULATORY_DOCS = [
  {
    title: "Instruction N°001-01-2024 BCEAO",
    description: "Cadre des actifs numériques en zone UEMOA",
    type: "Référence officielle",
  },
  {
    title: "Règlement AMF-UMOA",
    description: "Encadrement de l'appel public à l'épargne",
    type: "Référence officielle",
  },
  {
    title: "Guide AML/CFT Afritoken",
    description: "Procédures internes de lutte anti-blanchiment",
    type: "Document interne",
  },
  {
    title: "Modèle de contrat investisseur",
    description: "Template juridique conforme OHADA",
    type: "Template",
  },
];

// =============================================================
// INVESTISSEUR — Moussa Diallo
// =============================================================

export const INVESTOR = {
  firstName: "Moussa",
  lastName: "Diallo",
  email: "moussa.diallo@email.com",
  kycVerified: true,
  tokens: 500,
  capitalInvested: 500_000,
  investmentDate: "2026-01-01",
  monthsRemaining: 33,
  monthlyDividend: 10_000,
  totalReceived: 30_000,
  projectedTotalGain: 360_000,
  reimbursementDate: "2029-01-01",
  nextDividendDate: "2026-05-01",
};

export const INVESTOR_TOKENS = [
  {
    project: "Green Mobility VTC",
    tokens: 500,
    capital: 500_000,
    yieldRate: "2%/mois",
    nextDividend: "2026-05-01",
    status: "Actif",
  },
];

export const INVESTOR_DIVIDEND_HISTORY = [
  { date: "2026-04-01", project: "Green Mobility", amount: 10_000, status: "Reçu", txn: "TXN-2026-04-001" },
  { date: "2026-03-01", project: "Green Mobility", amount: 10_000, status: "Reçu", txn: "TXN-2026-03-001" },
  { date: "2026-02-01", project: "Green Mobility", amount: 10_000, status: "Reçu", txn: "TXN-2026-02-001" },
];

// Génère 36 mois (Jan 2026 → Dec 2028) — 3 réels, 33 projetés
export const INVESTOR_DIVIDEND_TIMELINE = (() => {
  const data: { month: string; received: number | null; projected: number; cumulative: number }[] = [];
  let cumulative = 0;
  const start = new Date(2026, 0, 1);
  for (let i = 0; i < 36; i++) {
    const d = new Date(start.getFullYear(), start.getMonth() + i, 1);
    const monthLabel = d.toLocaleDateString("fr-FR", { month: "short", year: "2-digit" });
    cumulative += 10_000;
    const isReceived = i < 3;
    data.push({
      month: monthLabel,
      received: isReceived ? cumulative : null,
      projected: cumulative,
      cumulative,
    });
  }
  return data;
})();

export const SECONDARY_MARKET_OFFERS = [
  { seller: "F. Traoré", project: "Green Mobility", tokens: 50, price: 1_020, total: 51_000 },
  { seller: "A. Sow", project: "Green Mobility", tokens: 100, price: 1_015, total: 101_500 },
  { seller: "K. Ndiaye", project: "Green Mobility", tokens: 25, price: 1_025, total: 25_625 },
];

// =============================================================
// ENTREPRISE — Green Mobility
// =============================================================

export const COMPANY = {
  legalName: "Green Mobility Sénégal SARL",
  shortName: "Green Mobility",
  director: "Ibrahima Sow",
  ninea: "123456789",
  sector: "VTC Électrique",
  status: "Collecte en cours",
};

export const COMPANY_REVENUE_HISTORY = [
  {
    month: "Avril 2026",
    declared: 71_500_000,
    iot: 71_500_000,
    gap: 0,
    dividends: 6_000_000,
    status: "En cours",
  },
  {
    month: "Mars 2026",
    declared: 68_200_000,
    iot: 68_200_000,
    gap: 0,
    dividends: 6_000_000,
    status: "Versé",
  },
  {
    month: "Février 2026",
    declared: 65_800_000,
    iot: 65_800_000,
    gap: 0,
    dividends: 6_000_000,
    status: "Versé",
  },
  {
    month: "Janvier 2026",
    declared: 71_100_000,
    iot: 71_100_000,
    gap: 0,
    dividends: 6_000_000,
    status: "Versé",
  },
];

export const FUND_USAGE = [
  { name: "Achat de 55 voitures électriques", value: 275_000_000, percent: 91.7, color: "#1B5E20" },
  { name: "Fonds de roulement", value: 15_000_000, percent: 5.0, color: "#F9A825" },
  { name: "Réserve d'urgence", value: 10_000_000, percent: 3.3, color: "#2E7D32" },
];

export const COMPANY_IOT = {
  activeVehicles: 55,
  detectedTrips: 85_800,
  estimatedRevenue: 71_500_000,
};

// =============================================================
// CANDIDATURE — Secteurs éligibles
// =============================================================

export const ELIGIBLE_SECTORS = [
  { value: "vtc-electrique", label: "VTC Électrique", priority: "A" },
  { value: "transport-marchandises", label: "Transport de marchandises", priority: "A" },
  { value: "agro-industrie", label: "Agro-industrie", priority: "A" },
  { value: "energie-renouvelable", label: "Énergie renouvelable", priority: "A" },
  { value: "logistique", label: "Logistique & cold chain", priority: "B" },
  { value: "telecoms", label: "Télécoms & connectivité", priority: "B" },
  { value: "industrie", label: "Industrie manufacturière", priority: "B" },
  { value: "fintech", label: "Fintech & paiement", priority: "B" },
];

// =============================================================
// ADMIN — Dashboard BCEAO
// =============================================================

export const ADMIN_KPIS = {
  aum: 195_000_000,
  activeInvestors: 423,
  activeCompanies: 1,
  distributionsCount: 3,
  totalDistributed: 18_000_000,
  afritokenRevenue: 47_000_000,
};

export const RECENT_TRANSACTIONS = [
  { date: "2026-04-01 14:32", investor: "M. Diallo", type: "Dividende reçu", amount: 10_000, hash: "0x4f3d8a91c2b1", status: "ok" },
  { date: "2026-04-01 14:31", investor: "F. Traoré", type: "Dividende reçu", amount: 25_000, hash: "0x8c1ee93af3d2", status: "ok" },
  { date: "2026-04-01 14:30", investor: "A. Sow", type: "Dividende reçu", amount: 5_000, hash: "0x2a9b71f8c4e5", status: "ok" },
  { date: "2026-04-01 14:30", investor: "K. Ndiaye", type: "Dividende reçu", amount: 15_000, hash: "0x9d4c7e1a2b3f", status: "ok" },
  { date: "2026-04-01 14:29", investor: "S. Camara", type: "Dividende reçu", amount: 8_000, hash: "0x6e2f43a1d7c8", status: "ok" },
  { date: "2026-04-01 14:28", investor: "B. Diop", type: "Dividende reçu", amount: 20_000, hash: "0x1a5b8c3e9f4d", status: "ok" },
  { date: "2026-04-01 14:28", investor: "M. Bah", type: "Dividende reçu", amount: 12_000, hash: "0xf3a92d6c4e7b", status: "ok" },
  { date: "2026-04-01 14:27", investor: "O. Mané", type: "Dividende reçu", amount: 7_500, hash: "0xb84e2c7f1a9d", status: "ok" },
  { date: "2026-04-01 14:26", investor: "I. Kane", type: "Dividende reçu", amount: 18_000, hash: "0x57c1d3e8a4b6", status: "ok" },
  { date: "2026-04-01 14:25", investor: "P. Sène", type: "Dividende reçu", amount: 6_000, hash: "0xe9b2f6a3c1d8", status: "ok" },
];

export const TOTAL_TRANSACTIONS = 1962;

export const KYC_RECENT = [
  { investor: "M. Diallo", date: "2026-01-15", document: "CNI Sénégal", status: "Validé" },
  { investor: "F. Traoré", date: "2026-01-18", document: "CNI Mali", status: "Validé" },
  { investor: "A. Sow", date: "2026-01-22", document: "Passeport SN", status: "Validé" },
  { investor: "K. Ndiaye", date: "2026-02-03", document: "CNI Sénégal", status: "Validé" },
  { investor: "S. Camara", date: "2026-02-09", document: "CNI Côte d'Ivoire", status: "Validé" },
];

export const KYC_STATS = {
  verified: 423,
  suspicious: 0,
  blacklisted: 0,
  amlCompliance: 100,
};

export const ESCROW_ACCOUNT = {
  bank: "BSIC Sénégal",
  totalBalance: 195_000_000,
  availableForCompany: 178_333_334,
  reimbursementReserve: 13_333_333,
  emergencyReserve: 10_000_000,
  lastMovement: { date: "2026-04-01", type: "Distribution", amount: 6_000_000 },
  nextDistribution: "2026-05-01",
};

export const AUDIT_HISTORY = [
  { month: "Avril 2026", auditor: "Cabinet Audit Sénégal", revenue: 71_500_000, gap: 0, status: "En cours" },
  { month: "Mars 2026", auditor: "Cabinet Audit Sénégal", revenue: 68_200_000, gap: 0, status: "Certifié" },
  { month: "Février 2026", auditor: "Cabinet Audit Sénégal", revenue: 65_800_000, gap: 0, status: "Certifié" },
];

export const COMPANIES_PIPELINE = [
  { name: "Green Mobility", sector: "VTC Électrique", score: 91, status: "active", note: "Active" },
  { name: "Transport Dakar SA", sector: "Transport", score: 67, status: "conditional", note: "Conditionnel" },
  { name: "Restaurant Le Baobab", sector: "Restauration", score: 42, status: "rejected", note: "Rejeté" },
];

export const FRAUD_ALERT = {
  date: "2026-04-01 09:15",
  declared: 50_000_000,
  measured: 71_500_000,
  gapPercent: 30,
  actions: [
    "Distribution suspendue immédiatement",
    "Auditeur notifié par email",
    "Entreprise mise en demeure",
    "Investisseurs informés",
  ],
};

// =============================================================
// HELPERS
// =============================================================

export function formatFCFA(amount: number, options?: { compact?: boolean }) {
  if (options?.compact && amount >= 1_000_000) {
    if (amount >= 1_000_000_000) return `${(amount / 1_000_000_000).toFixed(1)}Md`;
    return `${(amount / 1_000_000).toFixed(amount % 1_000_000 === 0 ? 0 : 1)}M`;
  }
  return new Intl.NumberFormat("fr-FR").format(amount);
}

export function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}
