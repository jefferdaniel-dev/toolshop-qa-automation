# Reglas del proyecto

Proyecto: automatización QA de ecommerce. Suite principal en Toolshop (buscar → carrito → checkout completo con tarjetas de prueba, D14); smoke de solo lectura en reuse.cl (ver `brain/decisions.md` D12).
Stack: Python 3.15 (`.venv`), Playwright, pytest-bdd (Gherkin), POM. Fases futuras: Docker, GitHub Actions, Supabase (auth), front en Vercel (Next.js, v0 + Claude Design), agente LangGraph con API de Grok, evals y skills.

## Comunicación
- Español, directo, sin relleno. Explica un tecnicismo en una frase la primera vez.
- Agrupa las preguntas al usuario en un solo mensaje, ordenadas por lo que más bloquea.
- Si hay una forma más simple de lograr lo mismo, dilo antes de seguir.

## Flujo de trabajo
- Trabajo guiado por `brain/tasks.md`. Una tarea a la vez, vía `/hiruzen`.
- Antes de escribir el criterio de una tarea nueva, confirmar con el usuario el comportamiento esperado en sus propias palabras; si el pedido admite dos lecturas, preguntar (lección de T14).
- Leer `brain/decisions.md` y las últimas entradas de `brain/log.md` antes de empezar.
- Test primero (escenario que falla), luego el código mínimo que lo hace pasar.
- Al validar se corre solo el escenario que se tocó, elegido con `-m <tag> -k "<texto de la fila>"`, sin comentar filas del `.feature`. Más de uno solo si la validación lo exige (p. ej. dos tipos de acceso seguidos), diciendo por qué. La suite completa solo si el usuario la pide.
- Al terminar: actualizar estado en `brain/tasks.md` y agregar entrada en `brain/log.md`.

## Validación proporcional
Prevalece sobre los pasos 7 y 9 de `/hiruzen` (decisión del usuario, 2026-11-25).
- Ronda completa (ROCK LEE, SHIKAMARU, FURY, KAKASHI) si el cambio toca el hook, credenciales, Docker, CI o lo que se publique (reportes, logs). FURY y ROCK LEE nunca se omiten ahí.
- En los demás cambios con código: ROCK LEE y uno más, el que corresponda al riesgo. Si solo cambia documentación: SHIKAMARU o KAKASHI.
- En un reintento repite quien dio FAIL y ROCK LEE si cambió algo que se ejecuta. Si el arreglo toca más archivos de los que dictó JUEZ, vuelve la ronda que correspondía.
- El orquestador siempre compara el informe con el diff y la salida real; no repite pruebas que ya corrió un validador, salvo que algo no cuadre o haya que confirmar un FAIL.
- Antes de empezar una tarea que vaya a pedir aprobaciones al usuario, avisarle cuántas se esperan y por qué.
- La lista de permisos de `settings.json` no se amplía para reducir solicitudes.

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
- Para forzar un fallo al validar, nunca usar credenciales incorrectas de una cuenta compartida (la cuenta demo se bloquea); provocar el fallo de otra forma, sin tocar el login.
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
- Commits, push y cualquier publicación en GitHub (`gh repo/pr/release`) solo cuando el usuario lo pida; `settings.json` y el hook `.claude/hooks/guard.py` siempre piden su aprobación.
- Nunca reescribir historia ni forzar push (el hook lo bloquea).
