# Backlog

Estados: `pending` · `in_progress` · `blocked` · `done`
Responsable: **usuario** (requiere tu cuenta, instalación con admin o datos privados) · **agente** (vía `/hiruzen`).

**Siguiente: T22.** Después, Fase 3. T6 en pausa por decisión del usuario (2026-11-19).

## Fase 0 — Preparación del entorno
Cada herramienta se instala justo antes de la fase que la usa.

| Id | Qué | Responsable | Se necesita en | Estado |
|---|---|---|---|---|
| P1 | `.env` con `BASE_URL=https://practicesoftwaretesting.com` (ver D12) y `TEST_USER_EMAIL`/`TEST_USER_PASSWORD` | usuario | Fase 1 | `done` |
| P2 | Python (se usa el 3.15 instalado, ver D7) + Chromium de Playwright | — | Fase 1 | `done` |
| P3 | Repo en GitHub (público): https://github.com/jefferdaniel-dev/toolshop-qa-automation | agente con `gh`, previa confirmación | Fase 3 | `done` |
| P4 | Cuenta Supabase + conector Supabase en Claude | usuario | Fase 4 | `pending` |
| P5 | Cuenta Vercel/v0 + conectores Vercel y v0 en Claude | usuario | Fase 5 | `pending` |
| P6 | Docker Desktop 4.100.1 (WSL2, por usuario) | usuario | Fase 2 | `done` |
| P7 | API key gratuita de Grok en `.env` (sin valor real en `.env.example`) | usuario | Fase 6 | `pending` |

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

### T6 · Smoke de reuse.cl — `blocked` (en pausa por decisión del usuario, 2026-11-19)
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

## Fase 2 — Docker

### T19 · Imagen Docker para correr las pruebas — `done`
Pedido del usuario (2026-11-24); comportamiento confirmado con él antes de escribir el criterio.
Criterio de aceptación:
- `Dockerfile` sobre `python:3.15-slim` (D30) que instala `requirements.txt` y Chromium con sus dependencias del sistema. `requirements.txt` fija `playwright==1.65.2`, la versión ya instalada en `.venv`.
- `.dockerignore` por lista permitida (todo excluido salvo lo que la imagen usa): `.env`, `recordings/`, `.git`, `.venv`, `evidencias/` y `reports/` nunca entran a la imagen.
- Scripts npm `toolshop:docker:build` (construye) y `toolshop:docker` (corre sin pantalla con `--rm` y `--env-file .env`). Los filtros van después de `--`, por ejemplo `npm run toolshop:docker -- -m search`.
- Sin argumentos no corre ninguna prueba: solo muestra los tags disponibles.
- Al correr con filtro, el reporte y las capturas quedan en `reports/` y `evidencias/` de la carpeta del proyecto.
- README: sección corta de Docker (requisito, construir, correr con filtro, aviso de que los valores de `.env` van sin comillas).
- Sin cambios en las pruebas. Validación solo con `-m search -k "Combination and Pliers"` (sin login; pytest no acepta espacios sueltos en `-k`).

### T20 · Cierre de observaciones de Docker — `done`
Origen: observaciones de FURY y KAKASHI en T19. Comportamiento confirmado con el usuario (2026-11-24).
Criterio de aceptación:
- En el contenedor, sin `-m` ni `-k` no corre ninguna prueba aunque se pasen otras opciones (p. ej. `npm run toolshop:docker -- -v`): termina con error y un mensaje que dice cómo elegir. Basta uno de los dos filtros. Sin argumentos sigue listando los tags con código 0. Los comandos locales (`toolshop:all` y demás) no cambian.
- Reportes y evidencias creados en el contenedor usan la hora de `America/Bogota` (`TZ` funciona en la imagen sin instalar `tzdata`, comprobado).
- El hook `.claude/hooks/guard.py` bloquea, sin preguntar, los comandos de Docker que podrían mostrar la contraseña: opciones filtrantes de pytest (`-l`, `--showlocals`, `--tb=long`, `--full-trace`, `--tracing`) en `docker run ... toolshop-qa`; `--entrypoint env` o `printenv`; `docker inspect`; y `docker exec` con `env` o `printenv`. Siguen pasando `npm run toolshop:docker:build`, `npm run toolshop:docker -- -m search -k "..."`, y `docker images`, `ps`, `build` y `history`.
- El hook se prueba pasándole comandos de ejemplo por stdin, sin ejecutarlos: primero los casos que hoy no bloquea, luego los mismos bloqueados. Editarlo pide la aprobación del usuario. Actualizar D25.
- Validación: la corrida sin filtro, `-m search -k "Combination and Pliers"`, y una con solo `-k` usando `--collect-only`. Sin login ni compra.
- README de Docker: ajustar la frase sobre correr sin argumentos.

### T21 · Reporte Allure en lugar de pytest-html — `done`
Pedido del usuario (2026-11-24): el reporte actual sale vacío y sin capturas. Causa confirmada: pytest-html 4.2.0 falla al abrirse desde una ruta con tilde (`pushState` con `unescape`). Comportamiento confirmado con el usuario. Reemplaza el reporte de T5.
Criterio de aceptación:
- `allure-pytest-bdd` fijado en `requirements.txt` y Allure 3 fijado en `package.json`; se quitan `pytest-html`, su opción en `pytest.ini` y el código que solo servía para él. Se mantiene la captura en fallos en `test-results/`.
- Cada escenario, pase o falle, muestra en el reporte sus pasos en Gherkin con las capturas de `evidencias/` adjuntas en el paso que las tomó. En un fallo se adjunta también la captura del momento.
- El reporte no muestra los argumentos de los pasos (fixtures), para que una clave pasada como dato no se filtre; sí la fila de `Ejemplos`. Tampoco el nombre del equipo, ni en claro ni codificado.
- La corrida (local y Docker) deja los resultados en una carpeta propia dentro de `reports/`, sin sobrescribir las anteriores y con el nombre de hoy (`<YYYY-MM-DD_HH-MM-SS>_<selección>`). `npm run toolshop:report`, en el PC, arma un HTML único y en español de la última corrida. La imagen Docker no lleva Node.
- El HTML abre bien con doble clic desde la ruta del proyecto (tiene tilde y espacios), verificado sin errores de JavaScript.
- El reporte usa los colores de Tokyo Night (variante Night, paleta publicada en `tokyo-night/tokyo-night-vscode-theme`) en fondo, texto, bordes, enlaces y estados (aprobado, fallido, roto), y abre siempre así aunque el sistema esté en modo claro. Los colores viven en un archivo CSS propio.
- Prueba de fuga: con una clave inventada en memoria y un fallo forzado (sin tocar login real), no aparece en resultados ni en el HTML.
- Los filtros del contenedor y las opciones bloqueadas por el hook siguen igual. Actualizar D24, D29 y README (stack, reporte, comandos, Docker).
- Validación: `-m search -k "Combination and Pliers"` en local y en Docker, más la sonda de fuga. Sin login ni compra.

### T22 · Cerrar fugas fuera del reporte y endurecer el hook — `pending`
Origen: observaciones de FURY y JUEZ en T20 y T21. Comportamiento confirmado con el usuario (2026-11-25).
Criterio de aceptación:
- Al fallar una prueba, los valores de `TEST_USER_PASSWORD` y `TEST_USER_EMAIL` salen como `***` en la consola de pytest y en los textos del reporte (mensajes, trazas y adjuntos de texto), en todas sus formas escapadas. El correo sigue visible en la captura `login` (D23). Variable ausente, vacía o solo espacios: sin cambios ni error.
- En el reporte, la ruta local del proyecto no aparece en mensajes ni trazas (queda relativa). En la consola no cambia.
- El login comprueba que el campo es `type=password` antes de escribir la clave.
- El hook bloquea, sin preguntar, en comandos de pytest, `toolshop:` y `docker run ... toolshop-qa`: `--tb` con cualquier valor que no sea `short`, `line`, `native` o `no` si la sonda demuestra que no filtran, `-o`/`--override-ini` con `addopts`, `-c`/`--config-file`, `--confcutdir`, `--noconftest` y `DEBUG=pw:*` (también con `$env:`, `export` y `docker -e`). No debe bloquear `-k`, `-m`, `--collect-only`, `--headed`, `-v`, `--lf`, `-x` ni los scripts npm.
- Hook roto, sin dejar al agente encerrado (acordado con el usuario, 2026-11-25):
  - Prevención: una edición con Edit o Write que deje `guard.py` (o el lanzador) con error de sintaxis se niega, comprobando el contenido resultante antes de guardar. El archivo vigente no cambia.
  - Modo degradado: un lanzador pequeño arranca `guard.py`; si no puede, se permite leer y buscar (salvo `.env`), editar solo `guard.py` pide aprobación, y todo lo demás (comandos y otras ediciones) se niega con un mensaje que dice la causa y cómo repararlo (`git restore .claude/hooks/guard.py` en la terminal del usuario).
  - Antes de construirlo, comprobar cómo trata Claude Code cada código de salida del hook y si `ask` llega a mostrarse en modo automático; si no se muestra, editar `guard.py` en modo degradado también se niega. La comprobación no puede dejar el hook real roto: se hace con copias o por stdin.
  - Límite aceptado: si falta `py -3.15` o se rompe el propio lanzador, repara el usuario.
  - Tocar `.claude/` pide la aprobación del usuario.
- El hook se prueba por stdin, sin ejecutar los comandos de ejemplo: primero los casos que hoy pasan, luego los mismos bloqueados; las tablas de T20 siguen con 0 desajustes y ninguna decisión se debilita frente a `HEAD`.
- Sondas con claves y correos inventados en una copia aislada, sin login real, buscando en la consola, los resultados, los adjuntos y el HTML con base64 decodificado.
- Actualizar D23, D25, D29 y README. Validación real: solo `-m search -k "Combination and Pliers"` en local y Docker.

## Fases siguientes (se detallan al cerrar la anterior)
Orden acordado con el usuario (2026-11-19). Meta: un sistema todo en uno para lanzar pruebas desde la web y recibir el resultado explicado de forma amigable.
- Fase 3: GitHub Actions — CI en push/PR + ejecución a demanda (`workflow_dispatch`), reporte como artefacto, revisando que no publique capturas sensibles.
- Fase 4: Supabase — tabla de corridas; el workflow guarda resultados; autenticación y login.
- Fase 5: Front en Vercel (Next.js) — diseño con Claude Design (D5), lanzar una prueba con pasos simples, dispara el workflow, historial, experiencia de espera (D6).
- Fase 6: Agente con LangGraph — usa la API gratuita de Grok para lanzar la prueba e interpretar el resultado.
- Fase 7: Evals — medir a cada agente del flujo con casos y resultados esperados.
- Fase 8: Skills y mejora cíclica — convertir partes del flujo en skills y volver a correr los evals para mejorarlos.
- Fase 9: Demo propia de ecommerce — tienda pequeña para practicar sin riesgo sobre un sitio real.
