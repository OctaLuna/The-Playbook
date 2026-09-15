# Quickstart: Validación manual de la Interfaz Web

**Basado en:** `specs/004-interfaz-web/spec.md` y `plan.md`

Requiere el backend levantado con al menos 001 implementada:
`docker compose -f infra/docker-compose.yml up -d` y `cd frontend && npm run dev`.

## Escenario 1 — Recorrido completo del producto
1. Abrir la página principal.
2. Verificar: se listan los partidos próximos con equipos, liga y fecha, ordenados por
   proximidad al kickoff.
3. Filtrar por una liga y verificar que la lista se acota y que la liga aparece en la URL.
   Copiar esa URL en una pestaña nueva y verificar que el filtro se conserva.
4. Abrir un partido con predicción generada.
5. Verificar: las cuatro señales (1X2, O/U 2.5, BTTS, xG) y el badge de confianza están en la
   misma pantalla, sin navegar.
6. Verificar: la explicación aparece y **cada** pieza de evidencia tiene titular y enlace.
   Abrir un enlace y comprobar que lleva a la noticia real.
7. Enviar una pregunta de seguimiento y verificar que la respuesta aparece en la misma vista,
   con la evidencia en la que se apoya.

## Escenario 2 — La API cae
1. Con la interfaz abierta, parar el backend (`docker compose stop backend`).
2. Recargar la página principal.
3. Verificar: se muestra un mensaje de error que **distingue el fallo de "no hay partidos"**, y
   ofrece reintentar.
4. Levantar el backend de nuevo y pulsar reintentar. Verificar que la lista carga.

## Escenario 3 — Partido sin explicación
1. Abrir un partido que tenga predicción pero cuya explicación aún no se haya generado (002 no
   implementada, o el job de generación aún no ha corrido).
2. Verificar: las cuatro señales se muestran igual, y la interfaz declara que la explicación no
   está disponible todavía. La vista no se rompe ni queda en blanco.

## Escenario 4 — Aviso de datos insuficientes
1. Abrir un partido cuya predicción trae `low_data_warning: true`.
2. Verificar: el aviso se lee **antes** que las probabilidades, no como nota al pie.

## Escenario 5 — Track record sin credenciales
1. Abrir el panel de track record en una ventana privada, sin sesión iniciada.
2. Verificar: carga sin pedir autenticación.
3. Verificar: los tres mercados (1X2, O/U 2.5, BTTS) aparecen por separado, cada uno con su
   porcentaje de aciertos y sus métricas.
4. Entrar al detalle y verificar que cada fila muestra lo predicho junto a lo ocurrido.
5. Si `model_versions` trae más de una versión, verificar que la interfaz lo advierte.

## Escenario 6 — Muestra insuficiente
1. Con una base de datos sin partidos evaluados, abrir el panel.
2. Verificar: declara que aún no hay muestra suficiente, en vez de mostrar ceros —que se leerían
   como "el modelo falla siempre".

## Escenario 7 — Accesibilidad
1. Recorrer las tres vistas usando solo el teclado (`Tab`, `Enter`, `Escape`).
2. Verificar: todo control es alcanzable, el foco es siempre visible, y ningún elemento
   interactivo se salta.
3. Reducir la ventana a 360 px de ancho y verificar que ninguna vista genera desplazamiento
   horizontal.
