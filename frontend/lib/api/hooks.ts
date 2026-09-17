import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import {
  demoExplanations,
  demoMatches,
  demoPredictions,
  demoTrackRecord,
  demoTrackRecordMatches,
  demoUpcomingMatches,
} from "./demo-data";
import type {
  ExplanationResponse,
  FollowUpResponse,
  FollowUpRequest,
  LeaguesResponse,
  MatchDetail,
  PredictionResponse,
  TrackRecordMatchesResponse,
  TrackRecordResponse,
  UpcomingMatchesResponse,
} from "./types";

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

export function useLeagues() {
  return useQuery({
    queryKey: ["leagues"],
    queryFn: async () => {
      if (DEMO_MODE) {
        return {
          leagues: [
            { id: "premier_league", name: "Premier League" },
            { id: "la_liga", name: "La Liga" },
            { id: "serie_a", name: "Serie A" },
          ],
        } satisfies LeaguesResponse;
      }

      return apiClient.get<LeaguesResponse>("/api/leagues");
    },
  });
}

export function useUpcomingMatches(league: string, page = 1) {
  const params = new URLSearchParams({ page: String(page) });

  if (league) {
    params.set("league", league);
  }

  return useQuery({
    queryKey: ["matches", "upcoming", league, page],
    queryFn: async () => {
      if (DEMO_MODE) {
        const matches = league
          ? demoUpcomingMatches.matches.filter(
              (match) =>
                match.league.toLowerCase().replaceAll(" ", "_") === league,
            )
          : demoUpcomingMatches.matches;

        return {
          ...demoUpcomingMatches,
          matches,
        } satisfies UpcomingMatchesResponse;
      }

      return apiClient.get<UpcomingMatchesResponse>(
        `/api/matches/upcoming?${params.toString()}`,
      );
    },
  });
}

export function useMatch(matchId: string) {
  return useQuery({
    queryKey: ["match", matchId],
    queryFn: async () => {
      if (DEMO_MODE) {
        return demoMatches[matchId] ?? null;
      }

      return apiClient.get<MatchDetail>(
        `/api/matches/${encodeURIComponent(matchId)}`,
      );
    },
    enabled: Boolean(matchId),
  });
}

export function usePrediction(matchId: string) {
  return useQuery({
    queryKey: ["prediction", matchId],
    queryFn: async () => {
      if (DEMO_MODE) {
        return demoPredictions[matchId] ?? null;
      }

      return apiClient.get<PredictionResponse>(
        `/api/matches/${encodeURIComponent(matchId)}/prediction`,
      );
    },
    enabled: Boolean(matchId),
  });
}

export function useExplanation(matchId: string) {
  return useQuery({
    queryKey: ["explanation", matchId],
    queryFn: async () => {
      if (DEMO_MODE) {
        return demoExplanations[matchId] ?? null;
      }

      return apiClient.get<ExplanationResponse>(
        `/api/matches/${encodeURIComponent(matchId)}/explanation`,
      );
    },
    enabled: Boolean(matchId),
  });
}

export function useFollowUp(matchId: string) {
  return async (request: FollowUpRequest): Promise<FollowUpResponse> => {
    if (DEMO_MODE) {
      return {
        match_id: matchId,
        question: request.question,
        answer:
          "La respuesta de seguimiento aparecerá aquí cuando el servicio de explicación esté conectado al backend.",
        evidence: demoExplanations[matchId]?.evidence ?? [],
        generated_at: new Date().toISOString(),
      };
    }

    return apiClient.post<FollowUpResponse, FollowUpRequest>(
      `/api/matches/${encodeURIComponent(matchId)}/explanation/follow-up`,
      request,
    );
  };
}

export function useTrackRecord(league: string) {
  const params = new URLSearchParams();

  if (league) {
    params.set("league", league);
  }

  const query = params.toString();

  return useQuery({
    queryKey: ["trackRecord", league],
    queryFn: async () => {
      if (DEMO_MODE) {
        return {
          ...demoTrackRecord,
          league: league || demoTrackRecord.league,
        } satisfies TrackRecordResponse;
      }

      return apiClient.get<TrackRecordResponse>(
        `/api/track-record${query ? `?${query}` : ""}`,
      );
    },
  });
}

export function useTrackRecordMatches(league: string, page = 1) {
  const params = new URLSearchParams({ page: String(page) });

  if (league) {
    params.set("league", league);
  }

  const query = params.toString();

  return useQuery({
    queryKey: ["trackRecord", "matches", league, page],
    queryFn: async () => {
      if (DEMO_MODE) {
        return demoTrackRecordMatches satisfies TrackRecordMatchesResponse;
      }

      return apiClient.get<TrackRecordMatchesResponse>(
        `/api/track-record/matches?${query}`,
      );
    },
  });
}