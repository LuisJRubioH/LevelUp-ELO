/**
 * components/ELO/ELOChart.tsx
 * ============================
 * Gráfico de línea de evolución del ELO global del estudiante.
 */

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ELOPoint {
  label: string; // ej: "Intento 1", fecha, etc.
  elo: number;
}

interface ELOChartProps {
  data: ELOPoint[];
  title?: string;
}

export function ELOChart({ data, title = "Evolución ELO" }: ELOChartProps) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-sm">
        Sin datos de ELO aún. ¡Responde algunas preguntas!
      </div>
    );
  }

  return (
    <div>
      {title && <h3 className="text-sm font-medium text-slate-400 mb-3">{title}</h3>}
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="label"
            tick={{ fill: "#64748b", fontSize: 10 }}
            tickLine={false}
          />
          <YAxis
            domain={["auto", "auto"]}
            tick={{ fill: "#64748b", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "8px",
              color: "#f1f5f9",
              fontSize: "12px",
            }}
            formatter={(value) => [`ELO ${Math.round(Number(value))}`, ""]}
          />
          <Line
            type="monotone"
            dataKey="elo"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5, fill: "#8b5cf6" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
