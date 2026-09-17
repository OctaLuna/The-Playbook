interface ErrorStateProps {
  error: unknown;
  onRetry: () => void;
}

function getErrorMessage(error: unknown) {
  if (error && typeof error === "object" && "message" in error) {
    const message = error.message;

    if (typeof message === "string" && message.length > 0) {
      return message;
    }
  }

  return "No se pudo cargar la información.";
}

export function Error({ error, onRetry }: ErrorStateProps) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-lg border p-5"
    >
      <p className="font-medium">Ocurrió un error</p>
      <p className="mt-2 text-sm text-muted-foreground">
        {getErrorMessage(error)}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 rounded-md border px-4 py-2 font-medium focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        Reintentar
      </button>
    </div>
  );
}
