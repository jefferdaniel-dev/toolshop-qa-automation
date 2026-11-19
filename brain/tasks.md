# Backlog

Estados: `pending` · `in_progress` · `blocked` · `done`
Responsable: **usuario** (requiere tu cuenta, instalación con admin o datos privados) · **agente** (vía `/hiruzen`).

**Siguiente: T6.** Orden acordado con el usuario (2026-11-19): T15 → T16 → T17 → T5 → T18 → T6.

## Fase 0 — Preparación del entorno
Cada herramienta se instala justo antes de la fase que la usa.

| Id | Qué | Responsable | Se necesita en | Estado |
|---|---|---|---|---|
| P1 | `.env` con `BASE_URL=https://practicesoftwaretesting.com` (ver D12) y `TEST_USER_EMAIL`/`TEST_USER_PASSWORD` | usuario | Fase 1 | `done` |
| P2 | Python (se usa el 3.15 instalado, ver D7) + Chromium de Playwright | — | Fase 1 | `done` |
| P3 | Repo en GitHub (público): https://github.com/jefferdaniel-dev/toolshop-qa-automation | agente con `gh`, previa confirmación | Fase 2 | `done` |
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

### T5 · Captura en fallos + reporte HTML — `done`
Reporte HTML pedido por el usuario (2026-11-18). Sin trace ni video (decisión del usuario 2026-11-19): el trace graba la contraseña en texto plano (D25) y los videos no se quieren por ahora.
Criterio de aceptación:
- Al fallar un escenario se guarda una captura de la pantalla en el momento del fallo en `test-results/`.
- En ejecución exitosa no se guarda nada en `test-results/`.
- `pytest-html` fijado en `requirements.txt`; cada corrida deja un reporte HTML autocontenido (`--self-contained-html` en `pytest.ini`), con la captura incrustada en los escenarios fallidos.
- Un reporte por corrida, sin sobrescribir los anteriores, con nombre que identifica la corrida: `reports/<YYYY-MM-DD_HH-MM-SS>_<selección>.html`, donde `<selección>` sale de `-m` y `-k` saneados (p. ej. `compra_Cordless-and-login_home`) o `all` si no hay filtro (pedido del usuario, 2026-11-19).
- README: dónde queda el reporte.
- El reporte nunca muestra credenciales (sigue `--tb=short`; sin trace ni video).

### T6 · Smoke de reuse.cl — `pending`
Criterio de aceptación:
- Escenario con tag `@smoke_reuse`: abrir la home de `REUSE_URL` y buscar un término genérico muestra al menos un resultado.
- Sin carrito ni checkout. Excluido por defecto; solo corre a demanda (`-m smoke_reuse` o equivalente).
- `REUSE_URL` documentada en `.env.example` sin valor.

### T7 · Evidencias por módulo — `done`
Criterio de aceptación:
- Cada escenario (home, @search, @cart, @checkout) guarda capturas según D21: carpeta del día, subcarpeta `<producto>_<fecha-hora>` (o `home_<fecha-hora>` si no hay producto) y archivos `NN-<modulo>-<fecha-hora>.png` numerados en el orden del flujo.
- Módulos mínimos: home, busqueda (con el término escrito, antes de buscar), resultados, producto, carrito, invitado (formulario lleno, antes de enviar), direccion (llena, antes de continuar), pago (llena, antes de pagar), pago-exitoso, factura.
- `evidencias/` en `.gitignore`. Sin capturas dentro de los Page Objects con aserciones; los POM separan llenar y enviar donde haga falta.

### T8 · Direcciones reales en Ejemplos — `done` (cerrada por el usuario; observaciones de calidad pasan a T10)
Criterio de aceptación:
- El Esquema @checkout recibe la dirección desde `Ejemplos` (columnas país, código postal, número, calle) con al menos 5 direcciones reales verificadas: Carrera 6 15-88, 110321 (CO, Museo del Oro); 350 5th Avenue, 10118 (US, Empire State); 1600 Amphitheatre Parkway, 94043 (US, Googleplex); Museumstraat 1, 1071XX (NL, Rijksmuseum); Platz der Republik 1, 11011 (DE, Reichstag; reemplaza a GB por D22).
- La prueba escribe la calle real y verifica que ciudad y estado del formulario coincidan con la respuesta de `/postcode-lookup` (D19). `buyers.json` deja de traer dirección.

### T9 · Comprador invitado o registrado — `done`
Criterio de aceptación:
- Columna `tipo_comprador` (`invitado` | `registrado`) en los `Ejemplos` de @checkout, con al menos una fila de cada tipo.
- Registrado: login con `TEST_USER_EMAIL`/`TEST_USER_PASSWORD`; ambas documentadas sin valor en `.env.example`. Evidencia `login` con el formulario lleno, antes de entrar.
- Credenciales nunca impresas ni en capturas (la captura de login enmascara la contraseña o la omite).

### T10 · Refactor de verificación de status y steps — `done`
Origen: observaciones de KAKASHI y FURY al cierre de T8 y T9. Sin cambio de comportamiento; la suite sigue pasando igual.
Criterio de aceptación:
- Un solo helper de verificación de status reemplaza los asserts repetidos: guarda el status en una variable antes de comparar y el mensaje dice método y ruta, sin host ni query (pytest no debe imprimir la URL completa de la Response).
- Un único Given para abrir la tienda, compartido por `home.feature` y `purchase.feature`.
- Las esperas de `HomePage.open`, `HomePage.submit_search` y `CheckoutPage.fill_address` filtran por método HTTP y ruta exacta.
- El When "busca" solo actúa; la verificación de resultados queda solo en el Then.
- `CheckoutPage.invoice_path` declarado en `__init__` (observación de KAKASHI en T9).
- Evaluar separar el step de comprador invitado/registrado en dos (observación de KAKASHI en T9).
- Helper `open_store(page)` para no repetir abrir la home + status en `store_with_products` y en `login_home` (KAKASHI en T11).
- En `continue_checkout`, la segunda espera de `street` es redundante con `login_home`; confirmar con una sonda si `proceed-2` dispara otro `GET /users/me` con el perfil ya cargado y esperar ese efecto concreto (JUEZ en T11).
- `pytest.ini` con `addopts = --tb=short`; nunca `--tb=long`, `--showlocals` ni tracing en corridas con credenciales (FURY en T9: exponen la contraseña).

### T11 · Columna `acceso`: invitado, login en checkout o login en home — `done`
Pedido del usuario (2026-11-18). Reemplaza la columna `tipo_comprador` de T9. Login en home según `recordings/raw_full_flow.py` (`nav-sign-in` → email, password, `login-submit`).
Criterio de aceptación:
- Columna `acceso` en los `Ejemplos` de @checkout. Valores:
  - `invitado` o celda vacía: compra como invitado;
  - `login_checkout`: inicia sesión en el paso de login del checkout (comportamiento actual de `registrado`);
  - `login_home`: inicia sesión desde la home antes de buscar y en el checkout continúa ya autenticado.
  Al menos una fila de cada valor (una con celda vacía).
- Un valor desconocido falla con un mensaje claro.
- Evidencia `login` en ambos casos de login, formulario lleno antes de entrar; credenciales nunca impresas ni en capturas (D23).

### T12 · Comandos cortos con navegador visible + README — `done`
Pedido del usuario (2026-11-18): correr con `npm run toolshop:<algo>`.
Criterio de aceptación:
- `package.json` (sin dependencias) con scripts: `toolshop:all`, `toolshop:search`, `toolshop:cart`, `toolshop:checkout`, `toolshop:invitado`, `toolshop:login`. Todos con `--headed` y usando el Python de `.venv`.
- `--headed` solo en los scripts, no en `pytest.ini` (CI corre sin pantalla).
- `README.md` corto: qué es, requisitos, instalación, `.env` desde `.env.example`, tabla de comandos, dónde quedan las evidencias, y cómo seguir el trabajo (`brain/` + `/hiruzen`).

### T13 · ID de factura en la carpeta de evidencias — `done`
Pedido del usuario (2026-11-18).
Criterio de aceptación:
- Al confirmar una compra, la carpeta del escenario se renombra agregando el número de factura al final: `<producto>_<fecha-hora>_INV-…`.
- Si la compra no llega a factura, la carpeta queda con el nombre original.
- Actualizar D21.

### T14 · Una sola ventana de navegador por corrida — `done` (revertida 2026-11-19: el usuario quería un navegador por prueba, el comportamiento original; ver D27)
Pedido del usuario (2026-11-18): con `--headed`, hoy se abre y cierra una ventana por fila de `Ejemplos`; genera ruido.
Criterio de aceptación:
- Con `--headed`, toda la corrida usa una sola ventana: un contexto y una página compartidos por la sesión.
- Antes de cada escenario se limpian cookies, `localStorage` y `sessionStorage`, y se parte de `about:blank`; ningún escenario hereda carrito ni sesión del anterior.
- Sin `--headed` (CI) se mantiene un contexto aislado por prueba.
- Prueba de aislamiento: correr `-m login` seguido de `-m invitado` en la misma sesión (`-m "login or invitado"`) pasa, y el invitado no aparece autenticado.
- Evidencias por escenario sin cambios (D21). Registrar la decisión en `brain/decisions.md`.

### T15 · Columna `etapa` y tabla única de compra — `done`
Pedido del usuario (2026-11-19). Reemplaza los bloques `@login`/`@invitado`.
Criterio de aceptación:
- Una sola tabla de `Ejemplos` en el escenario de compra, con columnas `acceso` y `etapa`, y un comentario encima que explique cada valor de ambas.
- `etapa`: `checkout` llena todo (dirección y tarjeta), toma la captura `pago` y se detiene justo antes del clic en pagar, verificando que el botón esté habilitado; `confirmacion` paga, ve "Payment was successful", confirma y recibe factura `INV-`. Un valor desconocido falla con un mensaje claro.
- Al menos una fila de cada `acceso` (una vacía) y de cada `etapa`.
- Sin tags `@login`/`@invitado`. Scripts npm: `toolshop:checkout` (filas `checkout`), `toolshop:confirmacion` (filas `confirmacion`), `toolshop:login` y `toolshop:invitado` (filtro `-k`, la fila vacía cuenta como invitado). Verificar cada filtro con `--collect-only`.
- La protección "solo en Toolshop" sigue cubriendo el escenario. README: tabla de comandos y una línea sobre `etapa`. Actualizar D16, D20, D24.

### T16 · Capturas de `login_home`: home → login → home — `done`
Pedido del usuario (2026-11-19). Hoy la carpeta empieza en `01-login`.
Criterio de aceptación:
- Con `login_home`, las capturas empiezan `01-home` (tienda sin sesión), `02-login` (formulario lleno), `03-home` (tienda ya autenticada) y siguen igual.
- Los demás accesos no cambian.

### T17 · Nombres cortos de evidencias — `done`
Pedido del usuario (2026-11-19).
Criterio de aceptación:
- Carpeta: `evidencias/<YYYY-MM-DD>/<HH-MM-SS>_<tag>_<producto>[_<acceso>][_INV-n]`; `<tag>` es `etapa` en compra (`checkout`/`confirmacion`) y `search`/`cart`/`home` en los demás; `<acceso>` solo en compra.
- Capturas: `NN-<modulo>.png`.
- Actualizar D21.

### T18 · README: cómo se construyó con IA — `done`
Pedido del usuario (2026-11-19): a los reclutadores les interesa cómo se resolvieron los problemas, no solo el resultado. Formato elegido: opción B.
Criterio de aceptación:
- `docs/proceso-con-ia.md`: diagrama del flujo de agentes (HIRUZEN → PICCOLO → ROCK LEE/SHIKAMARU/FURY/KAKASHI → JUEZ → reintento), las reglas que se impusieron y por qué (TDD, nunca verde sin correr, alcance mínimo, hook de seguridad, validar solo lo tocado), cifras sacadas de `brain/` (tareas cerradas, reintentos, hallazgos de validadores) y una bitácora de 5–7 problemas reales contados como problema → cómo se detectó → qué se decidió → qué cambió, con enlace a la decisión (`brain/decisions.md`, D-n).
- Casos mínimos: método `QUERY` de Toolshop; carrera de la precarga del perfil (D23); `gh repo create --push` que saltó el deny y dio origen al hook (D25); T14 malinterpretada y revertida (D27/D28); captura en fallos que no funcionaba con pytest-bdd, hallada por un validador y diagnosticada por JUEZ (D29); cuenta demo bloqueada por un fallo forzado.
- README: sección "Cómo se construyó" con un resumen corto (3–5 líneas) y enlace al documento; corregir lo que haya quedado desactualizado en esa sección.
- Todo verificable contra `brain/log.md` y `brain/decisions.md`; nada inventado. Sin datos personales (nombre, correo), credenciales ni valores de `.env`. Diagrama en Mermaid (GitHub lo renderiza).

## Fases siguientes (se detallan al cerrar la anterior)
- Fase 2: GitHub Actions — CI en push/PR + ejecución a demanda (`workflow_dispatch`), reporte como artefacto.
- Fase 3: Supabase — tabla de corridas; el workflow guarda resultados; auth.
- Fase 4: Dashboard Next.js — diseño con Claude Design (D5), dispara el workflow, historial, experiencia de espera (D6).
- Fase 5: Docker — imagen reproducible para correr las pruebas local igual que en CI.
