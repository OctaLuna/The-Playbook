#!/usr/bin/env node
/**
 * format.mjs — PostToolUse. Formatea el archivo recién escrito según su extensión.
 *
 * Diseñado para un repo que hoy es 100% Markdown y que mañana tendrá Python y
 * TypeScript: si la herramienta no está instalada, el hook sale en silencio en vez de
 * fallar. Así se puede instalar hoy y empieza a rendir solo cuando llegue el código,
 * sin ruido intermedio.
 *
 * Contrato: exit 0 siempre. Formatear no debe interrumpir nunca al agente.
 */

import { readFileSync } from "node:fs";
import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { extname, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const ruta = evento?.tool_input?.file_path;
if (!ruta || !existsSync(ruta)) process.exit(0);

/** Comandos por extensión. `npx -y` resuelve binarios locales o los descarga. */
const POR_EXTENSION = {
  ".py": [["ruff", ["check", "--fix", "--quiet", ruta]], ["ruff", ["format", "--quiet", ruta]]],
  ".pyi": [["ruff", ["format", "--quiet", ruta]]],
  ".ts": [["prettier", ["--write", ruta]], ["eslint", ["--fix", ruta]]],
  ".tsx": [["prettier", ["--write", ruta]], ["eslint", ["--fix", ruta]]],
  ".js": [["prettier", ["--write", ruta]]],
  ".jsx": [["prettier", ["--write", ruta]]],
  ".mjs": [["prettier", ["--write", ruta]]],
  ".css": [["prettier", ["--write", ruta]]],
  ".json": [["prettier", ["--write", ruta]]],
  ".jsonc": [["prettier", ["--write", ruta]]],
  ".sql": [["sqlfluff", ["fix", "--dialect", "postgres", "--force", ruta]]],
};

const comandos = POR_EXTENSION[extname(ruta).toLowerCase()] ?? [];

/** ¿Existe el binario? Evita el coste y el ruido de invocar algo no instalado. */
const disponible = (bin) => {
  const r = spawnSync(bin, ["--version"], { stdio: "ignore", shell: true, timeout: 10_000 });
  return r.status === 0;
};

for (const [bin, args] of comandos) {
  if (!disponible(bin)) continue;
  spawnSync(bin, args, { stdio: "ignore", shell: true, cwd: RAIZ, timeout: 30_000 });
}

process.exit(0);
