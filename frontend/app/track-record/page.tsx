"use client";

import Link from "next/link";
import { Suspense } from "react";
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
      return "Mercado 1X2";
    case "over_under_2_5":
      return "Goles O/U 2.5";
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
  }).format(new Date(date));
}

function resultLabel(hit: boolean) {
  return hit ? "Acierto" : "Falló";
}

export default function TrackRecordPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
          <Cargando />
        </main>
      }
    >
      <TrackRecordContent />
    </Suspense>
  );
}

function TrackRecordContent() {
  const searchParams = useSearchParams();
  const league = searchParams.get("league") ?? "";

  const leaguesQuery = useLeagues();
  const trackRecordQuery = useTrackRecord(league);
  const matchesQuery = useTrackRecordMatches(league, 1);

  if (leaguesQuery.isLoading) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <Cargando />
      </main>
    );
  }

  if (leaguesQuery.isError) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <ErrorState
          error={leaguesQuery.error}
          onRetry={() => void leaguesQuery.refetch()}
        />
      </main>
    );
  }

  const leagues = leaguesQuery.data?.leagues ?? [];

  if (!league) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <div className="mb-8">
          <h1 className="font-display text-4xl tracking-wide">
            TRACK RECORD
          </h1>
          <p className="mt-1.5 max-w-2xl text-[15px] text-muted-foreground">
            Auditoría pública del desempeño del modelo, mercado por mercado.
            Elegí una liga para ver el detalle.
          </p>
        </div>

        {leagues.length === 0 ? (
          <Vacio
            title="No hay ligas disponibles"
            message="El backend todavía no ha publicado ligas para consultar."
          />
        ) : (
          <div
            role="list"
            aria-label="Elegir liga"
            className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
          >
            {leagues.map((item) => (
              <Link
                key={item.id}
                href={`/track-record?league=${encodeURIComponent(item.id)}`}
                role="listitem"
                className="match-card flex items-center justify-between rounded border border-border px-5 py-4"
              >
                <span className="font-display text-xl tracking-wide">
                  {item.name}
                </span>
                <span className="text-primary" aria-hidden="true">
                  →
                </span>
              </Link>
            ))}
          </div>
        )}
      </main>
    );
  }

  if (trackRecordQuery.isLoading || matchesQuery.isLoading) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <Cargando />
      </main>
    );
  }

  if (trackRecordQuery.isError) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <ErrorState
          error={trackRecordQuery.error}
          onRetry={() => void trackRecordQuery.refetch()}
        />
      </main>
    );
  }

  if (matchesQuery.isError) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <ErrorState
          error={matchesQuery.error}
          onRetry={() => void matchesQuery.refetch()}
        />
      </main>
    );
  }

  const data = trackRecordQuery.data;
  const matches = matchesQuery.data?.matches ?? [];

  if (!data || data.markets.length === 0) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <Vacio
          title="Historial no disponible"
          message="Todavía no hay datos suficientes para mostrar el track record de esta liga."
        />
      </main>
    );
  }

  const leagueName =
    leagues.find((item) => item.id === league)?.name ?? data.league;
  const hasMultipleVersions = data.model_versions.length > 1;

  return (
    <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
      <Link
        href="/track-record"
        className="mb-6 inline-block text-xs font-semibold uppercase tracking-wide text-muted-foreground transition hover:text-foreground"
      >
        ← Todas las ligas
      </Link>

      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="font-display text-4xl tracking-wide">{leagueName}</h1>
        <div className="tabular flex gap-6 text-sm text-muted-foreground">
          <span>Ventana <b className="text-foreground">{data.window_size}</b></span>
          <span>Incluidos <b className="text-foreground">{data.matches_included}</b></span>
        </div>
      </div>
      <p className="mb-7 max-w-2xl text-[15px] text-muted-foreground">
        Desempeño histórico del modelo para partidos ya disputados.
      </p>

      {hasMultipleVersions && (
        <div
          role="status"
          className="mb-7 flex gap-3 rounded border border-[#4a3a1e] bg-[#1a160d] px-4.5 py-3.5"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#e8a33d"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mt-0.5 flex-shrink-0"
            aria-hidden="true"
          >
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <p className="text-[13px] leading-relaxed text-[#e8c88d]">
            <b className="text-[#e8a33d]">Ventana con reentrenamiento:</b>{" "}
            este historial incluye más de una versión del modelo (
            {data.model_versions.join(", ")}). No es una serie continua.
          </p>
        </div>
      )}

      <div className="mb-9 grid gap-4 lg:grid-cols-3">
        {data.markets.map((market) => (
          <article
            key={market.market}
            className="rounded border border-border p-5.5"
          >
            <h2 className="font-display text-lg tracking-wide text-primary">
              {marketName(market.market)}
            </h2>

            <p className="tabular mt-3 text-4xl font-semibold">
              {percentage(market.hit_rate)}
            </p>
            <p className="mb-4 text-[11px] uppercase tracking-wide text-muted-foreground">
              Aciertos
            </p>

            <dl className="tabular space-y-2 border-t border-border pt-3.5 text-[13px]">
              <div className="flex justify-between">
                <dt className="font-sans text-muted-foreground">
                  Brier score
                </dt>
                <dd>{market.avg_brier_score.toFixed(3)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-sans text-muted-foreground">Log-loss</dt>
                <dd>{market.avg_log_loss.toFixed(3)}</dd>
              </div>
              {market.avg_market_log_loss !== null && (
                <div className="flex justify-between">
                  <dt className="font-sans text-muted-foreground">
                    Baseline de mercado
                  </dt>
                  <dd>{market.avg_market_log_loss.toFixed(3)}</dd>
                </div>
              )}
            </dl>

            <p className="tabular mt-4 border-t border-border pt-3 text-[11px] text-muted-foreground">
              N = {data.matches_included}
            </p>
          </article>
        ))}
      </div>

      <h2 className="font-display mb-4 text-2xl tracking-wide">
        HISTORIAL PARTIDO A PARTIDO
      </h2>

      {matches.length === 0 ? (
        <Vacio
          title="Sin partidos históricos"
          message="No hay partidos disponibles para el detalle del historial."
        />
      ) : (
        <div className="overflow-hidden rounded border border-border">
          <table className="w-full border-collapse text-[14px]">
            <thead>
              <tr className="border-b border-border text-left text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3 font-bold">Fecha</th>
                <th className="px-4 py-3 font-bold">Partido</th>
                <th className="px-4 py-3 font-bold">1X2</th>
                <th className="px-4 py-3 font-bold">O/U 2.5</th>
                <th className="px-4 py-3 font-bold">Ambos marcan</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((match) => (
                <tr key={match.match_id} className="border-b border-[#151a18] last:border-none">
                  <td className="tabular px-4 py-3.5 text-muted-foreground">
                    {formatDate(match.kickoff_at)}
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="font-semibold">
                      {match.home_team} <span className="text-muted-foreground">vs</span>{" "}
                      {match.away_team}
                    </div>
                    <div className="tabular mt-0.5 text-[11px] text-muted-foreground">
                      {match.model_version} · {match.real_result.home_goals}–
                      {match.real_result.away_goals}
                    </div>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={match.hit_1x2 ? "text-primary" : "text-muted-foreground"}
                    >
                      {resultLabel(match.hit_1x2)}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={
                        match.hit_over_under_2_5 ? "text-primary" : "text-muted-foreground"
                      }
                    >
                      {resultLabel(match.hit_over_under_2_5)}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={match.hit_btts ? "text-primary" : "text-muted-foreground"}
                    >
                      {resultLabel(match.hit_btts)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
