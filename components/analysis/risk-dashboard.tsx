"use client"

import { useApp } from "@/context/app-context"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import type { RiskCategory } from "@/lib/types"

const COLORS = {
  // Color system: 5 total — primary blue, neutrals via tokens, green, red
  primary: "#2563eb", // blue-600
  green: "#16a34a", // green-600 (available for future accents)
  red: "#dc2626", // red-600 (used by destructive badge)
}

export function RiskDashboard() {
  const { analysis, t } = useApp()
  
  if (!analysis) {
    console.log("No analysis data available")
    return <p className="text-sm text-muted-foreground">{t.noDocYet}</p>
  }
  
  if (!analysis.risks?.by_category || !Array.isArray(analysis.risks.by_category) || analysis.risks.by_category.length === 0) {
    console.log("No risk category data available")
    return <p className="text-sm text-muted-foreground">No risk data available</p>
  }
  
  const data = analysis.risks.by_category.map((it: RiskCategory) => ({ name: it.category, score: it.score }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.riskDashboardTitle}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">{t.riskLegend}</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} barCategoryGap={24}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip formatter={(v: any) => [`${v}`, t.tooltipRisk]} />
              <Bar dataKey="score" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4 className="font-medium">{t.recommendations}</h4>
          <ul className="list-disc ms-5 mt-2 space-y-1">
            {analysis.risks?.recommendations?.map((r, i) => (
              <li key={i} className="leading-6">
                {r}
              </li>
            )) || <li>No recommendations available</li>}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}
