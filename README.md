# Automatización QA de ecommerce · Toolshop

Suite end-to-end sobre [Toolshop](https://practicesoftwaretesting.com), una tienda hecha para practicar automatización. Cubre el recorrido completo de una compra: buscar un producto, agregarlo al carrito y pagarlo con una tarjeta de prueba hasta obtener la factura. Se puede comprar como invitado o con un usuario registrado, que inicia sesión en la home o en el checkout.

Los escenarios están escritos en Gherkin en español, para que los lea negocio, y el código en inglés.

## Qué demuestra

- **BDD con datos en los Ejemplos.** Producto, tipo de acceso y dirección viven en tablas `Ejemplos`; agregar un caso es agregar una fila, sin tocar código.
- **Page Object Model.** Las páginas exponen acciones y consultas; los steps orquestan y verifican. Sin aserciones dentro de las páginas.
- **Esperas por la API, no por tiempo.** Cada acción que dispara una petición espera la respuesta de la API correspondiente y verifica su status. Sin `sleep` ni reintentos como parche.
- **Locators estables.** Test-id (`data-test`), rol o texto; nada de XPath ni clases de estilo.
- **Evidencia por paso.** Cada escenario guarda una captura por pantalla; la carpeta de una compra exitosa lleva el número de factura.
- **Credenciales seguras.** El usuario de prueba sale de variables de entorno; nunca se imprime y la contraseña sale enmascarada en las capturas.
- **Hallazgos documentados.** La suite encontró tres comportamientos del sitio que vale la pena reportar (ver más abajo).

## Stack

| Pieza | Uso |
|---|---|
| Python 3.15 | Lenguaje de la suite |
| Playwright 1.65 | Navegador (Chromium) |
| pytest 9 + pytest-bdd 9 | Runner y Gherkin |
| python-dotenv | Configuración desde `.env` |
| npm | Solo como lanzador de comandos cortos, sin dependencias |

## Estructura

```
tests/
├─ features/        # Gherkin: home.feature, purchase.feature
├─ steps/           # Steps de pytest-bdd: orquestan y verifican
├─ pages/           # Page Objects: home, resultados, producto, carrito, login, checkout
├─ data/            # Compradores sintéticos y tarjetas de prueba
└─ conftest.py      # URL base, idioma del navegador, evidencias
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

Cada corrida deja su propio reporte `reports/<YYYY-MM-DD_HH-MM-SS>_<selección>.html` (autocontenido, se abre con doble clic; `<selección>` sale de `-m` y `-k`, o es `all`; no se sobrescriben). Si un escenario falla, la captura de la pantalla en ese momento queda incrustada en el reporte y en `test-results/`. No se guarda trace ni video. Ambas carpetas están fuera de git.

## Hallazgos de QA en Toolshop

1. **El código postal genera ciudades ficticias.** `GET /postcode-lookup` devuelve ciudad y estado inventados pero fijos por código postal (10001 → "Gianniburgh, New Hampshire"), y la creación de la factura rechaza con 422 cualquier otra ciudad, aunque sea la real. La suite escribe la calle real y verifica que el formulario muestre exactamente lo que devolvió la API.
2. **Una dirección del Reino Unido no se puede completar.** Para GB la API devuelve el estado vacío, pero el formulario lo exige y deja deshabilitado "Proceed to checkout".
3. **La precarga del perfil borra la dirección escrita.** Con sesión iniciada, el checkout pide el perfil del usuario y, si la respuesta llega tarde, sobrescribe los campos ya escritos. Con login desde la home el perfil puede pedirse dos veces. La prueba espera a que el perfil termine de cargar antes de escribir.

## Cómo correrlo

Requisitos: Windows, Python 3.15 y Node/npm. Los comandos de `npm` usan la ruta `.venv\Scripts\python`, propia de Windows.

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install chromium
copy .env.example .env
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

Filtros extra de pytest van después de `--`, por ejemplo `npm run toolshop:confirmacion -- -k "Thor"`. Sin navegador visible: `.venv\Scripts\python -m pytest`.

## Cómo se construyó

Diseñé un flujo de agentes en Claude Code, una tarea a la vez: **HIRUZEN** (`/hiruzen`) orquesta, **PICCOLO** implementa con test primero, cuatro validadores revisan en paralelo (**ROCK LEE** corre solo el escenario tocado, **SHIKAMARU** el alcance, **FURY** la seguridad, **KAKASHI** las buenas prácticas) y, si alguno falla, **JUEZ** dictamina si la culpa es de la prueba, del producto o del entorno antes de reintentar (máximo dos veces).

La memoria vive en `brain/` (backlog con criterios, decisiones con su porqué y bitácora), las reglas en `CLAUDE.md`, y un hook (`.claude/hooks/guard.py`) bloquea acciones riesgosas y pide aprobación antes de publicar en GitHub.

En [docs/proceso-con-ia.md](docs/proceso-con-ia.md) cuento el flujo con un diagrama, las reglas y su porqué, cifras sacadas de `brain/` y seis problemas reales: cómo se detectaron y cómo se resolvieron.

## Próximas fases

1. **GitHub Actions:** la suite corre en cada push y a demanda, con el reporte como artefacto.
2. **Supabase:** historial de corridas.
3. **Dashboard en Next.js:** lanzar corridas y ver resultados desde el navegador.
4. **Docker:** imagen reproducible para correr igual en local y en CI.
