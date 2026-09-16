import { API_BASE_URL } from "./config";

export class ApiError extends Error {
  readonly status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export class NetworkError extends ApiError {
  constructor(message = "No se pudo conectar con el backend") {
    super(message, null);
    this.name = "NetworkError";
  }
}

export class NotFoundError extends ApiError {
  constructor(message = "Recurso no encontrado") {
    super(message, 404);
    this.name = "NotFoundError";
  }
}

export class ServerError extends ApiError {
  constructor(status: number, message = "Error del servidor") {
    super(message, status);
    this.name = "ServerError";
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
  } catch {
    throw new NetworkError();
  }

  if (response.status === 404) {
    throw new NotFoundError();
  }

  if (response.status >= 500) {
    throw new ServerError(response.status);
  }

  if (!response.ok) {
    throw new ApiError(
      `Error de API: ${response.status} ${response.statusText}`,
      response.status,
    );
  }

  return (await response.json()) as T;
}

export const apiClient = {
  get<T>(path: string): Promise<T> {
    return request<T>(path);
  },

  post<TResponse, TBody>(
    path: string,
    body: TBody,
  ): Promise<TResponse> {
    return request<TResponse>(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};
