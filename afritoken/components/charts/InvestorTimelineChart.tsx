"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function InvestorTimelineChart({
  data,
}: {
  data: { month: string; received: number | null; projected: number }[];
}) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" tick={{ fontSize: 10 }} interval={2} />
          <YAxis
            tick={{ fontSize: 10 }}
            tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0D1B0F",
              border: "1px solid rgba(249,168,37,0.3)",
              borderRadius: 12,
              fontSize: 12,
            }}
            formatter={(v: number) => `${v.toLocaleString("fr-FR")} FCFA`}
            labelStyle={{ color: "#F9A825" }}
          />
          <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
          <ReferenceLine
            x={data[data.length - 1]?.month}
            stroke="#F9A825"
            strokeDasharray="2 4"
            label={{ value: "Capital remboursé", fill: "#F9A825", fontSize: 10, position: "insideTopRight" }}
          />
          <Line
            type="monotone"
            dataKey="received"
            stroke="#2E7D32"
            strokeWidth={2.5}
            name="Dividendes reçus"
            dot={{ r: 3, fill: "#2E7D32" }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="projected"
            stroke="#F9A825"
            strokeWidth={2}
            strokeDasharray="6 4"
            name="Projection 36 mois"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
