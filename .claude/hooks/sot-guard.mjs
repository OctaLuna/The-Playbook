#!/usr/bin/env node
/**
 * sot-guard.mjs — PreToolUse. Protege la regla de fuente única de verdad.
 *
 * La auditoría SDD encontró los tres `tasks.md` duplicados byte a byte entre
 * `specs/` (spec-kit) y `openspec/changes/` — 75 tareas sin ninguna marca de cuál
 * mandaba. Marcar `[x]` en una dejaba mintiendo a la otra.
 *
 * Documentarlo no basta: un agente que abre `openspec/changes/001/tasks.md` y ve una
 * lista de tareas la edita. Este hook lo bloquea y le dice a dónde ir.
 *
 * Contrato: exit 0 permite; exit 2 bloquea y manda stderr al modelo.
 */

import { readFileSync } from "node:fs";

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0); // Sin evento parseable no hay nada que proteger.
}

const ruta = (evento?.tool_input?.file_path ?? "").replace(/\\/g, "/");
if (!ruta) process.exit(0);

const stub = /openspec\/changes\/([^/]+)\/tasks\.md$/.exec(ruta);
if (stub) {
  const id = stub[1];
  console.error(
    `BLOQUEADO: openspec/changes/${id}/tasks.md es un stub, no la fuente de verdad.\n\n` +
    `Las tareas de este change viven en specs/${id}/tasks.md, y ahí es donde se marcan\n` +
    `los [x]. En este repositorio spec-kit es canónico; OpenSpec aporta solo proposal.md\n` +
    `y design.md.\n\n` +
    `Si de verdad querías editar el stub (p. ej. para reformular su texto), pídeselo al\n` +
    `usuario explícitamente. Ver CLAUDE.md § Fuentes de verdad.`
  );
  process.exit(2);
}

process.exit(0);
