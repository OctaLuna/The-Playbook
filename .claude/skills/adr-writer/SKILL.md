---
name: adr-writer
description: Redacta un nuevo Architecture Decision Record en docs/adr/ siguiendo la plantilla canónica de ADR 0001, lo numera correlativamente, lo enlaza en docs/project_spec.md §12, y supersede en vez de editar cualquier ADR anterior que reemplace. Úsala cuando una decisión se aparte de docs/project_spec.md o memory/constitution.md, o resuelva una contradicción entre documentos.
---

# Redactar un ADR

Sigue el criterio y formato ya fijados en `docs/adr/README.md`. Esta skill no decide
*si* hace falta un ADR — eso lo dice esa regla — solo escribe uno correcto una vez que
el usuario confirmó que aplica.

## 1. Confirmar que corresponde un ADR

Según `docs/adr/README.md`, escribe uno solo si la decisión:

- contradice o modifica algo ya escrito en `docs/project_spec.md` o `memory/constitution.md`;
- elige entre alternativas con consecuencias difíciles de revertir (stack, esquema de
  datos, límites de proceso); o
- resuelve una contradicción entre dos documentos del repo.

Si la decisión ya está cubierta por la tabla "Decisiones técnicas y su porqué" de un
`plan.md`, no corresponde ADR — dile al usuario que ese es su sitio natural.

## 2. Numerar correlativamente

Lee `docs/adr/README.md` § Índice para encontrar el número más alto ya usado (hoy
`0001`). El nuevo ADR es el siguiente número, con cuatro dígitos y cero a la izquierda.
Los números nunca se reutilizan, ni siquiera si un ADR se descarta antes de aceptarse.

## 3. Escribir con la plantilla de ADR 0001

Usa `docs/adr/0001-badge-confianza-calibrado.md` como plantilla estructural exacta:

- Título: `# ADR NNNN — <título corto de la decisión>`.
- Cabecera: `**Estado:**` (Propuesto/Aceptado/Rechazado/Reemplazado), `**Fecha:**`
  (AAAA-MM-DD), `**Origen:**` (qué disparó la decisión), `**Afecta a:**` (rutas exactas
  de los documentos que este ADR corrige o restringe).
- Secciones, en este orden: **Contexto** · **Decisión** · **Justificación** ·
  **Consecuencias** · **Alternativas descartadas**.
- La sección Alternativas descartadas es una tabla `| Alternativa | Por qué no |`.
- Idioma español, identificadores de código en inglés (regla general del repo).

## 4. Enlazar en docs/adr/README.md y en project_spec.md §12

- Agrega una fila a la tabla `## Índice` de `docs/adr/README.md`, mismo formato que la
  fila de ADR 0001: número enlazado a su archivo, título, estado, fecha.
- Agrega una fila a `docs/project_spec.md` § 12 (la tabla de registro de cambios más
  reciente, hoy `12.1`, o crea `12.2` si `12.1` ya cerró un ciclo distinto) describiendo
  qué cambió, con qué versión y por qué — mismo formato que las filas existentes.
- Si el ADR corrige una sección específica de `project_spec.md` (como hizo ADR 0001 con
  §2.1), edita esa sección para que refleje la decisión — el ADR documenta el porqué,
  la sección del spec debe quedar correcta por sí sola para quien no lea el ADR.

## 5. Nunca editar un ADR aceptado — supersedelo

Si este ADR reemplaza la decisión de uno anterior:

- **No edites el ADR anterior.** Solo agrégale una línea bajo su cabecera:
  `**Superseded by:** ADR NNNN (` seguido del nombre de archivo del ADR nuevo `)`.
- Actualiza su fila en el Índice de `docs/adr/README.md`: columna Estado pasa a
  `Reemplazado por NNNN`.
- El ADR nuevo, en su sección Contexto, referencia explícitamente al que reemplaza y
  resume por qué dejó de aplicar.

Esta regla viene de `docs/adr/README.md`: *"Un ADR aceptado no se edita: se supersede
con uno nuevo que lo referencia."* — no es una convención de esta skill, es la regla del
repo.
