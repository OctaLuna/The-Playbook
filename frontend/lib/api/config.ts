const backendBaseUrl = process.env.NEXT_PUBLIC_API_URL;

if (!backendBaseUrl) {
  throw new Error("NEXT_PUBLIC_API_URL no está configurada");
}

export const API_BASE_URL = backendBaseUrl.replace(/\/$/, "");
