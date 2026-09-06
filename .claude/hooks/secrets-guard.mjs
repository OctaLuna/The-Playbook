#!/usr/bin/env node
/**
 * secrets-guard.mjs — PreToolUse. Implementa el criterio de la DoD del equipo
 * "Ausencia de datos sensibles o secretos en el código o los archivos subidos"
 * (docs/team-charter.md §6) como un control automático y no como una revisión manual.
 *
 * Este proyecto maneja credenciales de AWS Bedrock, API-Football y PostgreSQL, así que
 * el riesgo es real y no teórico.
 *
 * Contrato: exit 0 permite; exit 2 bloquea y manda stderr al modelo.
 */

import { readFileSync } from "node:fs";

let evento;
try {
  evento = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const entrada = evento?.tool_input ?? {};
const ruta = (entrada.file_path ?? "").replace(/\\/g, "/");

// Los ficheros de ejemplo existen precisamente para llevar placeholders.
if (/\.env\.example$|\.env\.sample$/.test(ruta)) process.exit(0);

const contenido = [entrada.content, entrada.new_string].filter(Boolean).join("\n");
if (!contenido) process.exit(0);

const PATRONES = [
  [/\bAKIA[0-9A-Z]{16}\b/, "AWS Access Key ID"],
  [/\baws_secret_access_key\s*=\s*['"]?[A-Za-z0-9/+=]{40}/i, "AWS Secret Access Key"],
  [/\b(?:postgres|postgresql|redis|mysql):\/\/[^\s:/@]+:[^\s@]{4,}@/, "cadena de conexión con contraseña"],
  [/\b(RAPIDAPI_KEY|API_FOOTBALL_KEY|NEWS_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*=\s*['"]?(?!(?:your|xxx|<|\$\{|changeme|placeholder|tu_))\S{12,}/i, "API key real en una asignación"],
  [/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/, "clave privada"],
  [/\bghp_[A-Za-z0-9]{36}\b/, "GitHub personal access token"],
];

const hallazgos = PATRONES.filter(([re]) => re.test(contenido)).map(([, n]) => n);

if (hallazgos.length) {
  console.error(
    `BLOQUEADO: parece haber un secreto en ${ruta || "el contenido a escribir"}.\n\n` +
    `Detectado: ${hallazgos.join(", ")}.\n\n` +
    `La DoD del equipo (docs/team-charter.md §6) exige ausencia de secretos en los\n` +
    `archivos versionados. Usa una variable de entorno leída desde\n` +
    `backend/app/core/ (Pydantic Settings) y deja solo un placeholder en .env.example.\n\n` +
    `Si es un falso positivo (un valor de ejemplo o un fixture de test), díselo al\n` +
    `usuario y que confirme antes de reintentar.`
  );
  process.exit(2);
}

process.exit(0);
