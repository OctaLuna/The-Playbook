import { Skeleton } from "@/components/ui/skeleton";

export function Cargando() {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Cargando contenido"
      className="space-y-4"
    >
      <Skeleton className="h-8 w-1/3" />
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-24 w-full" />
    </div>
  );
}
