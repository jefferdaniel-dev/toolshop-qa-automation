# Log

## 2026-11-18 · Fase 0 — Fundación
- Creados: `CLAUDE.md`, `.claude/settings.json`, `.claude/agents/*`, `.claude/commands/next-task.md`, `brain/*`, `.gitignore`, `.env.example`.
- T1 bloqueada: falta la URL del ecommerce (`BASE_URL`).

## 2026-11-18 · Decisión de ejecución remota y preparación
- D4 aceptada: GitHub Actions como ejecutor; se elimina FastAPI. Fases renumeradas (1 tests, 2 Actions, 3 Supabase, 4 dashboard, 5 Docker).
- Registradas D5 (diseño con Claude Design), D6 (espera en front, pendiente), D7 (Python 3.13 en venv).
- Inventario: Python 3.15, Node 26, npm, git, gh (con sesión iniciada) instalados; faltan Docker, CLI Vercel, CLI Supabase; sin conectores Vercel/Supabase/v0.

## 2026-11-18 · Entorno, codegen y agentes
- Python 3.15 verificado con el stack de pruebas (D7); Chromium de Playwright descargado. P2 cerrada.
- Flujo con grabaciones de codegen (D8): `recordings/` agregado a `.gitignore`, reglas en `CLAUDE.md`, prerrequisito en `/next-task`.
- Revisados agentes personales previos; adoptados JUEZ y reglas de PICCOLO/reportes (D9). Nuevo agente `juez`; `/next-task` lo usa antes de reintentar y no reintenta si la culpa es del producto o el entorno.
- Modelo asignado a cada agente (D10).

## 2026-11-18 · Agentes renombrados
- `/next-task` → `/hiruzen`; executor → piccolo, qa-runner → rock-lee, reviewer-scope → shikamaru, reviewer-security → fury, reviewer-practices → kakashi; juez sin cambio. Colores por agente (D11).

## 2026-11-18 · Sitio objetivo
- URL definida: https://www.reuse.cl (Shopify). Revisado `robots.txt`: `/search` permitido; `/cart` y `/checkout` excluidos para rastreadores. Riesgos registrados en D12. No se arrancó ninguna tarea.

## 2026-11-18 · Cambio de sitio objetivo
- Suite principal pasa a Toolshop (practicesoftwaretesting.com); reuse.cl queda como smoke a demanda (nueva T6). D12 reescrita; T4 llega hasta el paso de pago sin confirmar. No se arrancó ninguna tarea.
