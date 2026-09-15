#!/usr/bin/env node
/**
 * test-echo.mjs — PostToolUse sobre archivos test_....py dentro de backend/tests o backend/ml.
 * Corre ese archivo puntual con pytest apenas se escribe y devuelve el resultado —
 * PASSED/FAILED más las primeras líneas del traceback — como salida informativa.
 *
 * Existe porque una confirmación de fase Roja o Verde del Artículo III no vale nada si
 * nadie mira el motivo exacto del resultado: esto lo hace visible por defecto en vez de
 * depender de que alguien se acuerde de correr pytest a mano. red-phase-verifier.md hace
 * el juicio semántico sobre si el motivo es legítimo; este hook solo garantiza que la
 * evidencia esté siempre a la vista.
 *
 * Contrato: exit 0 siempre. Nunca bloquea — es un eco, no un gate.
 */

import { readFileSync, existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { resolve, dirname, relative, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { venvBin } from "./_venv.mjs";

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const BACKEND = resolve(RAIZ, "backend");
const PYTHON = venvBin("python");

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const ruta = evento?.tool_input?.file_path;
if (!ruta || !existsSync(ruta)) process.exit(0);

const rutaAbsoluta = resolve(ruta);
if (!basename(rutaAbsoluta).match(/^test_.*\.py$/)) process.exit(0);

const rutaRelativaBackend = relative(BACKEND, rutaAbsoluta);
if (rutaRelativaBackend.startsWith("..")) process.exit(0);
// Solo backend/tests/ y backend/ml/ — son los dos árboles que pytest recorre
// (testpaths = ["tests", "ml"] en pyproject.toml).
if (!/^(tests|ml)[\\/]/.test(rutaRelativaBackend)) process.exit(0);

if (!existsSync(PYTHON)) process.exit(0); // sin venv, sin eco — no hay con qué correrlo.

const resultado = spawnSync(PYTHON, ["-m", "pytest", rutaRelativaBackend, "-v"], {
  cwd: BACKEND,
  encoding: "utf8",
  timeout: 30_000,
});

const salida = [resultado.stdout, resultado.stderr].filter(Boolean).join("\n").trim();
const estado = resultado.status === 0 ? "PASSED" : "FAILED";
const lineas = salida.split("\n").slice(-20).join("\n"); // las últimas líneas traen el resumen y el traceback

console.error(
  `pytest ${rutaRelativaBackend} -> ${estado}\n\n${lineas}\n\n` +
  `Si esto es una confirmación de fase Red o Green del Artículo III, no des el resultado ` +
  `por bueno solo por el PASSED/FAILED — confirmá que la razón es la correcta (usá ` +
  `red-phase-verifier si hace falta un juicio más a fondo).`
);

process.exit(0);
