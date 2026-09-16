"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { Cargando } from "@/components/estado/Cargando";
import { Error as ErrorState } from "@/components/estado/Error";
import { Vacio } from "@/components/estado/Vacio";
import { useLeagues, useUpcomingMatches } from "@/lib/api/hooks";

function formatKickoff(kickoffAt: string) {
  return new Intl.DateTimeFormat("es-BO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(kickoffAt));
}

function formatDate(kickoffAt: string) {
  return new Intl.DateTimeFormat("es-BO", {
    day: "2-digit",
    month: "short",
  }).format(new Date(kickoffAt));
}

function leagueLabel(league: string) {
  switch (league) {
    case "premier_league":
      return "Premier League";
    case "la_liga":
      return "La Liga";
    case "serie_a":
      return "Serie A";
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
    case "cancelled":
      return "Cancelado";
    case "played":
      return "Jugado";
    default:
      return status;
  }
}

export default function Home() {
  const searchParams = useSearchParams();
  const league = searchParams.get("league") ?? "";

  const leaguesQuery = useLeagues();
  const matchesQuery = useUpcomingMatches(league, 1);

  if (matchesQuery.isLoading || leaguesQuery.isLoading) {
    return (
      <main className="min-h-[calc(100vh-80px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6] sm:px-8">
        <div className="mx-auto max-w-6xl">
          <Cargando />
        </div>
      </main>
    );
  }

  if (matchesQuery.isError) {
    return (
      <main className="min-h-[calc(100vh-80px)] bg-[#101c18] px-5 py-12 text-[#f4f0e6] sm:px-8">
        <div className="mx-auto max-w-6xl">
          <ErrorState
            error={matchesQuery.error}
            onRetry={() => void matchesQuery.refetch()}
          />
        </div>
      </main>
    );
  }

  const matches = [...(matchesQuery.data?.matches ?? [])].sort(
    (a, b) =>
      new Date(a.kickoff_at).getTime() -
      new Date(b.kickoff_at).getTime(),
  );

  const leagues = leaguesQuery.data?.leagues ?? [];

  return (
    <main className="min-h-[calc(100vh-80px)] bg-[#101c18] text-[#f4f0e6]">
      <section className="relative overflow-hidden border-b border-[#b49a62]/20">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_20%,rgba(180,154,98,0.13),transparent_28rem)]" />

        <div className="relative mx-auto max-w-6xl px-5 pb-14 pt-12 sm:px-8 sm:pb-20 sm:pt-16">
          <div className="max-w-3xl">
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.32em] text-[#b49a62]">
              Football intelligence
            </p>

            <h1 className="font-serif text-5xl leading-[0.95] tracking-[-0.04em] text-[#f4f0e6] sm:text-7xl">
              The week&apos;s
              <br />
              <span className="text-[#b49a62]">fixtures.</span>
            </h1>

            <p className="mt-7 max-w-xl text-base leading-7 text-[#c5c9c2] sm:text-lg">
              Predicciones de fútbol explicables, señales del modelo y
              evidencia para cada partido.
            </p>
          </div>

          <div className="mt-12 flex flex-wrap items-center gap-2 border-t border-[#f4f0e6]/10 pt-5">
            <Link
              href="/"
              className={`rounded-sm border px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] transition ${
                !league
                  ? "border-[#b49a62] bg-[#b49a62] text-[#17221e]"
                  : "border-[#f4f0e6]/15 text-[#c5c9c2] hover:border-[#b49a62]/60 hover:text-[#f4f0e6]"
              }`}
            >
              Todas
            </Link>

            {leagues.map((item) => (
              <Link
                key={item.id}
                href={`/?league=${encodeURIComponent(item.id)}`}
                className={`rounded-sm border px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] transition ${
                  league === item.id
                    ? "border-[#b49a62] bg-[#b49a62] text-[#17221e]"
                    : "border-[#f4f0e6]/15 text-[#c5c9c2] hover:border-[#b49a62]/60 hover:text-[#f4f0e6]"
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="mb-8 flex flex-col gap-3 border-b border-[#f4f0e6]/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#b49a62]">
              Upcoming matches
            </p>
            <h2 className="mt-2 font-serif text-3xl text-[#f4f0e6] sm:text-4xl">
              Próximos partidos
            </h2>
          </div>

          <p className="text-sm text-[#858f89]">
            {matches.length} partidos en agenda
          </p>
        </div>

        {matches.length === 0 ? (
          <Vacio
            title="No hay partidos próximos"
            message="No se encontraron partidos para esta selección."
          />
        ) : (
          <div className="space-y-4">
            {matches.map((match, index) => (
              <article
                key={match.id}
                className="match-card group relative overflow-hidden rounded-sm border border-[#d8cfbd]/15 bg-[#182922] transition duration-300"
                              >
                <div className="absolute bottom-0 left-0 top-0 w-1 bg-[#b49a62] opacity-0 transition group-hover:opacity-100" />

                <div className="grid gap-6 p-5 sm:grid-cols-[90px_1fr_auto] sm:items-center sm:p-7">
                  <div className="border-b border-[#f4f0e6]/10 pb-4 sm:border-b-0 sm:border-r sm:pb-0">
                    <p className="font-serif text-3xl text-[#b49a62]">
                      {String(index + 1).padStart(2, "0")}
                    </p>
                    <p className="mt-1 text-xs uppercase tracking-[0.16em] text-[#77827c]">
                      {formatDate(match.kickoff_at)}
                    </p>
                  </div>

                  <div>
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[#b49a62]">
                        {leagueLabel(match.league)}
                      </span>

                      <span className="h-1 w-1 rounded-full bg-[#b49a62]/60" />

                      <span className="text-xs uppercase tracking-[0.12em] text-[#77827c]">
                        {statusLabel(match.status)}
                      </span>
                    </div>

                    <h3 className="mt-4 font-serif text-2xl leading-tight text-[#f4f0e6] sm:text-3xl">
                      {match.home_team}
                      <span className="mx-3 text-[#b49a62]">vs.</span>
                      {match.away_team}
                    </h3>

                    <p className="mt-3 text-sm text-[#aeb6b0]">
                      {formatKickoff(match.kickoff_at)}
                    </p>

                    {!match.has_prediction && (
                      <p className="mt-4 inline-flex border border-[#f4f0e6]/10 bg-[#101c18] px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-[#858f89]">
                        Predicción no disponible
                      </p>
                    )}
                  </div>

                  <div className="sm:text-right">
                    {match.has_prediction ? (
                      <span className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#d0bd8b]">
                        <span className="h-2 w-2 rounded-full bg-[#b49a62]" />
                        Prediction ready
                      </span>
                    ) : (
                      <span className="text-xs uppercase tracking-[0.14em] text-[#68736d]">
                        Awaiting prediction
                      </span>
                    )}

                    <Link
                      href={`/partidos/${encodeURIComponent(match.id)}`}
                      className="mt-5 block text-xs font-semibold uppercase tracking-[0.18em] text-[#f4f0e6] underline decoration-[#b49a62] underline-offset-8 transition hover:text-[#b49a62] focus:outline-none focus:ring-2 focus:ring-[#b49a62]"
                    >
                      Ver partido →
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <footer className="border-t border-[#f4f0e6]/10">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-7 text-xs uppercase tracking-[0.16em] text-[#68736d] sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <span>The Playbook</span>
          <span>Explorable · Auditable · Football intelligence</span>
        </div>
      </footer>
    </main>
  );
}