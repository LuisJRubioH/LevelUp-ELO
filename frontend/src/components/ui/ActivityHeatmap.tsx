/**
 * components/ui/ActivityHeatmap.tsx
 * ===================================
 * Heatmap de actividad diaria (últimas 10 semanas × 7 días).
 * Recibe un objeto {date: count} donde date = "YYYY-MM-DD".
 */

interface ActivityHeatmapProps {
  data: Record<string, number>; // "YYYY-MM-DD" → intentos ese día
  weeks?: number; // número de semanas a mostrar (default 10)
}

const DAYS = ["L", "M", "X", "J", "V", "S", "D"];

function getColor(count: number): string {
  if (count === 0) return "bg-slate-800";
  if (count < 3) return "bg-violet-900/70";
  if (count < 7) return "bg-violet-700";
  if (count < 15) return "bg-violet-500";
  return "bg-violet-400";
}

/** Genera el grid de las últimas N semanas (lunes a domingo). */
function buildGrid(data: Record<string, number>, weeks: number) {
  const today = new Date();
  // Avanzar al próximo domingo (o hoy si es domingo)
  const dayOfWeek = today.getDay(); // 0=Dom, 1=Lun...
  const daysUntilSunday = dayOfWeek === 0 ? 0 : 7 - dayOfWeek;
  const endDate = new Date(today);
  endDate.setDate(today.getDate() + daysUntilSunday);

  const grid: { date: string; count: number }[][] = [];

  for (let w = weeks - 1; w >= 0; w--) {
    const week: { date: string; count: number }[] = [];
    for (let d = 0; d < 7; d++) {
      const date = new Date(endDate);
      date.setDate(endDate.getDate() - w * 7 - (6 - d));
      const key = date.toISOString().slice(0, 10);
      week.push({ date: key, count: data[key] ?? 0 });
    }
    grid.push(week);
  }
  return grid;
}

export function ActivityHeatmap({ data, weeks = 10 }: ActivityHeatmapProps) {
  const grid = buildGrid(data, weeks);
  const total = Object.values(data).reduce((s, v) => s + v, 0);

  return (
    <div>
      <div className="flex items-end gap-1 mb-1">
        {/* Etiquetas de días */}
        <div className="flex flex-col gap-0.5 mr-1">
          {DAYS.map((d) => (
            <span key={d} className="text-[9px] text-slate-600 h-3 flex items-center">
              {d}
            </span>
          ))}
        </div>
        {/* Grid semanas */}
        {grid.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-0.5">
            {week.map((cell) => (
              <div
                key={cell.date}
                className={`w-3 h-3 rounded-[2px] ${getColor(cell.count)} transition-colors`}
                title={cell.count > 0 ? `${cell.date}: ${cell.count} intentos` : cell.date}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-slate-500">{total} intentos en {weeks} semanas</span>
        <div className="flex items-center gap-1">
          <span className="text-[9px] text-slate-600">Menos</span>
          {["bg-slate-800", "bg-violet-900/70", "bg-violet-700", "bg-violet-500", "bg-violet-400"].map((c, i) => (
            <div key={i} className={`w-2.5 h-2.5 rounded-[2px] ${c}`} />
          ))}
          <span className="text-[9px] text-slate-600">Más</span>
        </div>
      </div>
    </div>
  );
}
