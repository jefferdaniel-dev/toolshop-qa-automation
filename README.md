# Automatización QA de ecommerce · Toolshop

Suite end-to-end sobre [Toolshop](https://practicesoftwaretesting.com), una tienda hecha para practicar automatización. Cubre el recorrido completo de una compra: buscar un producto, agregarlo al carrito y pagarlo con una tarjeta de prueba hasta obtener la factura. Se puede comprar como invitado o con un usuario registrado, que inicia sesión en la home o en el checkout.

Los escenarios están escritos en Gherkin en español, para que los lea negocio, y el código en inglés.

## Qué demuestra

- **BDD con datos en los Ejemplos.** Producto, tipo de acceso y dirección viven en tablas `Ejemplos`; agregar un caso es agregar una fila, sin tocar código.
- **Page Object Model.** Las páginas exponen acciones y consultas; los steps orquestan y verifican. Sin aserciones dentro de las páginas.
- **Esperas por la API, no por tiempo.** Cada acción que dispara una petición espera la respuesta de la API correspondiente y verifica su status. Sin `sleep` ni reintentos como parche.
- **Locators estables.** Test-id (`data-test`), rol o texto; nada de XPath ni clases de estilo.
- **Evidencia por paso.** Cada escenario guarda una captura por pantalla; la carpeta de una compra exitosa lleva el número de factura.
- **Credenciales seguras.** El usuario de prueba sale de variables de entorno; la contraseña sale enmascarada en las capturas (el login lo comprueba antes de escribirla) y, si una prueba falla, la contraseña y el correo salen como `***` en la consola y en el reporte.
- **Reporte legible.** Allure con pasos en Gherkin, capturas y colores Tokyo Night, en un HTML único que no hace conexiones externas.
- **Reproducible en Docker.** La misma imagen, sin root y con la base fijada, para local y CI; sin filtro no corre nada.
- **CI sin secretos (en revisión).** Workflow de GitHub Actions para cada push y pull request a `main`, y a demanda; nunca con login. La primera corrida en GitHub está en diagnóstico.
- **Barreras de seguridad para agentes de IA.** Un hook revisa cada comando, y si se rompe solo deja leer y repararlo.
- **Hallazgos documentados.** La suite encontró tres comportamientos del sitio que vale la pena reportar (ver más abajo).

## Stack

| Pieza | Uso |
|---|---|
| Python 3.15 | Lenguaje de la suite |
| Playwright 1.65 | Navegador (Chromium) |
| pytest 9 + pytest-bdd 9 | Runner y Gherkin |
| python-dotenv | Configuración desde `.env` |
| Allure 3 + allure-pytest-bdd | Reporte HTML con pasos en Gherkin, capturas y colores Tokyo Night |
| Docker | Imagen para correr las pruebas sin navegador visible |
| GitHub Actions | CI y ejecución a demanda, con el reporte como artefacto |
| npm | Lanzador de comandos cortos y fuente de Allure (única dependencia) |

## Estructura

```
tests/
├─ features/        # Gherkin: home.feature, purchase.feature
├─ steps/           # Steps de pytest-bdd: orquestan y verifican
├─ pages/           # Page Objects: home, resultados, producto, carrito, login, checkout
├─ data/            # Compradores sintéticos y tarjetas de prueba
└─ conftest.py      # URL base, idioma del navegador, evidencias
scripts/            # report.py y tokyo-night.css: arman el reporte HTML
Dockerfile          # Imagen de las pruebas
.github/workflows/  # pruebas.yml: CI y ejecución a demanda
docs/               # Cómo se construyó con IA
brain/              # Backlog, decisiones y bitácora del proyecto
.claude/            # Agentes, orquestador y reglas de seguridad (ver "Cómo se construyó")
```

## Ejemplo de escenario

```gherkin
@compra
Esquema del escenario: Comprar un producto según el acceso y la etapa
  Dado que el usuario está en la tienda
  Y que el usuario usa el acceso "<acceso>"
  Y que la compra llega hasta la etapa "<etapa>"
  Cuando busca "<producto>"
  Y abre "<producto>" desde los resultados
  Y agrega el producto al carrito
  Y abre el carrito
  Entonces ve en el carrito "<producto>" con cantidad 1 y el mismo precio del detalle
  Cuando continúa la compra
  Y ingresa la dirección "<calle>" "<numero>" con código postal "<codigo_postal>" en "<pais>"
  Entonces la ciudad y el estado se autocompletan según el código postal
  Cuando llena la tarjeta de prueba
  Entonces la compra termina según la etapa

  # acceso:
  #   invitado o vacío = compra sin cuenta, con un comprador sintético al azar
  #   login_home       = inicia sesión desde la home antes de buscar
  #   login_checkout   = inicia sesión en el paso de login del checkout
  # etapa:
  #   checkout     = llena todo y se detiene antes de pagar (el botón de pagar queda habilitado)
  #   confirmacion = paga y obtiene factura
  Ejemplos:
    | producto           | acceso         | etapa        | pais | codigo_postal | numero | calle                |
    | Thor Hammer        | login_checkout | confirmacion | US   | 10118         | 350    | 5th Avenue           |
    | Cordless Drill 12V | login_home     | checkout     | DE   | 11011         | 1      | Platz der Republik   |
    | Thor Hammer        | invitado       | checkout     | CO   | 110321        | 15-88  | Carrera 6            |
    | Combination Pliers |                | confirmacion | NL   | 1071XX        | 1      | Museumstraat         |
```

La columna `acceso` decide cómo compra cada fila:

| Valor | Qué hace |
|---|---|
| `invitado` o vacío | Compra sin cuenta, con un comprador sintético al azar |
| `login_checkout` | Inicia sesión en el paso de login del checkout |
| `login_home` | Inicia sesión desde la home antes de buscar; el checkout ya reconoce la sesión |

La columna `etapa` decide hasta dónde llega:

| Valor | Qué hace |
|---|---|
| `checkout` | Llena dirección y tarjeta, toma la captura `pago` y se detiene antes de pagar, verificando que el botón de pagar esté habilitado |
| `confirmacion` | Paga, ve "Payment was successful", confirma y recibe la factura `INV-…` |

Un valor desconocido en cualquiera de las dos columnas hace fallar la fila con un mensaje claro.

## Evidencias

Cada escenario guarda capturas numeradas en el orden del flujo. Una compra exitosa queda así:

```
evidencias/2026-11-19/15-33-43_confirmacion_Thor-Hammer_login_checkout_INV-2026000011/
├─ 01-home.png
├─ 02-busqueda.png
├─ 03-resultados.png
├─ 04-producto.png
├─ 05-carrito.png
├─ 06-login.png          # formulario lleno, contraseña enmascarada
├─ 07-direccion.png
├─ 08-pago.png
├─ 09-pago-exitoso.png
└─ 10-factura.png
```

El nombre de la carpeta es `<hora>_<etapa o tag>_<producto>_<acceso>`; `search` y `cart` no llevan acceso y la home queda como `<hora>_home`.

Si una compra no llega a la factura, la carpeta queda sin el sufijo `INV-…`: se ve a simple vista qué corrida no terminó. `evidencias/` no se versiona.

## Reporte

Cada corrida deja sus resultados en `reports/<YYYY-MM-DD_HH-MM-SS>_<selección>/resultados` (`<selección>` sale de `-m` y `-k`, o es `all`; no se sobrescriben). Para verlos:

```
npm run toolshop:report
```

Arma, en el PC, un HTML único y en español de la última corrida en `reports/<corrida>/informe/index.html`, que se abre con doble clic. Cada escenario muestra sus pasos en Gherkin con las capturas adjuntas al paso que las tomó, y la fila de `Ejemplos`; si falla, también la captura del momento (que además queda en `test-results/`). El reporte no muestra los argumentos de los pasos ni el nombre del equipo, y reemplaza por `***` los valores de `TEST_USER_PASSWORD` y `TEST_USER_EMAIL` en mensajes, trazas y adjuntos de texto, y también en la consola de pytest (una clave que no esté en esas variables no se redacta, ni lo que se imprima con `-s`); en el reporte la ruta local del proyecto queda relativa. Tampoco hace peticiones a internet: se le quita la analítica de Google que Allure incluye. Usa los colores de Tokyo Night (`scripts/tokyo-night.css`) y abre siempre oscuro, aunque el sistema esté en modo claro. No se guarda trace ni video. `reports/` y `test-results/` están fuera de git.

## Hallazgos de QA en Toolshop

1. **El código postal genera ciudades ficticias.** `GET /postcode-lookup` devuelve ciudad y estado inventados pero fijos por código postal (10001 → "Gianniburgh, New Hampshire"), y la creación de la factura rechaza con 422 cualquier otra ciudad, aunque sea la real. La suite escribe la calle real y verifica que el formulario muestre exactamente lo que devolvió la API.
2. **Una dirección del Reino Unido no se puede completar.** Para GB la API devuelve el estado vacío, pero el formulario lo exige y deja deshabilitado "Proceed to checkout".
3. **La precarga del perfil borra la dirección escrita.** Con sesión iniciada, el checkout pide el perfil del usuario y, si la respuesta llega tarde, sobrescribe los campos ya escritos. Con login desde la home el perfil puede pedirse dos veces. La prueba espera a que el perfil termine de cargar antes de escribir.

## Cómo correrlo

Requisitos: Windows, Python 3.15 y Node/npm (Node arma el reporte). Los comandos de `npm` usan la ruta `.venv\Scripts\python`, propia de Windows.

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install chromium
copy .env.example .env
npm install
```

Completa `.env` con `BASE_URL=https://practicesoftwaretesting.com` y un usuario de prueba de Toolshop en `TEST_USER_EMAIL` y `TEST_USER_PASSWORD`. `.env` no se versiona.

Todos estos comandos abren el navegador visible:

| Comando | Qué corre |
|---|---|
| `npm run toolshop:all` | Toda la suite |
| `npm run toolshop:search` | Búsqueda (`@search`) |
| `npm run toolshop:cart` | Carrito (`@cart`) |
| `npm run toolshop:checkout` | Filas con `etapa` checkout (se detienen antes de pagar) |
| `npm run toolshop:confirmacion` | Filas con `etapa` confirmacion (pagan y obtienen factura) |
| `npm run toolshop:invitado` | Filas como invitado (incluye la celda de acceso vacía) |
| `npm run toolshop:login` | Filas con usuario registrado (`login_checkout` y `login_home`) |
| `npm run toolshop:report` | No corre pruebas: arma el HTML de la última corrida (ver Reporte) |

Filtros extra de pytest van después de `--`, por ejemplo `npm run toolshop:confirmacion -- -k "Thor"`. Sin navegador visible: `.venv\Scripts\python -m pytest`.

### Con Docker

Requisito: Docker Desktop. La imagen (`python:3.15-slim` con Chromium) no incluye `.env`: las variables se pasan al correr. En ese archivo los valores van sin comillas, porque Docker las tomaría como parte del valor.

```
npm run toolshop:docker:build
npm run toolshop:docker -- -m search -k "Combination and Pliers"
```

Corre sin pantalla y deja los resultados y las capturas en `reports/` y `evidencias/` del proyecto; la imagen no lleva Node, así que el HTML se arma después en el PC con `npm run toolshop:report`. Sin argumentos no corre pruebas: solo lista los tags. Con otras opciones pero sin `-m` ni `-k` (por ejemplo solo `-v`) termina con error pidiendo elegir; con uno de los dos basta. Reportes y evidencias usan la hora de Bogotá. Con varias palabras en `-k` hay que unirlas con `and`. `-k " "` y `-m " "` (solo espacios) cuentan como vacíos. El contenedor no corre como root (usuario 1000, o el que pases con `--user`), así que los archivos de `reports/` no quedan de root en Linux.

### En GitHub Actions

El workflow `.github/workflows/pruebas.yml` usa la misma imagen del `Dockerfile` y corre sin credenciales ni secretos (solo `BASE_URL`, pública).

- **Automático** (push o pull request a `main`): home y búsqueda, `-k "test_home or test_buscar"` (4 pruebas).
- **A demanda**: pestaña Actions, workflow "Pruebas", "Run workflow". Se elige el tag (`search`, `cart` o `compra`) y, si se quiere, un filtro (por ejemplo `Combination and Pliers`). Las filas con login nunca corren: el filtro se combina siempre con `not login`. El filtro solo admite letras, números, espacios y `_ . ( ) -`, con paréntesis balanceados.
- **Resultado**: el job queda en rojo si falla una prueba y siempre sube el artefacto `reporte-allure` (un HTML, 7 días). Descárgalo desde la página de la corrida y ábrelo en el navegador.

Aviso: este repositorio es público. Los artefactos los puede descargar cualquiera con una cuenta de GitHub, y los logs y el filtro que escribas también son públicos. No se suben las carpetas `evidencias/` ni `resultados/`, pero el HTML sí lleva las capturas (con datos sintéticos) y muestra rama, commit y URL de la corrida. Las pruebas con login no corren en CI.

## Cómo se construyó

La IA implementa, propone y revisa; yo decido qué se construye, detecto cuándo algo no es lo que quería y convierto los errores que se pueden repetir en reglas. La arquitectura de agentes viene de mi experiencia laboral y de estudiar distintos diseños de agentes, y sigue en evolución: faltan evals que midan a cada agente, skills y una evaluación cíclica para mejorarlos. La idea de las banderas `acceso` y `etapa` en los Ejemplos también es mía.

El flujo trabaja una tarea a la vez: **HIRUZEN** (`/hiruzen`) orquesta, **PICCOLO** implementa con test primero y validan **ROCK LEE** (corre solo lo tocado), **SHIKAMARU** (alcance), **FURY** (seguridad) y **KAKASHI** (buenas prácticas). La ronda completa es para lo que toca seguridad, Docker, CI o algo público; el resto pasa por menos agentes. Si alguno falla, **JUEZ** dictamina si la culpa es de la prueba, del producto o del entorno antes de reintentar (máximo dos veces). Cada agente tiene su modelo según el riesgo de lo que hace.

La memoria vive en `brain/` (backlog con criterios, decisiones con su porqué y bitácora), las reglas en `CLAUDE.md`, y un hook (`.claude/hooks/guard.py` lanza las reglas de `guard_rules.py`) bloquea acciones riesgosas y pide aprobación antes de publicar en GitHub; si las reglas no cargan, solo deja leer y buscar, y reparar `guard_rules.py` con aprobación.

En [docs/proceso-con-ia.md](docs/proceso-con-ia.md) cuento el flujo con diagramas, los modelos de cada agente, las barreras de seguridad, las reglas y su porqué, cifras sacadas de `brain/` y doce problemas reales: cómo se detectaron, cómo se resolvieron y qué aporté yo en cada uno.

## Próximas fases

La meta es un sistema todo en uno: lanzar pruebas desde la web y recibir el resultado explicado de forma amigable.

1. **Supabase:** historial de corridas, autenticación y login.
2. **Front en Vercel:** lanzar una prueba con pasos simples y ver el resultado de forma clara.
3. **Agente con LangGraph:** con la API gratuita de Grok, lanza la prueba e interpreta el resultado.
4. **Evals:** medir a cada agente con casos y resultados esperados.
5. **Skills y mejora cíclica:** convertir partes del flujo en skills y volver a correr los evals para mejorarlos.
