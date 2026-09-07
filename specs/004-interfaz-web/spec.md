# Especificación: Interfaz Web

**Rama/ID:** `004-interfaz-web`
**Estado:** Borrador
**Entrada:** "Despliegue operativo en una plataforma web accesible (sección 1 del product goal). Las tres capacidades del MVP —predicción, explicación y track record— describen comportamiento de usuario ('el usuario abre la ficha del partido', 'el usuario ve el panel') que ninguna feature cubría: 001, 002 y 003 entregan API, no producto."

## Historias de usuario

### Historia 1 — Encontrar el partido que me interesa (Prioridad: P1)
Como aficionado, quiero ver los partidos próximos de las cinco grandes ligas y poder filtrarlos por liga, para llegar rápido al que quiero consultar sin recorrer una lista larga.

**Por qué esta prioridad:** Es la puerta de entrada al producto. Sin ella no hay forma de llegar a ninguna de las otras dos vistas, por buenas que sean.
**Prueba independiente:** Se puede probar mostrando la lista con datos de partidos próximos y comprobando que el filtro por liga acota el resultado, sin que existan aún la ficha ni el panel.

**Escenarios de aceptación:**
1. **Dado** que hay partidos próximos cubiertos, **Cuando** el usuario abre la página principal, **Entonces** ve la lista con equipos, liga y fecha de cada partido, ordenada por proximidad al kickoff.
2. **Dado** que el usuario selecciona una liga, **Cuando** se aplica el filtro, **Entonces** la lista muestra solo partidos de esa liga y el filtro seleccionado queda visible.
3. **Dado** un partido que aún no tiene predicción generada, **Cuando** aparece en la lista, **Entonces** se distingue visualmente de los que sí la tienen, en vez de parecer idéntico.

### Historia 2 — Entender la predicción de un partido (Prioridad: P1)
Como aficionado o analista amateur, quiero abrir un partido y ver en una sola pantalla las cuatro señales, su nivel de confianza y la explicación de por qué el modelo predice eso, para juzgar la predicción en vez de aceptarla.

**Por qué esta prioridad:** Es donde se materializan los pilares 1 y 2 a la vez. Es la pantalla que justifica el producto.
**Prueba independiente:** Se puede probar abriendo un partido con predicción y explicación ya generadas, y comprobando que ambas se muestran juntas, sin depender de la lista ni del panel de track record.

**Escenarios de aceptación:**
1. **Dado** un partido con predicción generada, **Cuando** el usuario abre su ficha, **Entonces** ve las cuatro señales (1X2, Over/Under 2.5, BTTS, xG) y el badge de confianza en la misma vista, sin navegar a otra pantalla.
2. **Dado** que existe una explicación para esa predicción, **Cuando** el usuario la lee, **Entonces** cada pieza de evidencia citada se muestra con su titular y un enlace a la fuente, de modo que pueda verificarla por su cuenta.
3. **Dado** que el usuario quiere profundizar, **Cuando** envía una pregunta de seguimiento, **Entonces** recibe la respuesta en la misma vista, junto a la evidencia en la que se apoya.
4. **Dado** un partido cuya predicción tiene el aviso de datos insuficientes, **Cuando** el usuario abre la ficha, **Entonces** el aviso es visible antes que las probabilidades, no escondido al final.

### Historia 3 — Comprobar si el modelo acierta (Prioridad: P1)
Como usuario escéptico, quiero ver el desempeño histórico real del modelo y poder auditarlo partido a partido, para decidir cuánto crédito darle a sus predicciones.

**Por qué esta prioridad:** Es el pilar 3 y el diferencial declarado frente a la competencia (sección 3). Un track record que existe en la API pero no en pantalla no cumple la promesa de ser auditable "por cualquier usuario".
**Prueba independiente:** Se puede probar mostrando el panel con datos de partidos ya evaluados, sin depender de las otras dos vistas.

**Escenarios de aceptación:**
1. **Dado** que hay partidos evaluados, **Cuando** el usuario abre el panel, **Entonces** ve el desempeño de los tres mercados por separado, cada uno con su porcentaje de aciertos y sus métricas.
2. **Dado** que el usuario quiere verificar el agregado, **Cuando** consulta el detalle, **Entonces** ve partido a partido lo que se predijo junto a lo que ocurrió realmente.
3. **Dado** que la ventana abarca más de una versión del modelo, **Cuando** se muestra el agregado, **Entonces** la interfaz lo advierte en vez de presentar la serie como continua.

## Casos límite
- ¿Qué ve el usuario mientras los datos cargan? → Un estado de carga que preserve la estructura de la página, no una pantalla en blanco ni un salto de contenido cuando llegan los datos.
- ¿Qué pasa si la API no responde? → Se muestra un error que explica qué falló y ofrece reintentar; nunca una pantalla vacía que parezca "no hay partidos".
- ¿Qué pasa si un partido no tiene explicación generada todavía? → La ficha muestra las señales igual y declara que la explicación aún no está disponible. La ausencia de 002 no puede romper la vista de 001.
- ¿Qué pasa si aún no hay partidos evaluados para el track record? → El panel declara que todavía no hay muestra suficiente en vez de mostrar ceros, que se leerían como "el modelo falla siempre".
- ¿Qué pasa con un partido pospuesto que ya tenía predicción? → Se muestra con su estado marcado y la predicción original visible, coherente con RF-009 de 001.

## Requisitos funcionales

> Escritos en sintaxis **EARS**. El patrón de cada requisito está anotado entre paréntesis
> al final. Ver `CLAUDE.md` § Convenciones de documentación.

- **RF-001:** El sistema DEBE mostrar la lista de partidos próximos cubiertos, con equipos, liga y fecha de kickoff, ordenada por proximidad. *(ubiquitous)*
- **RF-002:** DONDE el usuario ha seleccionado una liga, el sistema DEBE mostrar únicamente los partidos de esa liga y mantener visible el filtro aplicado. *(optional feature)*
- **RF-003:** El sistema DEBE mostrar, en una sola vista de la ficha del partido, las cuatro señales de la predicción y su nivel de confianza. *(ubiquitous)*
- **RF-004:** El sistema DEBE mostrar cada pieza de evidencia citada por la explicación con su titular y un enlace a la fuente original. *(ubiquitous)*
- **RF-005:** El usuario DEBE poder enviar una pregunta de seguimiento sobre una explicación y ver la respuesta en la misma vista, junto a la evidencia en la que se apoya. *(ubiquitous)*
- **RF-006:** El sistema DEBE mostrar el track record público con los tres mercados por separado, y permitir auditar el detalle partido a partido. *(ubiquitous)*
- **RF-007:** MIENTRAS una petición a la API esté en curso, el sistema DEBE mostrar un estado de carga que preserve la estructura de la página. *(state-driven)*
- **RF-008:** SI una petición a la API falla, ENTONCES el sistema DEBE mostrar un mensaje que distinga el error de la ausencia de datos y ofrecer reintentar. *(unwanted behaviour)*
- **RF-009:** SI un partido no tiene predicción o explicación generada, ENTONCES el sistema DEBE declararlo explícitamente y seguir mostrando el resto de la información disponible. *(unwanted behaviour)*
- **RF-010:** CUANDO una predicción trae el aviso de datos insuficientes, el sistema DEBE mostrarlo antes que las probabilidades. *(event-driven)*
- **RF-011:** El sistema DEBE ser utilizable con teclado y con lector de pantalla en las tres vistas. *(ubiquitous)*

### Requisitos no funcionales

- **RNF-001:** Las tres vistas DEBEN alcanzar contraste AA de WCAG 2.1 y anunciar correctamente los cambios de estado (carga, error, resultado) a un lector de pantalla.
- **RNF-002:** El sistema DEBE ser usable en pantallas de 360 px de ancho en adelante; ninguna vista genera desplazamiento horizontal.
- **RNF-003:** El sistema NO DEBE exigir autenticación para ninguna de las tres vistas — la auditabilidad pública es el pilar 3 (RNF-003 de 003).

## Fuera de alcance

| Fuera de alcance | Dónde vive |
|---|---|
| Autenticación, cuentas y favoritos de equipos o ligas | `docs/project_spec.md` §2.2, requiere auth simple. Fuera del MVP |
| Heatmap de tiros y radar chart de estilo de juego | `docs/project_spec.md` §2.2, funcionalidades adicionales |
| Cualquier vista de cuotas o comparador de casas de apuestas | Prohibido — Artículo V y `docs/project_spec.md` §2.4 |
| Selector de línea de Over/Under distinta de 2.5 | El MVP cubre una sola línea (RF-002 de 001) |
| Selector de idioma | El MVP es español-only (decisión de 002) |
| Ventanas configurables del track record | El MVP fija 50 partidos (RF-006 de 003) |
| Cálculo de predicciones, explicaciones o métricas en el cliente | Esta feature **solo consume** las APIs de 001, 002 y 003. Nada de lógica de negocio en el frontend (Artículo I) |

## Definition of Done

Aplica la [DoD del equipo](../../docs/team-charter.md#6-definition-of-done-dod-inicial), **más**:

- [ ] Todas las tareas de `tasks.md` cerradas y cada RF cubierto por al menos una.
- [ ] Los tipos del cliente derivan de los contratos de `specs/00X-*/contracts/`; no hay una segunda definición de las respuestas de la API escrita a mano (Artículo VIII).
- [ ] Las tres vistas tienen sus estados de carga, error y vacío implementados y probados, no solo el camino feliz.
- [ ] Ninguna vista calcula probabilidades, métricas ni aciertos: todo viene de la API (Artículo I).
- [ ] Ninguna vista muestra cuotas de casas de apuestas (Artículo V).
- [ ] Navegación por teclado verificada y contraste AA comprobado en las tres vistas.
- [ ] Los escenarios de `quickstart.md` se ejecutaron manualmente.

## Entidades clave
Esta feature no persiste datos propios. Trabaja con las representaciones que devuelven las APIs de 001, 002 y 003: **Partido**, **Predicción**, **Explicación** (con su **Evidencia**) y **TrackRecord** (agregado por mercado y detalle partido a partido). Ver `data-model.md`.

## Criterios de éxito
- **CE-001:** Un usuario que llega a la página principal puede alcanzar la predicción de un partido concreto y su explicación sin instrucciones previas.
- **CE-002:** Las tres vistas se comportan correctamente ante API caída, datos ausentes y muestra insuficiente — verificable forzando cada caso.
- **CE-003:** El track record es consultable sin cuenta ni credenciales, desde un navegador limpio.

## Checklist de completitud del requisito
- [x] No quedan marcadores `[NECESITA CLARIFICACIÓN]`
- [x] Los requisitos funcionales usan sintaxis EARS, con el patrón anotado en cada uno
- [x] Existe una sección **Fuera de alcance** explícita, no solo menciones dispersas
- [x] Existe una **Definition of Done** que enlaza la del equipo y añade los criterios del feature
- [x] Hay requisitos no funcionales (accesibilidad, responsive, acceso público)
- [x] No hay detalles de implementación en historias, escenarios ni casos límite — el stack concreto vive en `plan.md`
- [x] Cada requisito está cubierto por al menos una tarea, verificado por `npm run audit:sdd`
- [x] Los criterios de éxito son medibles
- [x] Cada historia de usuario es probable de forma independiente
- [x] No hay features especulativas o "por si acaso"
