# Automatización QA de ecommerce

Suite de pruebas end-to-end sobre [Toolshop](https://practicesoftwaretesting.com): buscar, agregar al carrito y comprar (invitado o con usuario registrado) con tarjetas de prueba. Escenarios en Gherkin (español) con pytest-bdd, Playwright y Page Object Model. Está planeado un smoke de solo lectura sobre reuse.cl (decisión D12 en `brain/decisions.md`, tarea T6); aún no existe.

## Requisitos

- Windows (los scripts de `package.json` usan la ruta `.venv\Scripts\python`; en Linux/macOS no funcionan tal cual, la CI de la Fase 2 invocará pytest directamente).
- Python 3.15 y Node/npm (npm solo como lanzador, sin dependencias).

## Instalación

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install chromium
copy .env.example .env
```

Completa `.env` con `BASE_URL=https://practicesoftwaretesting.com` y un usuario de prueba en `TEST_USER_EMAIL` y `TEST_USER_PASSWORD`. `.env` no se versiona.

## Comandos

Todos abren el navegador visible (`--headed`).

| Comando | Qué corre |
|---|---|
| `npm run toolshop:all` | Toda la suite |
| `npm run toolshop:search` | Búsqueda (`@search`) |
| `npm run toolshop:cart` | Carrito (`@cart`) |
| `npm run toolshop:checkout` | Compra completa (`@checkout`) |
| `npm run toolshop:invitado` | Compra como invitado (`@invitado`, incluye la fila con acceso vacío) |
| `npm run toolshop:login` | Compra con usuario registrado (`@login`: `login_checkout` y `login_home`) |

Para agregar filtros u opciones de pytest, pásalos después de `--`:

```
npm run toolshop:checkout -- -k "Thor"
```

Sin navegador visible: `.venv\Scripts\python -m pytest -m checkout`.

## Evidencias

Cada escenario guarda capturas numeradas en `evidencias/<YYYY-MM-DD>/<producto>_<fecha-hora>/` (carpeta no versionada, decisión D21).

## Cómo seguir el trabajo

El plan vive en `brain/`: `tasks.md` (tareas y estado), `decisions.md` (decisiones) y `log.md` (bitácora). Se avanza una tarea a la vez con el comando `/hiruzen`; las reglas del proyecto están en `CLAUDE.md`.
