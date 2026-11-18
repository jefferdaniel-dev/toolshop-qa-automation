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
@checkout
Esquema del escenario: Comprar un producto según el tipo de acceso termina con pago exitoso y factura
  Dado que el usuario usa el acceso "<acceso>"
  Y que el usuario está en la tienda
  Cuando busca "<producto>"
  Y abre "<producto>" desde los resultados
  Y agrega el producto al carrito
  Y abre el carrito
  Entonces ve en el carrito "<producto>" con cantidad 1 y el mismo precio del detalle
  Cuando continúa la compra
  Y ingresa la dirección "<calle>" "<numero>" con código postal "<codigo_postal>" en "<pais>"
  Entonces la ciudad y el estado se autocompletan según el código postal
  Cuando paga con una tarjeta de prueba
  Entonces ve que el pago fue exitoso
  Cuando confirma el pedido
  Entonces recibe un número de factura

  @invitado
  Ejemplos: Invitado
    | producto           | acceso   | pais | codigo_postal | numero | calle        |
    | Thor Hammer        | invitado | CO   | 110321        | 15-88  | Carrera 6    |
    | Combination Pliers |          | NL   | 1071XX        | 1      | Museumstraat |

  @login
  Ejemplos: Login
    | producto           | acceso         | pais | codigo_postal | numero | calle                |
    | Thor Hammer        | login_checkout | US   | 10118         | 350    | 5th Avenue           |
    | Combination Pliers | login_home     | US   | 94043         | 1600   | Amphitheatre Parkway |
    | Cordless Drill 12V | login_home     | DE   | 11011         | 1      | Platz der Republik   |
```

La columna `acceso` decide cómo compra cada fila:

| Valor | Qué hace |
|---|---|
| `invitado` o vacío | Compra sin cuenta, con un comprador sintético al azar |
| `login_checkout` | Inicia sesión en el paso de login del checkout |
| `login_home` | Inicia sesión desde la home antes de buscar; el checkout ya reconoce la sesión |

## Evidencias

Cada escenario guarda capturas numeradas en el orden del flujo. Una compra exitosa queda así:

```
evidencias/2026-11-18/Thor-Hammer_2026-11-18_16-30-53_INV-2026000090/
├─ 01-home-…png
├─ 02-busqueda-…png
├─ 03-resultados-…png
├─ 04-producto-…png
├─ 05-carrito-…png
├─ 06-login-…png          # formulario lleno, contraseña enmascarada
├─ 07-direccion-…png
├─ 08-pago-…png
├─ 09-pago-exitoso-…png
└─ 10-factura-…png
```

Si una compra no llega a la factura, la carpeta queda sin el sufijo `INV-…`: se ve a simple vista qué corrida no terminó. `evidencias/` no se versiona.

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
| `npm run toolshop:checkout` | Compra completa (`@checkout`) |
| `npm run toolshop:invitado` | Compras como invitado (`@invitado`) |
| `npm run toolshop:login` | Compras con usuario registrado (`@login`) |

Filtros extra de pytest van después de `--`, por ejemplo `npm run toolshop:checkout -- -k "Thor"`. Sin navegador visible: `.venv\Scripts\python -m pytest`.

## Cómo se construyó

El proyecto se desarrolla con un flujo de agentes en Claude Code, una tarea a la vez:

- **HIRUZEN** (`/hiruzen`) toma la siguiente tarea del backlog y orquesta.
- **PICCOLO** la implementa con test primero: el escenario falla, luego el código mínimo lo hace pasar.
- Cuatro validadores revisan en paralelo: **ROCK LEE** corre la suite, **SHIKAMARU** el alcance, **FURY** la seguridad y **KAKASHI** las buenas prácticas.
- Si alguno falla, **JUEZ** diagnostica si la culpa es de la prueba, del producto o del entorno antes de reintentar (máximo dos veces).

La memoria del proyecto vive en `brain/`: `tasks.md` (backlog y criterios de aceptación), `decisions.md` (decisiones técnicas con su porqué) y `log.md` (bitácora). Las reglas de trabajo están en `CLAUDE.md`, y un hook (`.claude/hooks/guard.py`) bloquea acciones riesgosas: leer `.env`, opciones de pytest que imprimirían la contraseña, reescribir historia, y commits con secretos; además pide aprobación antes de publicar en GitHub.

## Próximas fases

1. **GitHub Actions:** la suite corre en cada push y a demanda, con el reporte como artefacto.
2. **Supabase:** historial de corridas.
3. **Dashboard en Next.js:** lanzar corridas y ver resultados desde el navegador.
4. **Docker:** imagen reproducible para correr igual en local y en CI.
