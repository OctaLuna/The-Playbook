import Link from "next/link";

export function SiteHeader() {
  return (
    <>
      <header className="border-b border-white/10 bg-[#17352b] text-[#f4f0e6]">
        <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between px-6 py-4">
          <Link
            href="/"
            className="group flex items-center gap-3"
            aria-label="The Playbook - inicio"
          >
            <span className="flex h-10 w-10 items-center justify-center border border-[#b49a62]/60 bg-[#101c18] font-serif text-lg text-[#b49a62]">
              P
            </span>

            <div>
              <div className="font-serif text-lg tracking-[0.18em]">
                THE PLAYBOOK
              </div>
              <div className="text-[10px] uppercase tracking-[0.28em] text-[#aeb6b0]">
                Football intelligence
              </div>
            </div>
          </Link>

          <nav
            aria-label="Navegación principal"
            className="flex items-center gap-6 text-sm"
          >
            <Link
              href="/"
              className="text-[#d8ddd8] transition-colors hover:text-[#b49a62]"
            >
              Partidos
            </Link>

            <Link
              href="/track-record"
              className="text-[#d8ddd8] transition-colors hover:text-[#b49a62]"
            >
              Track Record
            </Link>
          </nav>
        </div>
      </header>

           {/* Football transition */}
      <div
        className="football-track pointer-events-none"
        aria-hidden="true"
      >
        <span className="football-ball">⚽</span>
      </div> 
    </>
  );
}