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

## 2026-11-18 · T1 intento 1
- PICCOLO: requirements.txt (pytest, pytest-bdd, pytest-playwright, python-dotenv fijados), tests/conftest.py, tests/features/home.feature, tests/steps/test_home.py, tests/pages/home_page.py, __init__.py. `pytest`: 1 passed.
- ROCK LEE, SHIKAMARU, FURY: PASS. KAKASHI: FAIL — locator CSS por prefijo `[data-test^="product-"]` en tests/pages/home_page.py:7 en vez de test-id/rol; observación: el step usa `home_page.page`.
- JUEZ: CULPA PRUEBA. Causa raíz: el prefijo `product-` también captura hijos de la tarjeta (`product-name`, `product-price`), así que `count()`/`nth()` futuros darían resultados erróneos. Corrección: `set_test_id_attribute("data-test")` en conftest y `get_by_test_id("product-name")`. `home_page.page` en el step se deja como observación. Reintento 1.

## 2026-11-18 · T1 done (reintento 1)
- PICCOLO: conftest con fixture autouse `set_test_id_attribute("data-test")`; POM con `get_by_test_id("product-name")`. Verificado en DOM: 9 `product-name` = 9 tarjetas.
- ROCK LEE, SHIKAMARU, FURY, KAKASHI: PASS. Verificación del orquestador: `pytest -q` → 1 passed.
- Observaciones no bloqueantes: `playwright` (transitiva) sin versión fijada en requirements.txt; el step accede a `home_page.page` para el título. Revisar si se repite en T2/T3.

## 2026-11-18 · Chromium completo
- Solo estaba descargado `chromium_headless_shell`; el Chromium con ventana estaba incompleto (faltaba chrome.exe), así que `--headed` fallaba. Se corrió `.venv/Scripts/python -m playwright install chromium`: `pytest --headed` → 1 passed. CI (Fase 2) debe incluir este paso.
