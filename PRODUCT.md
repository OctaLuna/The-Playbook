# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js 15 (App Router) + TypeScript en modo estricto, Tailwind CSS + shadcn/ui, TanStack Query para estado de servidor/caché/reintentos. Recharts únicamente para series del track record. Decidido en `specs/004-interfaz-web/plan.md` §7.1 y `docs/project_spec.md` — no es una decisión abierta de este init.

## Users

Aficionados y analistas amateur de fútbol que quieren **entender, no solo adivinar**, qué puede ocurrir en un partido. Llegan sin cuenta ni credenciales (RNF-003, público sin autenticación) y se dividen en tres momentos de uso, uno por historia de usuario de `spec.md`:

- Encontrar un partido próximo de las cinco grandes ligas (Premier League, LaLiga, Serie A, Bundesliga, Ligue 1) y filtrarlo por liga.
- Abrir la ficha de un partido para juzgar la predicción del modelo, no solo aceptarla — leer las cuatro señales, el nivel de confianza y la explicación con evidencia verificable, y poder preguntar más.
- Auditar el desempeño histórico real del modelo, partido a partido, como usuario escéptico que decide cuánto crédito darle.

## Product Purpose

The Playbook predice resultados de fútbol (1X2, Over/Under 2.5, BTTS, xG), explica cada predicción en lenguaje natural con evidencia verificable y anterior al kickoff, y publica su propio track record para que cualquiera lo audite. El frontend es la única superficie de producto de las tres capacidades — sin él, 001/002/003 son API, no producto (`spec.md`, sección "Entrada").

Éxito: un usuario que llega a la página principal alcanza la predicción de un partido concreto y su explicación sin instrucciones previas (CE-001); las tres vistas se comportan correctamente ante API caída, datos ausentes y muestra insuficiente (CE-002); el track record es consultable sin cuenta desde un navegador limpio (CE-003).

## Positioning

No es una casa de apuestas ni un comparador de cuotas — es una plataforma que hace su propio desempeño auditable en público, partido a partido, y que nunca oculta una predicción fallida. El diferencial no es la predicción en sí (cualquiera puede predecir), es la combinación de explicación verificable (evidencia con fuente, fecha y enlace, siempre anterior al kickoff) más track record público sin filtrar los errores. Un competidor que solo muestra "aciertos" o que mezcla evidencia con opinión no puede copiar esto sin romper su propio modelo de negocio.

## Operating Context

Navegador de escritorio o mobile, sin instalar nada, sin cuenta. El recorrido esperado es lineal: lista → filtro por liga → ficha del partido → explicación → pregunta de seguimiento → track record. Las tres vistas deben sobrevivir independientemente: 002 (explicación) y 003 (track record) son degradables — la ficha funciona sin explicación, el panel declara muestra insuficiente — pero 001 (predicción) es bloqueante: sin `Predicción` no hay nada que mostrar en la ficha.

El backend (FastAPI) puede no estar disponible o no tener datos reales todavía durante el desarrollo del frontend — es esperable trabajar contra los ejemplos de `contracts/*.md` antes de que 001/002/003 sirvan datos reales (`plan.md` §"Orden de creación de archivos").

## Capabilities and Constraints

**El frontend solo presenta y pide datos — nunca calcula.** Ninguna vista calcula probabilidades, métricas, aciertos, confianza ni explicaciones, y ninguna dispara generación de predicciones, entrenamiento o reindexado (Artículo I de la constitución del proyecto). Todo dato mostrado viene ya calculado de `GET /api/leagues`, `/api/matches/*`, `/api/matches/{id}/explanation*` y `/api/track-record*`.

**Prohibido de forma dura, no solo por omisión** (Artículo V + `docs/project_spec.md` §2.4): ningún comparador de casas de apuestas, ninguna cuota cruda expuesta — el track record solo muestra `avg_market_log_loss`/`market_implied_1x2` como referencia agregada de baseline, nunca una cuota por casa.

**Fuera de alcance del MVP** (no construir, no dejar puerta entreabierta): autenticación/cuentas/favoritos, selector de idioma (español-only), selector de línea O/U distinta de 2.5, ventana de track record configurable (fija en 50 partidos), heatmaps o radar charts de estilo de juego, live scores minuto a minuto.

**Resuelto en este init — la ruta `/` es la lista de partidos próximos (RF-001), no una landing de marketing.** Un mockup de referencia (ver Evidence on Hand) ponía la lista en `/partidos` y dejaba `/` como landing; se descartó esa estructura de rutas para mantener fidelidad estricta a la spec canónica.

**Terminología:** "partido" (Partido), "predicción" (Predicción: 1X2, Over/Under 2.5, BTTS, xG + nivel de confianza alta/media/baja), "explicación" (texto + evidencia verificable), "track record" (desempeño agregado por mercado + detalle partido a partido). Los tres mercados probabilísticos son `1x2`, `over_under_2_5`, `btts` — el xG no entra en el track record (no es una probabilidad).

**Indecisión registrada, no inventada:** la tabla de "historial partido a partido" del mockup de referencia mostraba una columna de confianza por fila que `track-record-api.md` no expone (la confianza vive en `Predicción` de 001, no en `EvaluaciónPredicción` de 003) — pendiente de decisión del equipo backend antes de construir esa columna.

## Brand Commitments

Nombre: **The Playbook**. Tagline confirmada: "Predicciones basadas en datos". Disclaimer legal obligatorio, visible (footer u otro lugar consistente en las tres vistas): *"The Playbook NO es una casa de apuestas ni ofrece asesoría financiera."* — confirmado como copy oficial del equipo, no placeholder.

## Evidence on Hand

- Los tres contratos de API congelados: `specs/001-prediccion-partido/contracts/matches-api.md`, `specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md`, `specs/003-track-record-publico/contracts/track-record-api.md` — cada uno con ejemplos JSON completos de request/response, la única fuente de verdad de qué datos existen.
- Mockup funcional de referencia visual: https://the-playbook-1.ai.studio/ (hecho por Octavio). Capturado y auditado: dark theme, acento verde neón, tipografía condensada bold, con datos de ejemplo hardcodeados (fallback cuando sus llamados a `/matches/upcoming`, `/leagues`, `/track-record` fallan). Tratarlo como evidencia de dirección visual, no como código a reutilizar — su estructura de rutas ya se descartó arriba, y su tabla de historial pivotea los datos distinto a como los devuelve la API real (una fila por partido con `hit_1x2`/`hit_over_under_2_5`/`hit_btts`, no una fila por mercado).
- Implementación actual en `frontend/`: llegó con el PR #16 (mergeado el 17/09/2026) y se rediseñó en el PR #21 (idioma español y dirección visual "marcador de estadio"). Es la base sobre la que se trabaja; el mockup externo sigue siendo solo referencia visual.
- El backend de 001 y 002 ya sirve datos (PR #24, #25 y #28, con CORS y fixture de demostración); el de 003 (track record) llega con el PR #29, aún abierto. Mientras no esté mergeado, el panel se valida contra los ejemplos del contrato.

## Product Principles

1. **El backend calcula, el frontend decide cómo mostrarlo y cuándo pedirlo** — ninguna excepción, ni por conveniencia visual ni por "solo un cálculo simple" (Artículo I).
2. **Ausencia declarada, nunca disfrazada** — un partido sin predicción, una explicación no generada, o una muestra insuficiente se dicen explícitamente; nunca se ocultan, ni se rellenan con ceros que parezcan desempeño real.
3. **Toda cifra que el usuario no puede verificar por su cuenta es una cifra que no debería mostrarse sin su fuente** — evidencia siempre con título, fuente, fecha y enlace al original.
4. **La ruta feliz no es la única ruta** — carga, error de red/5xx, vacío legítimo, y dato ausente son cuatro estados distintos con tratamiento visual distinto, en las tres vistas.
5. **Nunca parecer una casa de apuestas** — ni en la presentación de probabilidades, ni en el tratamiento visual de las cuotas de mercado del track record, que son referencia de baseline, no producto.

## Accessibility & Inclusion

Contraste AA de WCAG 2.1 en las tres vistas; anuncios accesibles de cambios de carga/error/resultado; utilizable completamente por teclado con foco visible; usable desde 360px de ancho sin scroll horizontal (RNF-001, RNF-002, RF-011 — no son metas aspiracionales, son parte de la Definition of Done del feature).
