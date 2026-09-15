# Propuesta: Interfaz Web

**Referencia completa:** `specs/004-interfaz-web/` (spec-kit) — spec, plan, modelo de datos,
contratos consumidos, quickstart y tareas.

## Por qué

El product goal promete "despliegue operativo en una **plataforma web accesible**"
(`docs/project_spec.md` §1), y las tres features del MVP describen comportamiento de usuario:
*"el usuario abre la ficha del partido"*, *"el usuario ve el panel"*. Pero 001, 002 y 003
entregan API, no producto: entre las tres suman 86 tareas y ninguna toca `frontend/`.

La revisión SDD previa a la implementación lo detectó: el frontend no estaba cubierto por
ninguna tarea **y tampoco estaba declarado fuera de alcance**. Un MVP que se completara tal como
estaba planificado sería una API sin nadie que la use, y el pilar 3 —track record auditable
"por cualquier usuario"— no se cumpliría: un panel que solo existe como JSON no es auditable por
un aficionado.

## Qué cambia

Se añade la capability `interfaz-web` con las tres vistas del MVP:

1. **Lista de partidos próximos**, con filtro por liga.
2. **Ficha del partido**: las cuatro señales, el badge de confianza, la explicación con su
   evidencia enlazable, y las preguntas de seguimiento.
3. **Panel de track record**: los tres mercados por separado y el detalle partido a partido.

Más los estados que hoy no tiene ninguna especificación: carga, error, y ausencia de datos.

## Qué NO cambia

Ningún contrato de backend. Esta capability **solo consume** los de 001, 002 y 003, ya
congelados. No añade lógica de negocio: ninguna vista calcula una probabilidad, una métrica ni
un acierto (Artículo I). Si una vista necesitara un dato que ningún contrato devuelve, se
cambiaría el contrato del backend, no se calcularía en el cliente.

## Código afectado

`frontend/app/`, `frontend/components/`, `frontend/lib/api/`, y el job `frontend` de
`.github/workflows/ci.yml`, hoy desactivado con `if: false`.

## Dependencias

Requiere **001 implementada** para el Grupo 4 en adelante. 002 y 003 son degradables por diseño:
la ficha funciona sin explicación (RF-009) y el panel declara muestra insuficiente cuando aún no
hay evaluaciones.
