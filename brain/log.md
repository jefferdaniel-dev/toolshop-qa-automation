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

## 2026-11-18 · Grabaciones T2–T4 limpias
- Grabación original del usuario (login → búsqueda → carrito → checkout → pago completo con tarjeta) respaldada en `recordings/raw_full_flow.py`.
- Limpieza: quitados login duplicado, clics/flechas repetidos, reescrituras de tarjeta y todo el paso de pago. Producto por nombre en vez de ULID. Credenciales vía `TEST_USER_EMAIL`/`TEST_USER_PASSWORD`.
- Dividida en `recordings/T2.py` (búsqueda), `T3.py` (carrito), `T4.py` (checkout hasta ver el método de pago, sin datos de tarjeta).
- Hallazgos de estabilidad (aplicar en POM/steps):
  1. Buscar antes de que la home termine de cargar pierde el texto: esperar a que haya productos visibles antes de buscar.
  2. Verificar resultados justo después de buscar lee la lista de la home (9 productos): esperar el conteo filtrado (`to_have_count(1)`) antes de verificar el texto.
- T2 y T3 limpias: 6/6 corridas en verde. T4 sin verificar (requiere credenciales en `.env`; el campo `street` no se llenó en la grabación, posiblemente precargado por la cuenta).

## 2026-11-18 · T2 intento 1
- PICCOLO: pytest.ini (marker search), tests/features/purchase.feature (Esquema @search, 3 productos), tests/pages/search_results_page.py, tests/steps/test_purchase.py; HomePage extendida con `search()`. pytest 4/4 en 4 corridas; `-m search` → 3 seleccionados.
- ROCK LEE, SHIKAMARU, FURY: PASS. KAKASHI: FAIL — `non_matching().to_have_count(0)` va antes de `first.to_be_visible()` y puede pasar en falso con la lista vacía; menores: Gherkin "tienda con productos visibles" poco declarativo, tabla desalineada, `product_names` duplicado en HomePage y SearchResultsPage.
- JUEZ: CULPA PRUEBA. El caption aparece antes de que la lista se filtre, así que no sirve como señal. La corrección de KAKASHI no basta: si el primer producto de la home ya contiene el término, `to_contain_text` pasa sobre la lista vieja. Corrección: en `search()`, esperar la respuesta de la API de búsqueda con `expect_response`; en el step, verificar primero `first.to_contain_text` y después que los no coincidentes sean 0; Gherkin "Dado que el usuario está en la tienda"; alinear la tabla. El `product_names` duplicado se deja (dos páginas distintas). Reintento 1.

## 2026-11-18 · T2 done (reintento 1)
- `HomePage.search()` con `expect_response` sobre `/products/search`; el step verifica `first.to_contain_text` y después `non_matching().to_have_count(0)`; Gherkin "Dado que el usuario está en la tienda"; se eliminó `caption`, que no se usaba.
- ROCK LEE (3/3 + `-m search` 3 seleccionados), SHIKAMARU, FURY, KAKASHI: PASS. Verificación del orquestador: 4 passed. Decisión D17.

## 2026-11-18 · T3 intento 1
- PICCOLO: tests/pages/product_page.py, tests/pages/cart_page.py; SearchResultsPage.open_product; Esquema @cart; marker cart. Precio del detalle (`unit-price`, sin "$") comparado con `product-price` del carrito; add-to-cart espera POST /carts 201. No evidenció el escenario en rojo antes del código. pytest 7/7 ×3.
- FURY: PASS. SHIKAMARU y KAKASHI: FAIL — `ProductPage.name` sin uso (product_page.py:9); KAKASHI sugiere mover la lectura del precio al POM. ROCK LEE: FAIL — 1 de 3 corridas con 6/7 fallos (home sin productos, `goto` timeout de 30 s), incluido T1 sin cambios.
- JUEZ: FAIL 1, CULPA PRUEBA → borrar `ProductPage.name`; la lectura del precio puede ir al POM (opcional). FAIL 2, CULPA ENTORNO → la API del sitio no respondió (categorías y tarjetas vacías, `goto` con timeout), probablemente por carga paralela de agentes. Mejora acorde con D17: `HomePage.open()` espera la respuesta de `/products` en lugar del `expect` de 5 s. Reintento 1, con revalidación de ROCK LEE en solitario.

## 2026-11-18 · T3 done (reintento 1)
- Se borró `ProductPage.name`; `ProductPage.loaded_price()` espera con `wait_for` y lee el precio; `HomePage.open()` espera la respuesta `/products` 200 (D17). La API del listado usa el método QUERY.
- ROCK LEE (7/7 ×3, incluso con corridas concurrentes), SHIKAMARU, FURY, KAKASHI: PASS. Verificación del orquestador: 7 passed.
- Observaciones no bloqueantes: `product_names` duplicado en HomePage y SearchResultsPage; los Given de home.feature y purchase.feature son casi iguales (unificar si aparece una tercera feature).

## 2026-11-18 · T4 intento 1
- PICCOLO (opus): tests/pages/checkout_page.py, tests/data/buyers.json (5), tests/data/cards.json (3, PlacetoPay aprobadas), Esquema @checkout, fixture `checkout_only_on_toolshop` (skip si el host no es Toolshop), `CartPage.proceed_to_checkout`, marker checkout. Hallazgo: Toolshop rellena ciudad y estado con `GET /postcode-lookup` y rechaza otros valores con 422, así que buyers.json no los trae. Rojo evidenciado. pytest 10/10 ×3.
- ROCK LEE (10/10 ×3 en serie; prints sin números), SHIKAMARU, FURY: PASS. KAKASHI: FAIL — (1) la espera del lookup (`checkout_page.py:41-54`) puede no ver una tercera petición, y `response()` puede ser None; (2) el escenario @checkout encadena carrito + pago + confirmación y repite los pasos de @cart; (3) el comentario de checkout_page.py:37-40 es confuso.
- FURY (baja): la protección depende del tag @checkout; con un skip, un BASE_URL mal configurado no se marcaría en rojo.
- JUEZ: CULPA PRUEBA, menor. El listener se registra antes de los fills y captura todas las peticiones; la propuesta de KAKASHI (un expect_response por fill) se descarta porque podría esperar 30 s si el debounce junta las peticiones. Aplicar: try/finally al quitar el listener, error claro si `response()` es None, comentario reducido al porqué, y justificar el escenario encadenado en D14. Reintento 1.
- Reintento 1 aplicado (try/finally, RuntimeError, comentario). Los 4 validadores dieron PASS (10/10 ×3).
- Verificación del orquestador: con `--headed` falla `get_by_role("tab", name="Continue as Guest")`, porque el navegador visible usa el idioma del sistema (español) y el headless usa inglés. Causa: el idioma del navegador no está fijado. Reintento 2: fijar `locale` en `browser_context_args`.
- Reintento 2: `browser_context_args` con `locale: "en-US"` (D18). ROCK LEE (headed 10/10, headless 10/10 ×2, checkout 3/3), SHIKAMARU, FURY, KAKASHI: PASS. Verificación del orquestador: `-m checkout -k Thor --headed` → 1 passed.

## 2026-11-18 · T4 done
- Suite: 10 escenarios (1 home + 3 @search + 3 @cart + 3 @checkout), en verde en headless y headed.
- Las sondas y corridas crearon facturas de invitado con datos sintéticos en Toolshop (sitio de práctica).
- Instrucción de FURY alineada con D14 (`.claude/agents/fury.md`).
