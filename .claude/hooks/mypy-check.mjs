#!/usr/bin/env node
/**
 * mypy-check.mjs — PostToolUse sobre archivos .py. Corre mypy y devuelve sus hallazgos
 * al agente en el momento en que escribe el código, mismo criterio que
 * .github/workflows/ci.yml usa con `mypy || true`: informativo, nunca bloquea.
 *
 * pyproject.toml fija `disallow_untyped_defs = true` para app/ml/rag/workers, pero
 * format.mjs solo corre ruff sobre .py — mypy no se veía hasta el PR. Este hook lo
 * adelanta a la escritura sin volverse un segundo guardián que interrumpa al agente.
 *
 * Contrato: exit 0 siempre. Si mypy no está instalado, o el archivo no es parte del
 * proyecto tipado, sale en silencio.
 */

import { readFileSync, existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { extname, resolve, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { venvBin } from "./_venv.mjs";

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const BACKEND = resolve(RAIZ, "backend");
const MYPY = venvBin("mypy");

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const ruta = evento?.tool_input?.file_path;
if (!ruta || !existsSync(ruta)) process.exit(0);
if (extname(ruta).toLowerCase() !== ".py") process.exit(0);

// mypy corre desde backend/ (ahí vive pyproject.toml con la config de tipos).
const rutaRelativa = relative(BACKEND, resolve(ruta));
if (rutaRelativa.startsWith("..")) process.exit(0);

const disponible = (bin) => {
  const r = spawnSync(bin, ["--version"], { stdio: "ignore", shell: true, timeout: 10_000 });
  return r.status === 0;
};

if (!disponible(MYPY)) process.exit(0);

const resultado = spawnSync(MYPY, [rutaRelativa], {
  cwd: BACKEND,
  encoding: "utf8",
  shell: true,
  timeout: 30_000,
});

if (resultado.stdout?.trim()) {
  console.error(
    `mypy encontró lo siguiente en ${rutaRelativa} (informativo, no bloquea):\n\n` +
    resultado.stdout.trim()
  );
}

process.exit(0);
