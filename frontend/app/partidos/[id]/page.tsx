"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { Cargando } from "@/components/estado/Cargando";
import { Error as ErrorState } from "@/components/estado/Error";
import { Vacio } from "@/components/estado/Vacio";
import {
  useExplanation,
  useFollowUp,
  useMatch,
  usePrediction,
} from "@/lib/api/hooks";
import type { FollowUpResponse } from "@/lib/api/types";

function formatKickoff(kickoffAt: string) {
  return new Intl.DateTimeFormat("es-BO", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(kickoffAt));
}

function percentage(value: number) {
  return `${Math.round(value * 100)}%`;
}

function statusLabel(status: string) {
  switch (status) {
    case "scheduled":
      return "Programado";
    case "postponed":
      return "Postergado";
    case "canceled":
      return "Cancelado";
    case "finished":
      return "Jugado";
    default:
      return status;
  }
}

export default function MatchDetailPage() {
  const params = useParams<{ id: string }>();
  const matchId = params.id;

  const matchQuery = useMatch(matchId);
  const predictionQuery = usePrediction(matchId);
  const explanationQuery = useExplanation(matchId);
  const followUp = useFollowUp(matchId);

  const [question, setQuestion] = useState("");
  const [followUpResponse, setFollowUpResponse] =
    useState<FollowUpResponse | null>(null);
  const [followUpError, setFollowUpError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [barsGrown, setBarsGrown] = useState(false);

  useEffect(() => {
    if (predictionQuery.data) {
      const frame = requestAnimationFrame(() =>
        requestAnimationFrame(() => setBarsGrown(true)),
      );
      return () => cancelAnimationFrame(frame);
    }
  }, [predictionQuery.data]);

  async function handleFollowUp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;

    setIsSubmitting(true);
    setFollowUpError(null);

    try {
      const response = await followUp({ question: trimmedQuestion });
      setFollowUpResponse(response);
    } catch {
      setFollowUpError("No se pudo obtener una respuesta. Intenta nuevamente.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (matchQuery.isLoading || predictionQuery.isLoading) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <Cargando />
      </main>
    );
  }

  if (matchQuery.isError) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <ErrorState error={matchQuery.error} onRetry={() => void matchQuery.refetch()} />
      </main>
    );
  }

  if (!matchQuery.data) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <Vacio title="Partido no encontrado" message="No se encontró información para este partido." />
      </main>
    );
  }

  const match = matchQuery.data;
  const prediction = predictionQuery.data;

  return (
    <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-9 pb-14">
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground transition hover:text-foreground"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Volver a partidos
      </Link>

      <div className="tabular mb-2 text-[13px] text-muted-foreground">
        {formatKickoff(match.kickoff_at)}
      </div>
      <div className="mb-7 flex flex-wrap items-baseline gap-5">
        <h1 className="font-display text-5xl tracking-wide">
          {match.home_team} <span className="text-muted-foreground">vs</span> {match.away_team}
        </h1>
        <span className="rounded-[3px] border border-[#3a423f] px-3 py-1.5 text-xs font-bold uppercase tracking-wide text-[#c8cdca]">
          {statusLabel(match.status)}
        </span>
      </div>

      {predictionQuery.isError || !prediction ? (
        <div className="rounded border border-border p-7">
          <h2 className="font-display text-2xl tracking-wide">
            PREDICCIÓN NO DISPONIBLE
          </h2>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">
            Este partido todavía no tiene una predicción generada por el modelo.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
          {/* Señales del modelo */}
          <div className="flex flex-col gap-6 rounded border border-border p-7">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-xl tracking-wide">
                SEÑALES DEL MODELO
              </h2>
              <span className="rounded-full bg-primary px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-primary-foreground">
                {prediction.confidence}
              </span>
            </div>

            {prediction.low_data_warning && (
              <div role="alert" className="rounded border border-[#4a3a1e] bg-[#1a160d] p-4">
                <p className="text-[13px] font-semibold text-[#e8a33d]">
                  Datos insuficientes
                </p>
                <p className="mt-1 text-[13px] leading-relaxed text-[#e8c88d]">
                  Las probabilidades deben interpretarse con precaución.
                </p>
              </div>
            )}

            <div>
              <div className="mb-2.5 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                Mercado 1X2
              </div>
              <div className="flex h-7 overflow-hidden rounded-[3px] bg-[#141816]">
                <div
                  className="h-full origin-left bg-primary transition-transform duration-700 ease-out"
                  style={{
                    width: "100%",
                    transform: `scaleX(${barsGrown ? prediction.probabilities_1x2.home : 0})`,
                  }}
                />
                <div
                  className="h-full origin-left bg-[#3a423f] transition-transform duration-700 ease-out"
                  style={{
                    width: "100%",
                    transform: `scaleX(${barsGrown ? prediction.probabilities_1x2.draw : 0})`,
                  }}
                />
                <div
                  className="h-full origin-left bg-[#21504a] transition-transform duration-700 ease-out"
                  style={{
                    width: "100%",
                    transform: `scaleX(${barsGrown ? prediction.probabilities_1x2.away : 0})`,
                  }}
                />
              </div>
              <div className="tabular mt-2 flex justify-between text-[13px]">
                <span>Local <b>{percentage(prediction.probabilities_1x2.home)}</b></span>
                <span className="text-muted-foreground">
                  Empate <b>{percentage(prediction.probabilities_1x2.draw)}</b>
                </span>
                <span>Visit. <b>{percentage(prediction.probabilities_1x2.away)}</b></span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3.5">
              <div className="rounded-[3px] border border-border p-3.5">
                <div className="mb-2 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                  Goles O/U 2.5
                </div>
                <div className="tabular flex justify-between">
                  <div>
                    <div className="text-[10px] text-muted-foreground">OVER</div>
                    <div className="text-xl font-semibold">{percentage(prediction.over_under_2_5.over)}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground">UNDER</div>
                    <div className="text-xl font-semibold text-muted-foreground">{percentage(prediction.over_under_2_5.under)}</div>
                  </div>
                </div>
              </div>
              <div className="rounded-[3px] border border-border p-3.5">
                <div className="mb-2 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                  Ambos marcan
                </div>
                <div className="tabular text-xl font-semibold">
                  Sí {percentage(prediction.btts.yes)}
                </div>
              </div>
            </div>

            <div className="rounded-[3px] border border-border p-3.5">
              <div className="mb-2 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                Goles esperados (xG)
              </div>
              <div className="tabular flex gap-7">
                <div><span className="text-xs text-muted-foreground">{match.home_team}</span> <b className="text-lg">{prediction.xg.home.toFixed(2)}</b></div>
                <div><span className="text-xs text-muted-foreground">{match.away_team}</span> <b className="text-lg">{prediction.xg.away.toFixed(2)}</b></div>
              </div>
            </div>

            <div className="tabular mt-auto border-t border-border pt-3.5 text-[11px] text-muted-foreground">
              Generado {new Intl.DateTimeFormat("es-BO", { dateStyle: "short", timeStyle: "short" }).format(new Date(prediction.generated_at))} · {prediction.model_version}
            </div>
          </div>

          {/* Analisis + evidencia + seguimiento */}
          <div className="flex flex-col gap-5">
            <div className="rounded border border-border p-7">
              <h2 className="font-display mb-3.5 text-xl tracking-wide">
                ANÁLISIS DEL MODELO
              </h2>

              {explanationQuery.isLoading ? (
                <p className="text-sm text-muted-foreground">Cargando explicación...</p>
              ) : explanationQuery.isError || !explanationQuery.data ? (
                <p className="text-sm text-muted-foreground">
                  No hay una explicación disponible para este partido todavía.
                </p>
              ) : (
                <>
                  <p className="max-w-[68ch] text-[15px] leading-relaxed text-[#c8cdca]">
                    {explanationQuery.data.text}
                  </p>

                  {explanationQuery.data.evidence.length > 0 && (
                    <div className="mt-5">
                      <div className="mb-2.5 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                        Evidencia utilizada
                      </div>
                      <ul className="flex flex-col gap-2.5">
                        {explanationQuery.data.evidence.map((item) => (
                          <li key={item.id}>
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="block rounded-[3px] border border-border p-3.5 transition hover:border-[#3a423f]"
                            >
                              <span className="text-sm font-semibold transition hover:text-primary">
                                {item.title} ↗
                              </span>
                              <div className="tabular mt-1 text-xs text-muted-foreground">
                                {item.source} · {new Intl.DateTimeFormat("es-BO", { dateStyle: "medium" }).format(new Date(item.published_at))}
                              </div>
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="rounded border border-border p-6">
              <label
                htmlFor="follow-up-question"
                className="mb-2.5 block text-[11px] font-bold uppercase tracking-wide text-muted-foreground"
              >
                Preguntar al modelo
              </label>

              <form onSubmit={handleFollowUp} className="flex gap-2.5">
                <input
                  id="follow-up-question"
                  type="text"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="¿Por qué pesa tanto la forma reciente?"
                  className="flex-grow rounded-[3px] border border-input bg-[#0f1310] px-3.5 py-3 text-sm text-foreground placeholder:text-[#565f5b]"
                />
                <button
                  type="submit"
                  disabled={isSubmitting || !question.trim()}
                  className="rounded-[3px] bg-primary px-5 text-[13px] font-bold uppercase tracking-wide text-primary-foreground transition hover:bg-[#35da7c] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isSubmitting ? "Consultando..." : "Preguntar"}
                </button>
              </form>

              {followUpError && (
                <p role="alert" className="mt-3.5 text-sm text-[#d59b9f]">
                  {followUpError}
                </p>
              )}

              {followUpResponse && (
                <div className="mt-5 border-t border-border pt-5">
                  <p className="font-display text-lg tracking-wide">
                    {followUpResponse.question}
                  </p>
                  <p className="mt-2 text-sm leading-relaxed text-[#c8cdca]">
                    {followUpResponse.answer}
                  </p>
                  {followUpResponse.evidence.length > 0 && (
                    <ul className="mt-3 space-y-1.5">
                      {followUpResponse.evidence.map((item) => (
                        <li key={item.id}>
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary underline underline-offset-4"
                          >
                            {item.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
