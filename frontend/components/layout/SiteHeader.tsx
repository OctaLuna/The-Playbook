import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="border-b border-border bg-background text-foreground">
      <div className="mx-auto flex h-[76px] max-w-6xl items-center justify-between px-6">
        <Link
          href="/"
          className="flex items-center gap-2.5"
          aria-label="The Playbook - inicio"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--accent)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M3 12h4l2 8 4-16 2 8h6" />
          </svg>
          <span className="font-display text-xl tracking-wide">
            THE PLAYBOOK
          </span>
        </Link>

        <nav aria-label="Navegación principal" className="flex items-center gap-9">
          <Link
            href="/"
            className="text-sm font-semibold uppercase tracking-wide text-foreground transition-colors hover:text-primary"
          >
            Partidos
          </Link>

          <Link
            href="/track-record"
            className="text-sm font-semibold uppercase tracking-wide text-muted-foreground transition-colors hover:text-foreground"
          >
            Track Record
          </Link>
        </nav>
      </div>
    </header>
  );
}
