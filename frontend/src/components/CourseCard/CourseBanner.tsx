/**
 * CourseBanner — pixel art banner matched by course-name keyword.
 * Mirror of V1's logic: keyword → /banners/<slug>.png, fallback gradient
 * with course initial. Pixel art preserved via image-rendering: pixelated.
 */

type Props = {
  courseName: string;
  className?: string;
};

const BANNER_RULES: Array<{ test: RegExp; file: string }> = [
  { test: /geometr|geometry/i, file: "geometria.png" },
  { test: /aritm|arithm/i, file: "aritmetica.png" },
  { test: /algebra/i, file: "algebra.png" },
  { test: /logic/i, file: "logica.png" },
  { test: /conteo|combinat/i, file: "conteo_combinatoria.png" },
  { test: /probabil/i, file: "probabilidad.png" },
];

// Strip diacritics so "Geometría" / "Lógica" / "Álgebra" match plain ASCII keywords.
function deburr(s: string): string {
  return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function resolveBanner(name: string): string | null {
  const ascii = deburr(name);
  for (const rule of BANNER_RULES) {
    if (rule.test.test(ascii)) return `/banners/${rule.file}`;
  }
  return null;
}

// Stable hue from the course name so fallback gradients don't all collapse to the same tone.
function hueFromName(name: string): number {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0;
  return h % 360;
}

export function CourseBanner({ courseName, className = "" }: Props) {
  const src = resolveBanner(courseName);
  const initial = courseName.trim().charAt(0).toUpperCase() || "?";

  if (src) {
    return (
      <div
        className={`relative w-full aspect-[16/7] overflow-hidden rounded-t-xl bg-[#0A0A0F] ${className}`}
      >
        <img
          src={src}
          alt=""
          aria-hidden="true"
          className="w-full h-full object-cover"
          style={{ imageRendering: "pixelated" }}
          loading="lazy"
        />
        <div
          className="absolute inset-x-0 bottom-0 h-1/3 pointer-events-none"
          style={{
            background:
              "linear-gradient(180deg, transparent 0%, rgba(10,10,15,0.85) 100%)",
          }}
        />
      </div>
    );
  }

  const hue = hueFromName(courseName);
  return (
    <div
      className={`relative w-full aspect-[16/7] overflow-hidden rounded-t-xl flex items-center justify-center ${className}`}
      style={{
        background: `linear-gradient(135deg, hsl(${hue} 35% 18%) 0%, hsl(${(hue + 40) % 360} 30% 10%) 100%)`,
      }}
      aria-hidden="true"
    >
      <span
        className="text-5xl font-black tracking-tight select-none"
        style={{ color: `hsl(${hue} 55% 72%)`, opacity: 0.85 }}
      >
        {initial}
      </span>
    </div>
  );
}
