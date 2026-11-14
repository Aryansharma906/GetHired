/** Lightweight vector artwork, drawn locally. No external images or tracking. */
export function CareerArt({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 380 260" fill="none" aria-hidden="true" className={`hero-art ${className}`}>
      <circle cx="210" cy="133" r="104" stroke="currentColor" strokeOpacity=".12" />
      <circle cx="210" cy="133" r="80" stroke="currentColor" strokeOpacity=".18" strokeDasharray="3 7" />
      <path d="M85 212C134 211 155 89 229 80C261 75 289 85 326 47" stroke="currentColor" strokeOpacity=".3" strokeWidth="2" />
      <g transform="rotate(-12 180 135)">
        <rect x="110" y="38" width="142" height="186" rx="13" fill="var(--color-accent-soft)" stroke="var(--color-accent-line)" />
      </g>
      <g transform="rotate(8 207 140)">
        <rect x="134" y="43" width="142" height="186" rx="13" fill="var(--color-card)" stroke="var(--color-accent-line)" />
        <rect x="154" y="63" width="30" height="30" rx="8" fill="var(--color-accent-soft)" />
        <path d="M163 74h12m-12 5h8m-8 5h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M195 71h57M195 81h38" stroke="currentColor" strokeOpacity=".5" strokeWidth="3" strokeLinecap="round" />
        <path d="M155 111h99M155 123h89M155 135h99M155 156h60M155 168h99M155 180h81M155 192h91" stroke="currentColor" strokeOpacity=".18" strokeWidth="3" strokeLinecap="round" />
        <path d="M155 209h35" stroke="currentColor" strokeOpacity=".5" strokeWidth="3" strokeLinecap="round" />
      </g>
      <rect x="249" y="159" width="67" height="48" rx="12" fill="var(--color-accent)" />
      <path d="m269 183 8 8 19-20" stroke="var(--color-on-primary)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="103" cy="72" r="19" fill="var(--color-card)" stroke="var(--color-accent-line)" />
      <path d="m103 61 2.5 8.5L114 72l-8.5 2.5L103 83l-2.5-8.5L92 72l8.5-2.5z" fill="currentColor" fillOpacity=".7" />
      <circle cx="314" cy="83" r="4" fill="currentColor" fillOpacity=".45" />
      <circle cx="83" cy="171" r="3" fill="currentColor" fillOpacity=".4" />
      <path d="M316 122v12m-6-6h12" stroke="currentColor" strokeOpacity=".5" strokeWidth="1.5" />
    </svg>
  );
}
