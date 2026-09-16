"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { Cargando } from "@/components/estado/Cargando";
import { Error as ErrorState } from "@/components/estado/Error";
import { Vacio } from "@/components/estado/Vacio";
import {
  useLeagues,
  useTrackRecord,
  useTrackRecordMatches,
} from "@/lib/api/hooks";

function marketName(market: string) {
  switch (market) {
    case "1x2":
      return "1X2";
    case "over_under_2_5":
      return "Over / Under 2.5";
    case "btts":
      return "Ambos marcan";
    default:
      return market;
  }
}

function percentage(value: number) {
  return `${Math.round(value * 100)}%`;
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat("es-BO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
}

function resultLabel(hit: boolean) {
  return hit ? "Acierto" : "Falló";
}

function resultStyle(hit: boolean) {
  return hit
    ? "border-[#4c6b5d] bg-[#20382f] text-[#d8e4dc]"
    : "border-[#694044] bg-[#39282a] text-[#e4cfd1]";
}

function predictionLabel(value: boolean) {
  return value ? "✓" : "—";
}

export default function TrackRecordPage() {
  const searchParams = useSearchParams();
  const league = searchParams.get("league") ?? "";

  const leaguesQuery = useLeagues();
  const trackRecordQuery = useTrackRecord(league);
  const matchesQuery = useTrackRecordMatches(league, 1);

  if (leaguesQuery.isLoading) {
    return <Cargando />;
  }

  if (leaguesQuery.isError) {
    return (
      <ErrorState
        error={leaguesQuery.error}
        onRetry={() => {
          void leaguesQuery.refetch();
        }}
      />
    );
  }

  const leagues = leaguesQuery.data?.leagues ?? [];

  if (!league) {
    return (
      <main className="min-h-[calc(100vh-76px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6]">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 max-w-3xl">
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.28em] text-[#b49a62]">
              Track Record
            </p>

            <h1 className="text-4xl font-semibold tracking-tight text-[#f4f0e6] sm:text-6xl">
              Historial público
              <br />
              <span className="text-[#aeb6b0]">del modelo.</span>
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-7 text-[#aeb6b0]">
              Revisa el desempeño histórico de las predicciones por liga y
              mercado. Los resultados mostrados corresponden exclusivamente a
              datos entregados por el backend.
            </p>
          </div>

          <section>
            <div className="mb-5 flex items-end justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#77827c]">
                  Select competition
                </p>
                <h2 className="mt-2 font-serif text-2xl text-[#f4f0e6]">
                  Elige una liga
                </h2>
              </div>
            </div>

            {leagues.length === 0 ? (
              <Vacio
                title="No hay ligas disponibles"
                message="El backend todavía no ha publicado ligas para consultar."
              />
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {leagues.map((item) => (
                  <Link
                    key={item.id}
                    href={`/track-record?league=${encodeURIComponent(item.id)}`}
                    className="group rounded-sm border border-[#2d4038] bg-[#182922] p-6 transition hover:border-[#b49a62] hover:bg-[#1d3029]"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-xs uppercase tracking-[0.18em] text-[#77827c]">
                          Competition
                        </p>

                        <h3 className="mt-3 font-serif text-2xl text-[#f4f0e6]">
                          {item.name}
                        </h3>
                      </div>

                      <span className="text-xl text-[#b49a62] transition group-hover:translate-x-1">
                        →
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </section>
        </div>
      </main>
    );
  }

  if (trackRecordQuery.isLoading || matchesQuery.isLoading) {
    return <Cargando />;
  }

  if (trackRecordQuery.isError) {
    return (
      <ErrorState
        error={trackRecordQuery.error}
        onRetry={() => {
          void trackRecordQuery.refetch();
        }}
      />
    );
  }

  if (matchesQuery.isError) {
    return (
      <ErrorState
        error={matchesQuery.error}
        onRetry={() => {
          void matchesQuery.refetch();
        }}
      />
    );
  }

  const data = trackRecordQuery.data;
  const matches = matchesQuery.data?.matches ?? [];

  if (!data || data.markets.length === 0) {
    return (
      <main className="min-h-[calc(100vh-76px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6]">
        <div className="mx-auto max-w-6xl">
          <Vacio
            title="Historial no disponible"
            message="Todavía no hay datos suficientes para mostrar el track record de esta liga."
          />
        </div>
      </main>
    );
  }

  const leagueName =
    leagues.find((item) => item.id === league)?.name ?? data.league;

  const hasMultipleVersions = data.model_versions.length > 1;

  return (
    <main className="min-h-[calc(100vh-76px)] bg-[#101c18] text-[#f4f0e6]">
      <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="mb-10">
          <Link
            href="/track-record"
            className="text-xs font-semibold uppercase tracking-[0.18em] text-[#77827c] transition hover:text-[#b49a62]"
          >
            ← Track Record
          </Link>
        </div>

        <section className="overflow-hidden rounded-sm border border-[#2d4038] bg-[#17352b]">
          <div className="grid lg:grid-cols-[1.4fr_1fr]">
            <div className="p-7 sm:p-10 lg:p-12">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#b49a62]">
                Track Record
              </p>

              <h1 className="mt-4 font-serif text-4xl leading-tight text-[#f4f0e6] sm:text-6xl">
                {leagueName}
              </h1>

              <p className="mt-5 max-w-2xl text-base leading-7 text-[#b8c0bb]">
                Historial público del modelo para evaluar cómo se han comportado
                sus predicciones en partidos ya disputados.
              </p>
            </div>

            <div className="grid grid-cols-2 border-t border-[#315044] lg:border-l lg:border-t-0">
              <div className="border-b border-r border-[#315044] p-6">
                <p className="text-[11px] uppercase tracking-[0.16em] text-[#81918a]">
                  Window
                </p>

                <p className="mt-3 font-serif text-3xl text-[#f4f0e6]">
                  {data.window_size}
                </p>

                <p className="mt-1 text-sm text-[#8e9b95]">partidos</p>
              </div>

              <div className="border-b border-[#315044] p-6">
                <p className="text-[11px] uppercase tracking-[0.16em] text-[#81918a]">
                  Included
                </p>

                <p className="mt-3 font-serif text-3xl text-[#f4f0e6]">
                  {data.matches_included}
                </p>

                <p className="mt-1 text-sm text-[#8e9b95]">evaluados</p>
              </div>

              <div className="border-r border-[#315044] p-6">
                <p className="text-[11px] uppercase tracking-[0.16em] text-[#81918a]">
                  Models
                </p>

                <p className="mt-3 font-serif text-2xl text-[#f4f0e6]">
                  {data.model_versions.length}
                </p>

                <p className="mt-1 text-sm text-[#8e9b95]">
                  versión{data.model_versions.length === 1 ? "" : "es"}
                </p>
              </div>

              <div className="p-6">
                <p className="text-[11px] uppercase tracking-[0.16em] text-[#81918a]">
                  Updated
                </p>

                <p className="mt-3 text-sm leading-6 text-[#d5dbd7]">
                  {formatDate(data.last_updated_at)}
                </p>
              </div>
            </div>
          </div>
        </section>

        {hasMultipleVersions && (
          <section className="mt-5 border border-[#66543a] bg-[#30251f] px-5 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#b49a62]">
              Model version notice
            </p>

            <p className="mt-2 text-sm leading-6 text-[#d8d0c4]">
              Este historial incluye más de una versión del modelo. Las
              versiones registradas son:{" "}
              <span className="font-semibold text-[#f4f0e6]">
                {data.model_versions.join(", ")}
              </span>
              .
            </p>
          </section>
        )}

        <section className="mt-14">
          <div className="mb-7">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#b49a62]">
              Market performance
            </p>

            <h2 className="mt-2 font-serif text-3xl text-[#f4f0e6] sm:text-4xl">
              Rendimiento por mercado
            </h2>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-[#8f9a94]">
              Métricas calculadas y publicadas por el backend para cada mercado
              evaluado.
            </p>
          </div>

          <div className="grid gap-5 lg:grid-cols-3">
            {data.markets.map((market) => (
              <article
                key={market.market}
                className="border border-[#2d4038] bg-[#182922] p-6 sm:p-7"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#77827c]">
                      Market
                    </p>

                    <h3 className="mt-2 font-serif text-2xl text-[#f4f0e6]">
                      {marketName(market.market)}
                    </h3>
                  </div>

                  <span className="border border-[#43554c] px-2 py-1 text-[10px] uppercase tracking-[0.15em] text-[#aeb6b0]">
                    Public
                  </span>
                </div>

                <div className="mt-8 border-t border-[#2d4038] pt-6">
                  <p className="text-[11px] uppercase tracking-[0.16em] text-[#77827c]">
                    Hit rate
                  </p>

                  <p className="mt-2 font-serif text-5xl text-[#f4f0e6]">
                    {percentage(market.hit_rate)}
                  </p>
                </div>

                <dl className="mt-7 space-y-4 text-sm">
                  <div className="flex items-center justify-between gap-4">
                    <dt className="text-[#8f9a94]">Brier score</dt>
                    <dd className="font-medium text-[#dce2de]">
                      {market.avg_brier_score.toFixed(3)}
                    </dd>
                  </div>

                  <div className="flex items-center justify-between gap-4">
                    <dt className="text-[#8f9a94]">Log loss</dt>
                    <dd className="font-medium text-[#dce2de]">
                      {market.avg_log_loss.toFixed(3)}
                    </dd>
                  </div>

                  <div className="flex items-center justify-between gap-4">
                    <dt className="text-[#8f9a94]">Baseline log loss</dt>
                    <dd className="font-medium text-[#dce2de]">
                      {market.avg_market_log_loss !== null
                        ? market.avg_market_log_loss.toFixed(3)
                        : "No disponible"}
                    </dd>
                  </div>

                  <div className="flex items-center justify-between gap-4 border-t border-[#2d4038] pt-4">
                    <dt className="text-[#8f9a94]">Baseline matches</dt>
                    <dd className="font-medium text-[#dce2de]">
                      {market.market_baseline_matches}
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-16">
          <div className="mb-7 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#b49a62]">
                Match by match
              </p>

              <h2 className="mt-2 font-serif text-3xl text-[#f4f0e6] sm:text-4xl">
                Detalle de partidos
              </h2>
            </div>

            <p className="text-sm text-[#77827c]">
              {matches.length} registro{matches.length === 1 ? "" : "s"}{" "}
              visibles
            </p>
          </div>

          {matches.length === 0 ? (
            <Vacio
              title="Sin partidos históricos"
              message="No hay partidos disponibles para el detalle del historial."
            />
          ) : (
            <div className="space-y-4">
              {matches.map((match) => (
                <article
                  key={match.match_id}
                  className="border border-[#2d4038] bg-[#182922]"
                >
                  <div className="grid lg:grid-cols-[1.2fr_0.8fr]">
                    <div className="p-6 sm:p-7">
                      <div className="flex flex-wrap items-center gap-3">
                        <span className="text-[11px] uppercase tracking-[0.16em] text-[#77827c]">
                          {match.league}
                        </span>

                        <span className="h-1 w-1 rounded-full bg-[#b49a62]" />

                        <span className="text-[11px] text-[#77827c]">
                          {formatDate(match.kickoff_at)}
                        </span>
                      </div>

                      <div className="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-4">
                        <div>
                          <p className="font-serif text-xl text-[#f4f0e6] sm:text-2xl">
                            {match.home_team}
                          </p>

                          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-[#77827c]">
                            Home
                          </p>
                        </div>

                        <div className="text-center">
                          <p className="font-serif text-3xl text-[#b49a62]">
                            {match.real_result.home_goals}–
                            {match.real_result.away_goals}
                          </p>

                          <p className="mt-1 text-[10px] uppercase tracking-[0.16em] text-[#77827c]">
                            Final
                          </p>
                        </div>

                        <div className="text-right">
                          <p className="font-serif text-xl text-[#f4f0e6] sm:text-2xl">
                            {match.away_team}
                          </p>

                          <p className="mt-1 text-xs uppercase tracking-[0.14em] text-[#77827c]">
                            Away
                          </p>
                        </div>
                      </div>

                      <div className="mt-7 border-t border-[#2d4038] pt-5">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <p className="text-[11px] uppercase tracking-[0.16em] text-[#77827c]">
                            Model version
                          </p>

                          <span className="text-xs text-[#aeb6b0]">
                            {match.model_version}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-[#2d4038] lg:border-l lg:border-t-0">
                      <div className="grid grid-cols-3 border-b border-[#2d4038]">
                        <div className="border-r border-[#2d4038] p-4">
                          <p className="text-[10px] uppercase tracking-[0.14em] text-[#77827c]">
                            1X2
                          </p>

                          <p className="mt-3 text-sm font-medium text-[#dce2de]">
                            {predictionLabel(match.hit_1x2)}{" "}
                            {resultLabel(match.hit_1x2)}
                          </p>

                          <p className="mt-3 text-xs text-[#77827c]">
                            H {percentage(match.predicted_1x2.home)} · D{" "}
                            {percentage(match.predicted_1x2.draw)} · A{" "}
                            {percentage(match.predicted_1x2.away)}
                          </p>
                        </div>

                        <div className="border-r border-[#2d4038] p-4">
                          <p className="text-[10px] uppercase tracking-[0.14em] text-[#77827c]">
                            O/U 2.5
                          </p>

                          <p className="mt-3 text-sm font-medium text-[#dce2de]">
                            {predictionLabel(match.hit_over_under_2_5)}{" "}
                            {resultLabel(match.hit_over_under_2_5)}
                          </p>

                          <p className="mt-3 text-xs text-[#77827c]">
                            O {percentage(match.predicted_over_under_2_5.over)}{" "}
                            · U{" "}
                            {percentage(match.predicted_over_under_2_5.under)}
                          </p>
                        </div>

                        <div className="p-4">
                          <p className="text-[10px] uppercase tracking-[0.14em] text-[#77827c]">
                            BTTS
                          </p>

                          <p className="mt-3 text-sm font-medium text-[#dce2de]">
                            {predictionLabel(match.hit_btts)}{" "}
                            {resultLabel(match.hit_btts)}
                          </p>

                          <p className="mt-3 text-xs text-[#77827c]">
                            Sí {percentage(match.predicted_btts.yes)} · No{" "}
                            {percentage(match.predicted_btts.no)}
                          </p>
                        </div>
                      </div>

                      <div className="p-5">
                        <p className="text-[10px] uppercase tracking-[0.16em] text-[#77827c]">
                          Prediction status
                        </p>

                        <div className="mt-4 flex flex-wrap gap-2">
                          <span
                            className={`border px-3 py-1.5 text-xs ${resultStyle(
                              match.hit_1x2,
                            )}`}
                          >
                            1X2 · {resultLabel(match.hit_1x2)}
                          </span>

                          <span
                            className={`border px-3 py-1.5 text-xs ${resultStyle(
                              match.hit_over_under_2_5,
                            )}`}
                          >
                            O/U · {resultLabel(match.hit_over_under_2_5)}
                          </span>

                          <span
                            className={`border px-3 py-1.5 text-xs ${resultStyle(
                              match.hit_btts,
                            )}`}
                          >
                            BTTS · {resultLabel(match.hit_btts)}
                          </span>
                        </div>

                        <div className="mt-5 border-t border-[#2d4038] pt-4">
                          <p className="text-[10px] uppercase tracking-[0.16em] text-[#77827c]">
                            Market baseline
                          </p>

                          {match.has_market_odds &&
                          match.market_implied_1x2 ? (
                            <p className="mt-2 text-xs leading-5 text-[#8f9a94]">
                              Probabilidades implícitas agregadas: H{" "}
                              {percentage(match.market_implied_1x2.home)} · D{" "}
                              {percentage(match.market_implied_1x2.draw)} · A{" "}
                              {percentage(match.market_implied_1x2.away)}
                            </p>
                          ) : (
                            <p className="mt-2 text-xs leading-5 text-[#77827c]">
                              No disponible para este partido.
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <footer className="mt-16 border-t border-[#2d4038] pt-6">
          <div className="flex flex-col gap-2 text-xs text-[#69766f] sm:flex-row sm:items-center sm:justify-between">
            <p>THE PLAYBOOK · Public model history</p>

            <p>
              Los valores mostrados provienen del backend y no se recalculan en
              la interfaz.
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
