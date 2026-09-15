# Architecture Decision Records

Registro de decisiones arquitectónicas del proyecto. Exigido por la §10 de
[`docs/project_spec.md`](../project_spec.md):

> *"Cada decisión que se aparte de este documento debe registrarse como un ADR en `docs/adr/`."*

## Cuándo escribir un ADR

Escribe uno cuando la decisión:

- contradice o modifica algo ya escrito en `docs/project_spec.md` o en `memory/constitution.md`;
- elige entre alternativas con consecuencias difíciles de revertir (stack, esquema de datos, límites de proceso);
- resuelve una contradicción entre dos documentos del repo.

No escribas uno para decisiones ya cubiertas por la tabla "Decisiones técnicas y su porqué"
de un `plan.md` — ese es su sitio natural.

## Formato

`NNNN-titulo-en-kebab-case.md`, numeración correlativa que nunca se reutiliza.
Un ADR aceptado no se edita: se supersede con uno nuevo que lo referencia.

Secciones: **Estado** · **Contexto** · **Decisión** · **Consecuencias** · **Alternativas descartadas**.

## Índice

| ADR | Título | Estado | Fecha |
|---|---|---|---|
| [0001](0001-badge-confianza-calibrado.md) | Nivel de confianza derivado de calibración empírica, no de distancia a uniforme | Aceptado | 2026-09-06 |
