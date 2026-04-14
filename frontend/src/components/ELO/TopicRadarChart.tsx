/**
 * components/ELO/TopicRadarChart.tsx
 * ====================================
 * Gráfico radar del rendimiento por tópico (top 8 por ELO).
 * Escala 0–3000 → 0–100 para el eje radial.
 */

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface TopicPoint {
  topic: string;
  rating: number;
}

interface TopicRadarChartProps {
  topics: TopicPoint[];
}

const MAX_ELO = 3000;
const MIN_ELO = 400;

function truncate(str: string, max = 14) {
  return str.length > max ? str.slice(0, max - 1) + "…" : str;
}

export function TopicRadarChart({ topics }: TopicRadarChartProps) {
  if (topics.length < 3) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-sm">
        Necesitas al menos 3 tópicos para el radar. ¡Practica más cursos!
      </div>
    );
  }

  // Top 8 por rating, normalizar a 0–100
  const data = topics
    .slice()
    .sort((a, b) => b.rating - a.rating)
    .slice(0, 8)
    .map((t) => ({
      topic: truncate(t.topic),
      score: Math.round(((t.rating - MIN_ELO) / (MAX_ELO - MIN_ELO)) * 100),
      rawElo: Math.round(t.rating),
    }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <PolarGrid stroke="#334155" />
        <PolarAngleAxis
          dataKey="topic"
          tick={{ fill: "#94a3b8", fontSize: 10 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "8px",
            color: "#f1f5f9",
            fontSize: "12px",
          }}
          formatter={(_value, _name, props) => [
            `ELO ${props.payload.rawElo}`,
            props.payload.topic,
          ]}
        />
        <Radar
          dataKey="score"
          stroke="#8b5cf6"
          fill="#8b5cf6"
          fillOpacity={0.25}
          dot={{ r: 3, fill: "#8b5cf6" }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
