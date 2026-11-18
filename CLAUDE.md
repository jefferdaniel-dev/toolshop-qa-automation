# Reglas del proyecto

Proyecto: automatización QA de ecommerce. Suite principal en Toolshop (buscar → carrito → checkout completo con tarjetas de prueba, D14); smoke de solo lectura en reuse.cl (ver `brain/decisions.md` D12).
Stack: Python 3.15 (`.venv`), Playwright, pytest-bdd (Gherkin), POM. Fases futuras: GitHub Actions, Supabase, Next.js (v0 + Claude Design), Docker.

## Comunicación
- Español, directo, sin relleno. Explica un tecnicismo en una frase la primera vez.
- Agrupa las preguntas al usuario en un solo mensaje, ordenadas por lo que más bloquea.
- Si hay una forma más simple de lograr lo mismo, dilo antes de seguir.

## Flujo de trabajo
- Trabajo guiado por `brain/tasks.md`. Una tarea a la vez, vía `/hiruzen`.
- Leer `brain/decisions.md` y las últimas entradas de `brain/log.md` antes de empezar.
- Test primero (escenario que falla), luego el código mínimo que lo hace pasar.
- Al terminar: actualizar estado en `brain/tasks.md` y agregar entrada en `brain/log.md`.

## Grabaciones con codegen
- Los flujos de UI parten de una grabación del usuario con `playwright codegen`, guardada en `recordings/<id-tarea>.py`.
- La grabación es insumo, no código final: se convierte a POM + steps. Nunca se importa ni se copia tal cual.
- De la grabación se toman los locators; se reemplazan por rol/label/texto/test-id si el grabado es frágil.
- Si la tarea necesita una grabación y no existe, la tarea queda `blocked` y se le pide al usuario con el comando exacto.

## Alcance mínimo
- Implementar solo lo que pide el criterio de aceptación de la tarea actual.
- Sin archivos, funciones, parámetros, dependencias ni configuración que la tarea no use.
- Sin abstracciones especulativas ni "por si acaso".

## Seguridad
- Nunca leer, imprimir, copiar ni commitear `.env` ni secretos. Las variables se documentan en `.env.example` sin valores reales.
- Configuración (URL base, credenciales de prueba) siempre desde variables de entorno.
- Datos de prueba sintéticos; nunca datos reales de personas.
- Nunca poner datos sensibles en logs, URLs, capturas ni reportes.
- Solo se completan pagos en Toolshop con tarjetas de prueba (D14). En sitios reales (reuse.cl) nunca se llega al carrito ni al checkout.

## Código
- Gherkin en español (lo lee negocio); código e identificadores en inglés.
- Sin comentarios dirigidos a agentes ni notas de proceso en el código. Las instrucciones viven aquí y en `brain/`.
- Comentarios solo cuando expliquen un "por qué" no obvio.
- POM: la página expone acciones y consultas del dominio; sin aserciones dentro de los Page Objects.
- Los steps solo orquestan y verifican.
- Locators por rol, label, texto o test-id; nada de XPath ni clases de estilo.
- Sin `sleep`/timeouts fijos ni reintentos como parche: auto-wait y `expect` de Playwright.
- Un escenario, una intención. Escenarios independientes entre sí.

## Reportes de agentes
- Conclusión, no volcado. Evidencia citable (`ruta:línea` o archivo de evidencia).
- Separar lo confirmado de lo supuesto. Nunca reportar en verde lo que no se corrió.
- Si la premisa de la tarea es falsa, decirlo y detenerse.

## Git
- Nunca `git push` ni reescribir historia. Commits solo cuando el usuario lo pida.
