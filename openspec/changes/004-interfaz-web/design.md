# Design: interfaz-web

**Referencia completa:** `specs/004-interfaz-web/plan.md`, `data-model.md` y
`contracts/README.md` (spec-kit) — este documento es un resumen orientado a OpenSpec; el detalle
de tipos, claves de caché y contratos consumidos vive en esos archivos, no se duplica aquí.

## Resumen técnico
Tres vistas en Next.js 15 (App Router) + TypeScript que consumen las APIs de 001, 002 y 003.
Los tipos de las respuestas se derivan de los contratos ya definidos, no se reescriben a mano.
TanStack Query gestiona caché, reintentos y los estados de carga y error. Sin lógica de negocio:
toda probabilidad, métrica y acierto llega calculado desde el backend.

## Gates de simplicidad y arquitectura (ver `../../project.md`)
- ≤3 módulos: un único proyecto `frontend/`, sin paquetes compartidos.
- Sin future-proofing: tres vistas. Auth, favoritos, selector de idioma y de línea O/U quedan
  explícitamente fuera de alcance.
- Framework directo: App Router y shadcn/ui tal cual, sin una capa propia que los envuelva.
- Integration-first: los tres contratos están congelados; las primeras pruebas verifican que los
  tipos derivados parsean sus respuestas de ejemplo.

## Cumplimiento de convenciones no negociables
- **Library-First:** el frontend habla HTTP y no importa nada del backend. Ninguna vista calcula
  una probabilidad, una métrica ni un acierto.
- **Independencia del mercado:** ninguna vista muestra cuotas de casas de apuestas. Solo el
  agregado `avg_market_log_loss` que el contrato de 003 expone como baseline.
- **Aislamiento de procesos:** el cliente nunca dispara generación de predicciones ni de
  explicaciones; solo lee lo ya calculado por Celery.

## Decisiones técnicas clave
| Decisión | Por qué |
|---|---|
| Tipos derivados de los contratos, una sola definición | Dos representaciones del mismo dato se desincronizan a la primera iteración |
| TanStack Query para toda lectura | Da caché, reintentos y estados de carga/error de fábrica, que es lo que piden RF-007 y RF-008 |
| Skeletons con la estructura de cada vista, no un spinner | Un spinner no evita el salto de contenido al llegar los datos |
| Error y vacío como componentes distintos | "La API falló" y "no hay partidos" son cosas distintas; unificarlos hace que un fallo parezca un dominio vacío |
| El aviso de datos insuficientes va sobre las probabilidades | Un aviso que se lee después de la cifra ya no cambia cómo se interpretó la cifra |
| Una sección por mercado en el panel, sin selector | Esconder los tres tras un selector invita a comparar solo el que mejor se vea |

Detalle completo de alternativas consideradas y requisito satisfecho por cada decisión:
`specs/004-interfaz-web/plan.md`.

## Modelo de datos y contratos
Esta capability no persiste nada. Ver `specs/004-interfaz-web/data-model.md` (tipos derivados y
claves de caché) y `specs/004-interfaz-web/contracts/README.md` (los tres contratos que consume,
enlazados en vez de copiados).

## Registro de complejidad
Ningún gate falló — no aplica.
