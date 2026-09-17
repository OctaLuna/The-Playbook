# Quickstart: Validación manual de la Interfaz Web

**Basado en:** `specs/004-interfaz-web/spec.md` y `plan.md`

## Requisitos

* Node.js instalado.
* Dependencias del frontend instaladas.
* Backend de las features 001, 002 y 003 disponible y ejecutándose.
* `frontend/.env.local` configurado con la URL real del backend.

## Preparar el frontend

Desde la carpeta `frontend/`:

```powershell
npm install
```

Crear el archivo `.env.local` a partir del ejemplo:

```powershell
Copy-Item .env.example .env.local
```

Revisar que `NEXT_PUBLIC_API_URL` apunte a la URL real donde está ejecutándose el backend.

## Validación automática

Ejecutar:

```powershell
npm run lint
npm run typecheck
npm test
```

Los tres comandos deben finalizar correctamente.

## Ejecutar la interfaz

Desde `frontend/`:

```powershell
npm run dev
```

Abrir la URL que muestre Next.js en la terminal.

## Escenario 1 — Recorrido completo del producto

1. Abrir la página principal.
2. Verificar que se listan los partidos próximos con equipos, liga y fecha.
3. Verificar que los partidos aparecen ordenados por proximidad al kickoff.
4. Filtrar por una liga y verificar que la liga aparece en la URL.
5. Copiar esa URL en una pestaña nueva y verificar que el filtro se conserva.
6. Abrir un partido con predicción generada.
7. Verificar que aparecen las cuatro señales: 1X2, O/U 2.5, BTTS y xG.
8. Verificar que el badge de confianza aparece en la misma vista.
9. Verificar que la explicación aparece y que cada evidencia tiene título y enlace.
10. Enviar una pregunta de seguimiento y verificar que la respuesta aparece en la misma vista junto con su evidencia.

## Escenario 2 — API no disponible

1. Con la interfaz abierta, detener el backend utilizando el procedimiento correspondiente al entorno del backend.
2. Recargar la página principal.
3. Verificar que aparece un mensaje de error distinto del estado de "no hay partidos".
4. Verificar que aparece la opción **Reintentar**.
5. Volver a levantar el backend.
6. Pulsar **Reintentar** y verificar que la información vuelve a cargar.

> Este repositorio no contiene `docker-compose.yml` ni `docker-compose.yaml`, por lo que no se documenta un comando Docker específico para el backend.

## Escenario 3 — Partido sin explicación

1. Abrir un partido que tenga predicción pero cuya explicación todavía no esté disponible.
2. Verificar que las cuatro señales continúan mostrándose.
3. Verificar que la interfaz indica que la explicación no está disponible todavía.
4. Verificar que la vista no se rompe ni queda en blanco.

## Escenario 4 — Aviso de datos insuficientes

1. Abrir un partido cuya predicción tenga `low_data_warning: true`.
2. Verificar que el aviso aparece antes de las probabilidades.
3. Verificar que el aviso no aparece únicamente como una nota al pie.

## Escenario 5 — Track record sin credenciales

1. Abrir el panel de track record en una ventana privada, sin sesión iniciada.
2. Verificar que carga sin solicitar autenticación.
3. Verificar que aparecen por separado los tres mercados: 1X2, O/U 2.5 y BTTS.
4. Verificar que cada mercado muestra su porcentaje de aciertos y sus métricas.
5. Entrar al detalle y verificar que cada fila muestra lo predicho junto con lo ocurrido.
6. Si `model_versions` contiene más de una versión, verificar que la interfaz muestra el aviso correspondiente.

## Escenario 6 — Muestra insuficiente

1. Con una base de datos sin partidos evaluados, abrir el panel de track record.
2. Verificar que declara que todavía no existe una muestra suficiente.
3. Verificar que no presenta ceros como sustituto de datos inexistentes.

## Escenario 7 — Accesibilidad y responsive

1. Recorrer las tres vistas utilizando únicamente el teclado (`Tab`, `Enter`, `Escape`).
2. Verificar que todos los controles interactivos son alcanzables.
3. Verificar que el foco permanece visible.
4. Reducir la ventana a 360 px de ancho.
5. Verificar que ninguna vista genera desplazamiento horizontal.

## Comprobación final

Antes de considerar la feature lista, ejecutar:

```powershell
npm run lint
npm run typecheck
npm test
```

Los tres comandos deben terminar sin errores.
