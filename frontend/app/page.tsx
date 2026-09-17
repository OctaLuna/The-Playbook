"use client";

import Link from "next/link";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { Cargando } from "@/components/estado/Cargando";
import { Error as ErrorState } from "@/components/estado/Error";
import { Vacio } from "@/components/estado/Vacio";
import { useLeagues, useUpcomingMatches } from "@/lib/api/hooks";

function formatKickoff(kickoffAt: string) {
  return new Intl.DateTimeFormat("es-BO", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(kickoffAt));
}

function leagueLabel(league: string) {
  switch (league) {
    case "premier_league":
      return "Premier League";
    case "laliga":
      return "LaLiga";
    case "serie_a":
      return "Serie A";
    case "bundesliga":
      return "Bundesliga";
    case "ligue_1":
      return "Ligue 1";
    default:
      return league;
  }
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

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
          <Cargando />
        </main>
      }
    >
      <HomeContent />
    </Suspense>
  );
}

function HomeContent() {
  const searchParams = useSearchParams();
  const league = searchParams.get("league") ?? "";

  const leaguesQuery = useLeagues();
  const matchesQuery = useUpcomingMatches(league, 1);

  if (matchesQuery.isLoading || leaguesQuery.isLoading) {
    return (
      <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
        <Cargando />
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

  const matches = [...(matchesQuery.data?.matches ?? [])].sort(
    (a, b) =>
      new Date(a.kickoff_at).getTime() - new Date(b.kickoff_at).getTime(),
  );

  const leagues = leaguesQuery.data?.leagues ?? [];

  return (
    <main className="mx-auto min-h-[calc(100vh-76px)] max-w-6xl px-6 py-10">
      <div className="mb-7">
        <h1 className="font-display text-4xl tracking-wide">
          PRÓXIMOS PARTIDOS
        </h1>
        <p className="mt-1.5 text-[15px] text-muted-foreground">
          Las cinco grandes ligas, ordenadas por proximidad al kickoff.
        </p>
      </div>

      <div
        role="group"
        aria-label="Filtrar por liga"
        className="mb-7 flex flex-wrap gap-2.5"
      >
        <Link
          href="/"
          aria-current={!league ? "true" : undefined}
          className={`rounded-[3px] border px-4 py-2 text-[13px] font-semibold uppercase tracking-wide transition ${
            !league
              ? "border-primary bg-primary text-primary-foreground"
              : "border-border text-[#c8cdca] hover:border-[#3a423f]"
          }`}
        >
          Todas
        </Link>

        {leagues.map((item) => (
          <Link
            key={item.id}
            href={`/?league=${encodeURIComponent(item.id)}`}
            aria-current={league === item.id ? "true" : undefined}
            className={`rounded-[3px] border px-4 py-2 text-[13px] font-semibold uppercase tracking-wide transition ${
              league === item.id
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border text-[#c8cdca] hover:border-[#3a423f]"
            }`}
          >
            {item.name}
          </Link>
        ))}
      </div>

      {matches.length === 0 ? (
        <Vacio
          title="No hay partidos próximos"
          message="No se encontraron partidos para esta selección."
        />
      ) : (
        <div
          role="list"
          aria-label="Próximos partidos"
          className="overflow-hidden rounded border border-border"
        >
          {matches.map((match, index) => (
            <Link
              key={match.id}
              href={`/partidos/${encodeURIComponent(match.id)}`}
              role="listitem"
              className={`match-card flex items-center gap-6 px-6 py-4.5 ${
                index < matches.length - 1 ? "border-b border-border" : ""
              }`}
            >
              <div className="tabular w-[100px] flex-shrink-0">
                <div className="text-xs uppercase text-muted-foreground">
                  {formatKickoff(match.kickoff_at).split(",")[0]}
                </div>
                <div className="text-[15px] font-semibold">
                  {formatKickoff(match.kickoff_at).split(",")[1]?.trim()}
                </div>
              </div>

              <div className="min-w-0 flex-grow">
                <div className="font-display text-2xl tracking-wide">
                  {match.home_team}{" "}
                  <span className="text-muted-foreground">vs</span>{" "}
                  {match.away_team}
                </div>
                <div className="mt-0.5 text-xs text-muted-foreground">
                  {leagueLabel(match.league)}
                  {match.status !== "scheduled" && (
                    <> · {statusLabel(match.status)}</>
                  )}
                </div>
              </div>

              <span
                className={`flex-shrink-0 rounded-full border px-3 py-1.5 text-xs font-bold uppercase tracking-wide ${
                  match.has_prediction
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-[#3a423f] text-muted-foreground"
                }`}
              >
                {match.has_prediction ? "Predicción lista" : "Sin predicción"}
              </span>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
