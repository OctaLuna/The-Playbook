/**
 * _venv.mjs — helper compartido. Los hooks que corren herramientas Python (ruff, mypy,
 * pytest) no pueden asumir que están en el PATH del proceso que ejecuta los hooks: en
 * este repo viven únicamente en backend/.venv/, nunca instaladas globalmente. Sin esto,
 * `spawnSync("mypy", ...)` falla en silencio y el hook queda como no-op permanente sin
 * que nadie lo note — exactamente lo que le pasaba a mypy-check.mjs y a la parte .py de
 * format.mjs antes de este archivo.
 */

import { existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const VENV = resolve(RAIZ, "backend", ".venv");

/** Ruta al binario dentro de backend/.venv si existe; si no, el nombre pelado (PATH). */
export function venvBin(nombre) {
  const win = resolve(VENV, "Scripts", `${nombre}.exe`);
  const posix = resolve(VENV, "bin", nombre);
  if (existsSync(win)) return win;
  if (existsSync(posix)) return posix;
  return nombre;
}
