#!/usr/bin/env node
/**
 * spec-lint.mjs — PostToolUse sobre Markdown. Corre el validador SDD y devuelve sus
 * hallazgos al agente en el momento en que los introduce, no semanas después.
 *
 * Los fallos que motivaron esto —un enlace a un archivo renombrado, una "sección 7.7"
 * que no existe, una tarea sin su RF— son invisibles al escribir y costosísimos al leer:
 * un agente que no puede resolver una referencia tiende a reconstruirla de memoria.
 *
 * No bloquea (exit 2 solo devuelve el texto como contexto): un aviso a tiempo basta, y
 * bloquear cada edición de documentación haría el repo inmanejable.
 */

import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const ruta = (evento?.tool_input?.file_path ?? "").replace(/\\/g, "/");
if (!ruta.endsWith(".md")) process.exit(0);

const r = spawnSync("node", [resolve(RAIZ, "scripts", "audit-sdd.mjs"), "--quiet"], {
  cwd: RAIZ,
  encoding: "utf8",
  timeout: 30_000,
});

// status 1 = hay errores. Se los devolvemos al agente para que los arregle ya.
if (r.status === 1 && r.stdout?.trim()) {
  console.error(
    "El validador SDD encontró inconsistencias en la documentación:\n" +
    r.stdout.replace(/\x1b\[[0-9;]*m/g, "") +
    "\nArregla la referencia — no la silencies. Si es un caso legítimo (un registro de\n" +
    "cambios que cita a propósito un nombre antiguo), márcalo con <!-- audit-sdd:ignore -->."
  );
  process.exit(2);
}

process.exit(0);
