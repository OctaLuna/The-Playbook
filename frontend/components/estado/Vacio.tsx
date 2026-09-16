interface VacioProps {
  title?: string;
  message?: string;
}

export function Vacio({
  title = "Sin resultados",
  message = "No hay información disponible.",
}: VacioProps) {
  return (
    <div className="flex min-h-32 flex-col items-center justify-center rounded-lg border p-6 text-center">
      <p className="font-medium">{title}</p>
      <p className="mt-1 text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
