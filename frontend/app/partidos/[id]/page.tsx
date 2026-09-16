"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
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
    day: "2-digit",
    month: "short",
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
    case "cancelled":
      return "Cancelado";
    case "played":
      return "Jugado";
    default:
      return status;
  }
}

function marketValueClass(value: number) {
  if (value >= 0.5) {
    return "text-[#b49a62]";
  }

  return "text-[#f4f0e6]";
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

  async function handleFollowUp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      return;
    }

    setIsSubmitting(true);
    setFollowUpError(null);

    try {
      const response = await followUp({
        question: trimmedQuestion,
      });

      setFollowUpResponse(response);
    } catch {
      setFollowUpError(
        "No se pudo obtener una respuesta. Intenta nuevamente.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (matchQuery.isLoading || predictionQuery.isLoading) {
    return (
      <main className="min-h-[calc(100vh-80px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6] sm:px-8">
        <div className="mx-auto max-w-6xl">
          <Cargando />
        </div>
      </main>
    );
  }

  if (matchQuery.isError) {
    return (
      <main className="min-h-[calc(100vh-80px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6] sm:px-8">
        <div className="mx-auto max-w-6xl">
          <ErrorState
            error={matchQuery.error}
            onRetry={() => void matchQuery.refetch()}
          />
        </div>
      </main>
    );
  }

  if (!matchQuery.data) {
    return (
      <main className="min-h-[calc(100vh-80px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6] sm:px-8">
        <div className="mx-auto max-w-6xl">
          <Vacio
            title="Partido no encontrado"
            message="No se encontró información para este partido."
          />
        </div>
      </main>
    );
  }

  const match = matchQuery.data;
  const prediction = predictionQuery.data;

  return (
    <main className="min-h-[calc(100vh-80px)] bg-[#101c18] text-[#f4f0e6]">
      <section className="border-b border-[#f4f0e6]/10">
        <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8 sm:py-12">
          <Link
            href="/"
            className="text-xs font-semibold uppercase tracking-[0.18em] text-[#858f89] transition hover:text-[#b49a62] focus:outline-none focus:ring-2 focus:ring-[#b49a62]"
          >
            ← Volver a partidos
          </Link>

          <div className="mt-10 grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#b49a62]">
                {match.league}
              </p>

              <h1 className="mt-4 max-w-4xl font-serif text-5xl leading-[0.95] tracking-[-0.04em] text-[#f4f0e6] sm:text-7xl">
                {match.home_team}
                <span className="mx-3 text-[#b49a62]">vs.</span>
                {match.away_team}
              </h1>

              <p className="mt-6 text-sm uppercase tracking-[0.14em] text-[#9ca59f]">
                {formatKickoff(match.kickoff_at)}
              </p>
            </div>

            <div className="border-l border-[#b49a62]/50 pl-5 lg:min-w-44">
              <p className="text-xs uppercase tracking-[0.18em] text-[#77827c]">
                Match status
              </p>

              <p className="mt-2 font-serif text-2xl text-[#b49a62]">
                {statusLabel(match.status)}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
        {predictionQuery.isError || !prediction ? (
          <div className="rounded-sm border border-[#d8cfbd]/15 bg-[#182922] p-7">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#b49a62]">
              Prediction
            </p>

            <h2 className="mt-3 font-serif text-3xl text-[#f4f0e6]">
              Predicción no disponible
            </h2>

            <p className="mt-3 max-w-xl text-sm leading-6 text-[#9ca59f]">
              Este partido todavía no tiene una predicción generada por el
              modelo.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {prediction.low_data_warning && (
              <div
                role="alert"
                className="border border-[#b49a62]/40 bg-[#30251f] p-5"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#b49a62]">
                  Data notice
                </p>

                <p className="mt-2 font-serif text-xl text-[#f4f0e6]">
                  Datos insuficientes para una predicción confiable.
                </p>

                <p className="mt-2 text-sm leading-6 text-[#b8b4aa]">
                  Las probabilidades mostradas deben interpretarse con
                  precaución.
                </p>
              </div>
            )}

            <section aria-label="Resumen de la predicción">
              <div className="mb-5 flex flex-col gap-3 border-b border-[#f4f0e6]/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#b49a62]">
                    Model prediction
                  </p>

                  <h2 className="mt-2 font-serif text-3xl text-[#f4f0e6]">
                    Match signals
                  </h2>
                </div>

                <div className="border border-[#b49a62]/40 px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-[#77827c]">
                    Confidence
                  </p>
                  <p className="mt-1 font-serif text-xl text-[#b49a62]">
                    {prediction.confidence}
                  </p>
                </div>
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                <article className="rounded-sm border border-[#d8cfbd]/15 bg-[#182922] p-6">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#77827c]">
                    01 · Match result
                  </p>

                  <h3 className="mt-2 font-serif text-2xl text-[#f4f0e6]">
                    1X2
                  </h3>

                  <div className="mt-7 grid grid-cols-3 divide-x divide-[#f4f0e6]/10">
                    <div className="pr-3">
                      <p className="text-xs text-[#77827c]">Local</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.probabilities_1x2.home,
                        )}`}
                      >
                        {percentage(prediction.probabilities_1x2.home)}
                      </p>
                    </div>

                    <div className="px-3">
                      <p className="text-xs text-[#77827c]">Empate</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.probabilities_1x2.draw,
                        )}`}
                      >
                        {percentage(prediction.probabilities_1x2.draw)}
                      </p>
                    </div>

                    <div className="pl-3">
                      <p className="text-xs text-[#77827c]">Visitante</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.probabilities_1x2.away,
                        )}`}
                      >
                        {percentage(prediction.probabilities_1x2.away)}
                      </p>
                    </div>
                  </div>
                </article>

                <article className="rounded-sm border border-[#d8cfbd]/15 bg-[#182922] p-6">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#77827c]">
                    02 · Goals
                  </p>

                  <h3 className="mt-2 font-serif text-2xl text-[#f4f0e6]">
                    Over / Under 2.5
                  </h3>

                  <div className="mt-7 grid grid-cols-2 divide-x divide-[#f4f0e6]/10">
                    <div className="pr-5">
                      <p className="text-xs text-[#77827c]">Over</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.over_under_2_5.over,
                        )}`}
                      >
                        {percentage(prediction.over_under_2_5.over)}
                      </p>
                    </div>

                    <div className="pl-5">
                      <p className="text-xs text-[#77827c]">Under</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.over_under_2_5.under,
                        )}`}
                      >
                        {percentage(prediction.over_under_2_5.under)}
                      </p>
                    </div>
                  </div>
                </article>

                <article className="rounded-sm border border-[#d8cfbd]/15 bg-[#182922] p-6">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#77827c]">
                    03 · Both to score
                  </p>

                  <h3 className="mt-2 font-serif text-2xl text-[#f4f0e6]">
                    Ambos marcan
                  </h3>

                  <div className="mt-7 grid grid-cols-2 divide-x divide-[#f4f0e6]/10">
                    <div className="pr-5">
                      <p className="text-xs text-[#77827c]">Sí</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.btts.yes,
                        )}`}
                      >
                        {percentage(prediction.btts.yes)}
                      </p>
                    </div>

                    <div className="pl-5">
                      <p className="text-xs text-[#77827c]">No</p>
                      <p
                        className={`mt-2 font-serif text-3xl ${marketValueClass(
                          prediction.btts.no,
                        )}`}
                      >
                        {percentage(prediction.btts.no)}
                      </p>
                    </div>
                  </div>
                </article>

                <article className="rounded-sm border border-[#d8cfbd]/15 bg-[#182922] p-6">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#77827c]">
                    04 · Expected goals
                  </p>

                  <h3 className="mt-2 font-serif text-2xl text-[#f4f0e6]">
                    xG
                  </h3>

                  <div className="mt-7 grid grid-cols-2 divide-x divide-[#f4f0e6]/10">
                    <div className="pr-5">
                      <p className="text-xs text-[#77827c]">
                        {match.home_team}
                      </p>
                      <p className="mt-2 font-serif text-3xl text-[#b49a62]">
                        {prediction.xg.home.toFixed(2)}
                      </p>
                    </div>

                    <div className="pl-5">
                      <p className="text-xs text-[#77827c]">
                        {match.away_team}
                      </p>
                      <p className="mt-2 font-serif text-3xl text-[#b49a62]">
                        {prediction.xg.away.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </article>
              </div>
            </section>

            <section
              aria-labelledby="explanation-title"
              className="border border-[#d8cfbd]/15 bg-[#f4f0e6] p-6 text-[#1f2924] sm:p-8"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#8c7443]">
                Model explanation
              </p>

              <h2
                id="explanation-title"
                className="mt-2 font-serif text-3xl text-[#17352b]"
              >
                Why the model sees this match this way
              </h2>

              {explanationQuery.isLoading ? (
                <p className="mt-5 text-sm text-[#657068]">
                  Cargando explicación...
                </p>
              ) : explanationQuery.isError || !explanationQuery.data ? (
                <p className="mt-5 text-sm leading-6 text-[#657068]">
                  No hay una explicación disponible para este partido.
                </p>
              ) : (
                <>
                  <p className="mt-5 max-w-3xl text-base leading-8 text-[#37443d]">
                    {explanationQuery.data.text}
                  </p>

                  {explanationQuery.data.evidence.length > 0 && (
                    <div className="mt-8 border-t border-[#17352b]/15 pt-6">
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#8c7443]">
                        Evidence
                      </p>

                      <ul className="mt-4 space-y-3">
                        {explanationQuery.data.evidence.map((item) => (
                          <li key={item.id}>
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noreferrer"
                              className="group flex items-start gap-3 text-sm text-[#17352b] hover:text-[#7b6333] focus:outline-none focus:ring-2 focus:ring-[#b49a62]"
                            >
                              <span className="mt-1 text-[#b49a62]">↗</span>
                              <span className="underline decoration-[#b49a62]/50 underline-offset-4">
                                {item.title}
                              </span>
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </section>

            <section className="rounded-sm border border-[#d8cfbd]/15 bg-[#182922] p-6 sm:p-8">
              <div className="max-w-2xl">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#b49a62]">
                  Ask the model
                </p>

                <h2 className="mt-2 font-serif text-3xl text-[#f4f0e6]">
                  ¿Quieres profundizar?
                </h2>

                <p className="mt-3 text-sm leading-6 text-[#9ca59f]">
                  Haz una pregunta sobre la explicación de esta predicción.
                </p>
              </div>

              <form
                onSubmit={handleFollowUp}
                className="mt-7 max-w-3xl space-y-4"
              >
                <label
                  htmlFor="follow-up-question"
                  className="text-xs font-semibold uppercase tracking-[0.16em] text-[#77827c]"
                >
                  Tu pregunta
                </label>

                <textarea
                  id="follow-up-question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={4}
                  placeholder="¿Por qué el modelo considera estos factores?"
                  className="w-full resize-y rounded-sm border border-[#f4f0e6]/15 bg-[#101c18] px-4 py-3 text-sm text-[#f4f0e6] placeholder:text-[#68736d] focus:border-[#b49a62] focus:outline-none focus:ring-1 focus:ring-[#b49a62]"
                />

                <button
                  type="submit"
                  disabled={isSubmitting || !question.trim()}
                  className="border border-[#b49a62] bg-[#b49a62] px-5 py-3 text-xs font-bold uppercase tracking-[0.18em] text-[#17221e] transition hover:bg-[#c4ab72] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isSubmitting ? "Consultando..." : "Preguntar →"}
                </button>
              </form>

              {followUpError && (
                <p role="alert" className="mt-5 text-sm text-[#d59b9f]">
                  {followUpError}
                </p>
              )}

              {followUpResponse && (
                <div className="mt-8 max-w-3xl border-t border-[#f4f0e6]/10 pt-7">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#b49a62]">
                    Response
                  </p>

                  <p className="mt-3 font-serif text-xl text-[#f4f0e6]">
                    {followUpResponse.question}
                  </p>

                  <p className="mt-4 text-sm leading-7 text-[#c5c9c2]">
                    {followUpResponse.answer}
                  </p>

                  {followUpResponse.evidence.length > 0 && (
                    <ul className="mt-5 space-y-2">
                      {followUpResponse.evidence.map((item) => (
                        <li key={item.id}>
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-sm text-[#b49a62] underline underline-offset-4 hover:text-[#d0bd8b]"
                          >
                            {item.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </section>

            <div className="border-t border-[#f4f0e6]/10 pt-6 text-xs uppercase tracking-[0.14em] text-[#68736d]">
              Model version: {prediction.model_version}
            </div>
          </div>
        )}
      </section>
    </main>
  );
}