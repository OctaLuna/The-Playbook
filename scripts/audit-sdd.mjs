#!/usr/bin/env node
/**
 * audit-sdd.mjs — Validador de integridad de la documentación SDD de The Playbook.
 *
 * Nació de la auditoría SDD que encontró, en un repo sin una sola línea de código:
 *   · 24 enlaces a `docs/project_spec.md` cuando el archivo se llamaba `project_spec_v2.md`
 *   · 14 referencias a secciones inexistentes (`7.7`, `7.9`) o desfasadas en uno
 *   · 1 de 75 tareas citando el requisito funcional que cubre
 *
 * Todos eran invisibles a simple vista y todos inducían a un agente a inventar. Este
 * script los convierte en un fallo de build.
 *
 * Uso:  node scripts/audit-sdd.mjs [--strict] [--quiet]
 *       --strict  los avisos también hacen fallar (usado en CI)
 *       --quiet   solo imprime si hay hallazgos (usado como hook)
 */

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, resolve, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const STRICT = process.argv.includes("--strict");
const QUIET = process.argv.includes("--quiet");

const SPEC_TECNICO = "docs/project_spec.md";
const IGNORE_DIRS = new Set([
  ".git", "node_modules", ".venv", "venv", "__pycache__",
  ".next", ".pytest_cache", ".ruff_cache", ".mypy_cache", "mlruns",
]);

const errors = [];
const warnings = [];
const err = (file, line, msg, fix) => errors.push({ file, line, msg, fix });
const warn = (file, line, msg, fix) => warnings.push({ file, line, msg, fix });

/* ------------------------------------------------------------------ helpers */

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    if (IGNORE_DIRS.has(entry)) continue;
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (entry.endsWith(".md")) out.push(full);
  }
  return out;
}

const rel = (f) => relative(ROOT, f).split(sep).join("/");

/** Cada línea con su número, para reportar ubicaciones exactas. */
function lines(file) {
  return readFileSync(file, "utf8").split(/\r?\n/);
}

/* -------------------------------------------- 1. secciones de project_spec */

/** Headings numerados de docs/project_spec.md → Set{"1","2.1","6.4",…} */
function seccionesDelSpecTecnico() {
  const path = join(ROOT, SPEC_TECNICO);
  if (!existsSync(path)) {
    err(SPEC_TECNICO, 0, "El spec técnico no existe en la ruta canónica",
        "Restaura docs/project_spec.md — 24 referencias del repo dependen de esta ruta");
    return new Set();
  }
  const set = new Set();
  for (const l of lines(path)) {
    const m = /^#{2,4}\s+(\d+(?:\.\d+)?)[.\s]/.exec(l);
    if (m) set.add(m[1]);
  }
  return set;
}

/* ------------------------------------------------------------- 2. RF y tasks */

function requisitosFuncionales() {
  const porFeature = new Map();
  for (const f of walk(join(ROOT, "specs"))) {
    if (!f.endsWith("spec.md")) continue;
    const feature = rel(f).split("/")[1];
    const rfs = new Map();
    lines(f).forEach((l, i) => {
      const m = /^-\s+\*\*(RF-\d+[a-z]?)/.exec(l);
      if (m) rfs.set(m[1], { line: i + 1, texto: l });
    });
    if (rfs.size) porFeature.set(feature, { file: rel(f), rfs });
  }
  return porFeature;
}

function tareas() {
  const porFeature = new Map();
  for (const f of walk(join(ROOT, "specs"))) {
    if (!f.endsWith("tasks.md")) continue;
    const feature = rel(f).split("/")[1];
    const ts = [];
    lines(f).forEach((l, i) => {
      const m = /^-\s+\[([ xX])\]\s+(T\d+[a-z]?)/.exec(l);
      if (!m) return;
      ts.push({
        id: m[2],
        hecha: m[1].toLowerCase() === "x",
        line: i + 1,
        rfs: [...l.matchAll(/RF-\d+[a-z]?/g)].map((x) => x[0]),
        // Una tarea de proceso (confirmar la fase Red, reutilizar un test guardián)
        // no implementa un requisito de producto: traza a la constitución.
        historia: /Historia\s+\d/i.test(l) || /\bArt(?:\.|ículo)\s+[IVX]+/i.test(l),
        texto: l,
      });
    });
    if (ts.length) porFeature.set(feature, { file: rel(f), ts });
  }
  return porFeature;
}

/* ------------------------------------------------------------------- checks */

/**
 * Exenciones. Un registro de cambios tiene que poder citar el nombre viejo de un archivo
 * sin que el validador lo lea como una referencia rota. Marcadores:
 *   <!-- audit-sdd:ignore -->              en la propia línea
 *   <!-- audit-sdd:ignore-start --> … end  para un bloque (p. ej. una tabla histórica)
 */
function revisarArchivo(file, secciones) {
  const r = rel(file);
  const esStubOpenSpec = r.startsWith("openspec/changes/") && r.endsWith("tasks.md");
  let enBloqueIgnorado = false;

  lines(file).forEach((l, i) => {
    const n = i + 1;

    if (l.includes("audit-sdd:ignore-start")) { enBloqueIgnorado = true; return; }
    if (l.includes("audit-sdd:ignore-end")) { enBloqueIgnorado = false; return; }
    if (enBloqueIgnorado || l.includes("audit-sdd:ignore")) return;

    // (a) el nombre viejo del spec técnico
    if (l.includes("project_spec_v2")) {
      err(r, n, "Referencia a `project_spec_v2.md`, que ya no existe",
          `El archivo canónico es ${SPEC_TECNICO}`);
    }

    // (b) secciones citadas que no resuelven
    for (const m of l.matchAll(/secci[oó]n(?:es)?\s+((?:\d+(?:\.\d+)?)(?:\s*[-,y]+\s*\d+(?:\.\d+)?)*)/gi)) {
      for (const nums of m[1].split(/[-,y]+/)) {
        const num = nums.trim();
        if (!num || secciones.has(num)) continue;
        // ¿existe el padre? entonces es un subíndice inventado
        const padre = num.split(".")[0];
        const pista = secciones.has(padre)
          ? `La sección ${padre} existe pero no tiene subsección ${num}. Subsecciones válidas: ${[...secciones].filter((s) => s.startsWith(padre + ".")).join(", ") || "ninguna"}`
          : `No hay ninguna sección ${num} en ${SPEC_TECNICO}`;
        err(r, n, `Referencia colgante: "sección ${num}"`, pista);
      }
    }

    // (c) enlaces markdown relativos que no resuelven
    for (const m of l.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
      const target = m[1].trim();
      if (/^(https?:|mailto:|#)/i.test(target)) continue;
      const limpio = target.split("#")[0].split("?")[0];
      if (!limpio) continue;
      if (!existsSync(resolve(dirname(file), limpio))) {
        err(r, n, `Enlace roto: \`${target}\``,
            `No existe ${limpio} relativo a ${dirname(r) || "."}`);
      }
    }

    // (d) rutas de código sin el prefijo canónico backend/
    if (!esStubOpenSpec) {
      for (const m of l.matchAll(/`(app|ml|rag|workers)\/[\w./*{},-]*`/g)) {
        err(r, n, `Ruta sin prefijo canónico: ${m[0]}`,
            "Las rutas de código se escriben desde la raíz del repo: `backend/…`");
      }
      if (/`backend\/ml\/models\/ensemble/.test(l)) {
        err(r, n, "Ruta del ensamble incorrecta",
            "Es `backend/ml/ensemble/` (hermana de models/, no hija) — ver Artículo II");
      }
    }
  });
}

function revisarTrazabilidad(rfs, ts) {
  for (const [feature, { file, rfs: mapaRf }] of rfs) {
    const tareasFeature = ts.get(feature);
    if (!tareasFeature) {
      err(file, 0, `El feature ${feature} tiene requisitos pero ningún tasks.md`,
          "Todo RF debe tener al menos una tarea que lo implemente");
      continue;
    }

    const cubiertos = new Set(tareasFeature.ts.flatMap((t) => t.rfs));

    for (const [id, { line }] of mapaRf) {
      if (!cubiertos.has(id)) {
        err(file, line, `${id} es huérfano: ninguna tarea lo cubre`,
            `Añade "— [${id}]" a la tarea correspondiente en ${tareasFeature.file}`);
      }
    }

    for (const t of tareasFeature.ts) {
      if (t.rfs.length === 0 && !t.historia) {
        warn(tareasFeature.file, t.line, `${t.id} no declara qué requisito cubre`,
             'Añade el sufijo "— [RF-00X]" (o cita la Historia para tareas de integración)');
      }
      for (const id of t.rfs) {
        if (!mapaRf.has(id)) {
          err(tareasFeature.file, t.line, `${t.id} cita ${id}, que no existe en el spec`,
              `Requisitos definidos en ${file}: ${[...mapaRf.keys()].join(", ")}`);
        }
      }
    }
  }
}

/** Avisa de RFs que aplanan a "ubiquitous" un requisito con condición o disparador. */
function revisarEARS(rfs) {
  const DISPARADOR = /\b(cuando|mientras|si\b|donde|una vez que|al (?:entrar|generar|recibir|superar)|antes de|después de|tras)\b/i;
  const PATRON_EARS = /^-\s+\*\*RF-\d+[a-z]?:\*\*\s*(cuando|mientras|si\b|donde)/i;

  for (const [, { file, rfs: mapa }] of rfs) {
    for (const [id, { line, texto }] of mapa) {
      if (PATRON_EARS.test(texto)) continue;
      if (DISPARADOR.test(texto.replace(/^-\s+\*\*RF-\d+[a-z]?:\*\*/, ""))) {
        warn(file, line, `${id} usa el patrón ubiquitous pero describe una condición`,
             'EARS: "CUANDO <disparador>, el sistema DEBE…" (event-driven) o ' +
             '"SI <condición>, ENTONCES el sistema DEBE…" (unwanted behaviour)');
      }
      if (/\bNUNCA DEBE\b/.test(texto)) {
        warn(file, line, `${id} usa "NUNCA DEBE", que no es un patrón EARS`,
             'Reescribe como unwanted behaviour: "SI <condición prohibida>, ENTONCES el sistema DEBE <acción de bloqueo>"');
      }
    }
  }
}

/* --------------------------------------------------------------------- main */

const secciones = seccionesDelSpecTecnico();
for (const f of walk(ROOT)) revisarArchivo(f, secciones);

const rfs = requisitosFuncionales();
const ts = tareas();
revisarTrazabilidad(rfs, ts);
revisarEARS(rfs);

/* ------------------------------------------------------------------ salida */

const pintar = (items, icono) => {
  let ultimo = null;
  for (const { file, line, msg, fix } of items) {
    if (file !== ultimo) {
      console.log(`\n  ${file}`);
      ultimo = file;
    }
    console.log(`    ${icono} ${line ? `L${line}` : "  "}  ${msg}`);
    if (fix) console.log(`         └─ ${fix}`);
  }
};

const totalRf = [...rfs.values()].reduce((a, x) => a + x.rfs.size, 0);
const totalTs = [...ts.values()].reduce((a, x) => a + x.ts.length, 0);
const trazadas = [...ts.values()].reduce(
  (a, x) => a + x.ts.filter((t) => t.rfs.length || t.historia).length, 0);

if (errors.length) {
  console.log("\n\x1b[31m✖ Errores\x1b[0m");
  pintar(errors, "\x1b[31m✖\x1b[0m");
}
if (warnings.length && !QUIET) {
  console.log("\n\x1b[33m⚠ Avisos\x1b[0m");
  pintar(warnings, "\x1b[33m⚠\x1b[0m");
}

if (!QUIET || errors.length || warnings.length) {
  const pct = totalTs ? Math.round((trazadas / totalTs) * 100) : 0;
  console.log(
    `\n  ${totalRf} requisitos · ${totalTs} tareas · ${pct}% trazadas` +
    ` · ${errors.length} errores · ${warnings.length} avisos\n`
  );
}

if (errors.length || (STRICT && warnings.length)) process.exit(1);
if (!QUIET && !errors.length && !warnings.length) {
  console.log("\x1b[32m✔ Documentación SDD consistente.\x1b[0m\n");
}
