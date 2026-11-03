# Kynetic — implementation plan

## Product approach
Kynetic is implemented as a frontend-only Next.js App Router prototype. A reusable authenticated shell provides the persistent workspace feel across evidence, career, assistant and settings routes. The product is intentionally non-linear: every module is directly navigable, and the dashboard offers contextual “pick up where you left off” prompts rather than a forced wizard.

## Design direction
- **Candidate styles**: Soft-Neon Productivity (0.07), Quiet Editorial SaaS (0.05), Learning OS Utility (0.08).
- **Chosen movement**: Soft-Neon Productivity — a calm, premium workspace with a dark ink canvas, luminous indigo/violet accents, and quiet data-dense surfaces.
- **Core principles**: evidence-first clarity; calm momentum; progressive disclosure; every action should feel reversible.
- **Color philosophy**: ink and mist neutrals keep the interface focused; indigo signals forward motion; teal confirms demonstrated capability; violet/amber marks project-backed evidence; coral is reserved for attention.
- **Layout paradigm**: a persistent left rail plus an asymmetric dashboard canvas, with one strong “next best move” panel balanced by compact evidence and progress modules.
- **Signature elements**: the Kynetic “orbit” mark; evidence pills with colored side rails; gradient capability rings and timeline connectors.
- **Interaction philosophy**: direct navigation, gentle hover lift, clear active states, and small status updates that reinforce momentum without gamification overload.
- **Animation**: 160–220ms ease-out transitions, subtle panel lift on hover, and a slow ambient glow on the hero orb only.
- **Typography system**: Geist/Inter-style UI sans with compact uppercase labels and a mono face for skill scores and technical snippets.
- **Brand essence**: a personal capability workspace for ambitious early-career builders, differentiated by evidence-aware progress. Personality: precise, encouraging, quietly confident.
- **Brand voice**: direct, warm, action-oriented. Examples: “Turn the work you’ve done into capability you can show.” / “One focused proof point at a time.”
- **Wordmark & logo**: an orbiting “K” formed by two offset arcs and a forward slash, paired with a compact lowercase wordmark.
- **Signature brand color**: electric indigo #6C63FF, used as the forward-motion signal.

## Project structure
- `app/`: App Router pages; landing, auth pages, design system, and a route-aware catch-all workspace page.
- `components/`: reusable shell, navigation, cards, charts, evidence badges and page sections.
- `lib/mocks/`: typed mock entities for user, capabilities, assessments, projects and activity.
- `lib/api/`: async API client façade over the typed mocks so screens do not import mocks directly.
- `public/manus-routes.json`: complete page route manifest for Preview.

## Build workflow
Use Next.js with strict TypeScript, Tailwind CSS, lucide-react and Recharts. The frontend uses no backend or secrets. Run diagnostics through the host-managed TypeScript registration, start the dev server on port 3000, verify the manifest and route rendering, then checkpoint the project on `main`.
