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
Las tareas T2–T4 y T6 parten de una grabación de codegen del usuario en `recordings/<id>.py` (ver D8).

### T1 · Entorno de pruebas base — `done`
Criterio de aceptación:
- `.venv` con Python 3.15 y `requirements.txt` con versiones fijadas de pytest, pytest-bdd y pytest-playwright.
- `tests/conftest.py` toma la URL base de la variable de entorno `BASE_URL`.
- Escenario `tests/features/home.feature`: "el usuario abre la tienda y ve la página principal" pasa con `python -m pytest`.

### T2 · Buscar producto — `pending`
Criterio de aceptación:
- Escenario: buscar un producto por nombre muestra resultados que contienen ese nombre.
- Page objects `HomePage` y `SearchResultsPage` en `tests/pages/`.

### T3 · Agregar producto al carrito — `pending`
Criterio de aceptación:
- Escenario: desde los resultados, abrir un producto y agregarlo; el carrito muestra el producto y cantidad 1.
- Page objects `ProductPage` y `CartPage`.

### T4 · Diligenciar checkout hasta el paso de pago — `pending`
Criterio de aceptación:
- Escenario: desde el carrito avanzar por el checkout, identificarse (cuenta de prueba desde variables de entorno o invitado, según ofrezca el sitio), llenar la dirección de facturación y llegar al paso de pago con el producto en el resumen.
- No se confirma el pedido.
- Datos de dirección ficticios en el escenario (tabla Gherkin); credenciales solo en `.env` y documentadas en `.env.example` sin valor.

### T5 · Evidencia en fallos — `pending`
Criterio de aceptación:
- Al fallar un escenario se guarda trace y screenshot en `test-results/`.
- En ejecución exitosa no se guardan.

### T6 · Smoke de reuse.cl — `pending`
Criterio de aceptación:
- Escenario con tag `@smoke_reuse`: abrir la home de `REUSE_URL` y buscar un término genérico muestra al menos un resultado.
- Sin carrito ni checkout. Excluido por defecto; solo corre a demanda (`-m smoke_reuse` o equivalente).
- `REUSE_URL` documentada en `.env.example` sin valor.

## Fases siguientes (se detallan al cerrar la anterior)
- Fase 2: GitHub Actions — CI en push/PR + ejecución a demanda (`workflow_dispatch`), reporte como artefacto.
- Fase 3: Supabase — tabla de corridas; el workflow guarda resultados; auth.
- Fase 4: Dashboard Next.js — diseño con Claude Design (D5), dispara el workflow, historial, experiencia de espera (D6).
- Fase 5: Docker — imagen reproducible para correr las pruebas local igual que en CI.
