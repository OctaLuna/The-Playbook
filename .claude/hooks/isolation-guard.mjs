#!/usr/bin/env node
/**
 * isolation-guard.mjs — PreToolUse. Protege el Artículo I (Library-First):
 * `backend/ml/` y `backend/rag/` no importan nada de `backend/app/api/`. Se comunican
 * con el backend únicamente vía `backend/app/services/`.
 *
 * El guardián documentado hoy es "Revisión de imports" — manual. Este hook lo vuelve
 * automático desde el primer archivo que toque esos árboles, en vez de depender de que
 * un agente o un revisor lo note a ojo.
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

const entrada = evento?.tool_input ?? {};
const ruta = (entrada.file_path ?? "").replace(/\\/g, "/");
if (!ruta) process.exit(0);

const enArbolAislado = /\/backend\/(ml|rag)\/.+/.test(ruta) || /^backend\/(ml|rag)\/.+/.test(ruta);
if (!enArbolAislado) process.exit(0);

const contenido = [entrada.content, entrada.new_string].filter(Boolean).join("\n");
if (!contenido) process.exit(0);

const PATRON_IMPORT_PROHIBIDO = /\b(?:from\s+app\.api(?:\.\S+)?\s+import|import\s+app\.api\b)/;

if (PATRON_IMPORT_PROHIBIDO.test(contenido)) {
  console.error(
    `BLOQUEADO: ${ruta} importa de app.api.\n\n` +
    `Artículo I (Library-First) de memory/constitution.md: backend/ml/ y backend/rag/\n` +
    `no importan nada de backend/app/api/. Se comunican con el backend únicamente vía\n` +
    `backend/app/services/, que es el único puente entre el API y el ML.\n\n` +
    `Si esta lógica necesita algo que hoy vive en app/api/, muévelo a app/services/ y\n` +
    `haz que ambos lados importen desde ahí.`
  );
  process.exit(2);
}

process.exit(0);
