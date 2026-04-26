"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { FUND_USAGE, formatFCFA } from "@/data/mockData";

export function FundUsagePie() {
  return (
    <div className="grid sm:grid-cols-2 gap-6 items-center">
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={FUND_USAGE}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={95}
              paddingAngle={2}
              stroke="#0D1B0F"
              strokeWidth={3}
            >
              {FUND_USAGE.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#0D1B0F",
                border: "1px solid rgba(249,168,37,0.3)",
                borderRadius: 12,
                fontSize: 12,
              }}
              formatter={(v: number) => `${formatFCFA(v)} FCFA`}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="space-y-3">
        {FUND_USAGE.map((entry) => (
          <li key={entry.name} className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
            <div className="flex items-center gap-3 mb-1.5">
              <span
                className="w-3 h-3 rounded-sm flex-shrink-0"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm text-neutral-light/85 font-medium">
                {entry.name}
              </span>
            </div>
            <div className="flex items-baseline justify-between font-mono">
              <span className="text-accent font-bold text-lg">{entry.percent}%</span>
              <span className="text-sm text-neutral-light/60">
                {formatFCFA(entry.value)} FCFA
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
