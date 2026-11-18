# Backlog

Estados: `pending` · `in_progress` · `blocked` · `done`
Responsable: **usuario** (requiere tu cuenta, instalación con admin o datos privados) · **agente** (vía `/hiruzen`).

## Fase 0 — Preparación del entorno
Cada herramienta se instala justo antes de la fase que la usa.

| Id | Qué | Responsable | Se necesita en | Estado |
|---|---|---|---|---|
| P1 | `.env` con `BASE_URL=https://practicesoftwaretesting.com` (ver D12) | usuario | Fase 1 | `pending` |
| P2 | Python (se usa el 3.15 instalado, ver D7) + Chromium de Playwright | — | Fase 1 | `done` |
| P3 | Repo en GitHub (público, para minutos ilimitados de Actions) | agente con `gh`, previa confirmación | Fase 2 | `pending` |
| P4 | Cuenta Supabase + conector Supabase en Claude | usuario | Fase 3 | `pending` |
| P5 | Cuenta Vercel/v0 + conectores Vercel y v0 en Claude | usuario | Fase 4 | `pending` |
| P6 | Docker Desktop (requiere admin y WSL2) | usuario | Fase 5 | `pending` |

Ya disponible: Git, Node/npm, GitHub CLI con sesión iniciada (scopes `repo`, `workflow`).

## Fase 1 — MVP tests (local)

Sitio principal: Toolshop (`BASE_URL`). Smoke secundario: reuse.cl (`REUSE_URL`), ver D12.
Las tareas T2–T4 y T6 parten de una grabación de codegen del usuario en `recordings/<id>.py` (ver D8). Grabaciones T2, T3 y T4 listas (T4 grabó login; se reemplaza por compra como invitado, D14).

### T1 · Entorno de pruebas base — `done`
Criterio de aceptación:
- `.venv` con Python 3.15 y `requirements.txt` con versiones fijadas de pytest, pytest-bdd y pytest-playwright.
- `tests/conftest.py` toma la URL base de la variable de entorno `BASE_URL`.
- Escenario `tests/features/home.feature`: "el usuario abre la tienda y ve la página principal" pasa con `python -m pytest`.

### T2 · Buscar producto (data-driven) — `done`
Criterio de aceptación:
- `tests/features/purchase.feature` con un `Esquema del escenario` tag `@search`: buscar `<producto>` muestra resultados y todos contienen ese nombre. `Ejemplos` con al menos 3 productos (p. ej. Thor Hammer, Combination Pliers, Cordless Drill 12V).
- Page Objects `HomePage` (búsqueda) y `SearchResultsPage` en `tests/pages/`.
- `pytest.ini` registra el marker `search`; `pytest -m search` corre solo estos escenarios.
- Esperas por estado (ver log "Grabaciones T2–T4 limpias"): la home con productos antes de buscar y el caption de búsqueda antes de verificar resultados.

### T3 · Agregar producto al carrito — `done`
Criterio de aceptación:
- En `purchase.feature`, `Esquema del escenario` tag `@cart` con los mismos `Ejemplos`: abrir `<producto>` desde los resultados, agregarlo y ver en el carrito el nombre, cantidad 1 y el mismo precio mostrado en el detalle.
- Page Objects `ProductPage` y `CartPage`. Marker `cart` registrado.

### T4 · Checkout completo con comprador y tarjeta aleatorios — `done`
Criterio de aceptación:
- En `purchase.feature`, `Esquema del escenario` tag `@checkout` con los mismos `Ejemplos`: comprar `<producto>` como invitado con un comprador aleatorio de `tests/data/buyers.json` (dirección incluida) y pagar con tarjeta aleatoria de `tests/data/cards.json`; ver "Payment was successful" y una factura `INV-`.
- Al menos 5 compradores sintéticos y 3 tarjetas de prueba (D15). Se imprime comprador y etiqueta de tarjeta, nunca el número.
- Page Object `CheckoutPage`. Marker `checkout` registrado.
- Protección: si `BASE_URL` no es el host de Toolshop, los escenarios `@checkout` no se ejecutan (skip con motivo explícito), para que nunca se pague en otro sitio (D12, D14).

### T5 · Evidencia en fallos — `pending`
Criterio de aceptación:
- Al fallar un escenario se guarda trace y screenshot en `test-results/`.
- En ejecución exitosa no se guardan.

### T6 · Smoke de reuse.cl — `pending`
Criterio de aceptación:
- Escenario con tag `@smoke_reuse`: abrir la home de `REUSE_URL` y buscar un término genérico muestra al menos un resultado.
- Sin carrito ni checkout. Excluido por defecto; solo corre a demanda (`-m smoke_reuse` o equivalente).
- `REUSE_URL` documentada en `.env.example` sin valor.

## Dudas para el usuario (2026-11-18)
1. Las tarjetas de PlacetoPay salen de una página de un integrador (docs.y.uno), no de la documentación oficial. ¿Las confirmas o tienes la lista oficial?
2. Toolshop aprueba cualquier tarjeta con formato válido, así que no se pueden probar rechazos. ¿Hace falta cubrir rechazos (mock de la API) o basta con el camino feliz?
3. Toolshop calcula la ciudad y el estado a partir del código postal (a veces con valores de relleno). Los compradores no traen ciudad ni estado. ¿Está bien así?
4. `recordings/raw_full_flow.py` y `recordings/T4.py` (con login) ya no se usan. ¿Se conservan o se borran? No están en git.
5. T2–T4 no están en ningún commit.

## Fases siguientes (se detallan al cerrar la anterior)
- Fase 2: GitHub Actions — CI en push/PR + ejecución a demanda (`workflow_dispatch`), reporte como artefacto.
- Fase 3: Supabase — tabla de corridas; el workflow guarda resultados; auth.
- Fase 4: Dashboard Next.js — diseño con Claude Design (D5), dispara el workflow, historial, experiencia de espera (D6).
- Fase 5: Docker — imagen reproducible para correr las pruebas local igual que en CI.
