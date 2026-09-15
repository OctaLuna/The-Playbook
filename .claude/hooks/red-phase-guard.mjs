#!/usr/bin/env node
/**
 * red-phase-guard.mjs — PreToolUse. Protege el Artículo III (Test-First) en el arranque
 * del stack: bloquea escribir código de implementación en los árboles que el Artículo III
 * cubre (backend/app/main.py, backend/app/{api,services,models,schemas}/, backend/workers/,
 * backend/ml/, backend/rag/) si todavía no existe ninguna prueba real (def test_...) bajo
 * backend/tests/ ni backend/ml/.
 *
 * No puede verificar que la prueba se haya visto fallar (fase Red) — eso exige ejecutar
 * pytest, fuera del alcance de un hook estático. Garantiza solo la precondición necesaria:
 * la prueba existe antes que la implementación. En Grupo 0 esto es exactamente B06 (test
 * de /health) antes de B07 (main.py).
 *
 * isolation-guard.mjs cubre el Artículo I; sot-guard.mjs la fuente única de verdad; este
 * cubre el Artículo III. backend/app/core/, backend/app/db/ y backend/alembic/ quedan
 * exentos: son el andamiaje de Grupo 0 (B03/B04/B08) que tasks.md coloca antes de B06 a
 * propósito — no hay comportamiento de producto que probar todavía.
 *
 * Contrato: exit 0 permite; exit 2 bloquea y manda stderr al modelo.
 */

import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0); // Sin evento parseable no hay nada que proteger.
}

const entrada = evento?.tool_input ?? {};
const rutaCruda = (entrada.file_path ?? "").replace(/\\/g, "/");
if (!rutaCruda) process.exit(0);

const match = /(?:^|\/)(backend\/.+)$/.exec(rutaCruda);
if (!match) process.exit(0);
const rutaRelativa = match[1];

const ARBOLES_CUBIERTOS = [
  /^backend\/app\/main\.py$/,
  /^backend\/app\/api\//,
  /^backend\/app\/services\//,
  /^backend\/app\/models\//,
  /^backend\/app\/schemas\//,
  /^backend\/workers\//,
  /^backend\/ml\//,
  /^backend\/rag\//,
];

const cubierto = ARBOLES_CUBIERTOS.some((patron) => patron.test(rutaRelativa));
if (!cubierto) process.exit(0);

function buscarRaizProyecto() {
  let dir = process.cwd();
  for (let i = 0; i < 5; i++) {
    if (existsSync(join(dir, "backend", "tests"))) return dir;
    dir = join(dir, "..");
  }
  return process.cwd();
}

function hayAlgunaPruebaReal(dir) {
  if (!existsSync(dir)) return false;
  for (const nombre of readdirSync(dir)) {
    const rutaHijo = join(dir, nombre);
    const info = statSync(rutaHijo);
    if (info.isDirectory()) {
      if (hayAlgunaPruebaReal(rutaHijo)) return true;
      continue;
    }
    if (!/^test_.*\.py$/.test(nombre)) continue;
    const contenido = readFileSync(rutaHijo, "utf8");
    if (/^\s*(?:async\s+)?def\s+test_/m.test(contenido)) return true;
  }
  return false;
}

const raiz = buscarRaizProyecto();
const existePrueba =
  hayAlgunaPruebaReal(join(raiz, "backend", "tests")) ||
  hayAlgunaPruebaReal(join(raiz, "backend", "ml"));

if (!existePrueba) {
  console.error(
    `BLOQUEADO: ${rutaRelativa} es código de implementación y todavía no existe ninguna\n` +
    `prueba real ("def test_...") en backend/tests/ ni backend/ml/.\n\n` +
    `Artículo III (Test-First) de memory/constitution.md, no negociable: se escribe la\n` +
    `prueba, el usuario la valida, y se confirma que falla (fase Red) antes de escribir\n` +
    `implementación. En Grupo 0 esto es B06 (test de /health) antes de B07 (main.py).\n\n` +
    `Este hook solo verifica que la prueba EXISTA. Verificar que la hayas visto fallar\n` +
    `sigue siendo tu responsabilidad — corre pytest y confirma el rojo antes de continuar.`
  );
  process.exit(2);
}

process.exit(0);
