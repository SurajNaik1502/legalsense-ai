"use client"

import { useApp } from "@/context/app-context"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function ClausesPanel() {
  const { analysis, t } = useApp()
  if (!analysis) return <p className="text-sm text-muted-foreground">{t.noDocYet}</p>
  const { doc } = analysis

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.clauses}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {doc.clauses.map((c) => (
          <div key={c.id} className="border rounded-md p-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">
                {t.clauseTitle} {c.title ? `: ${c.title}` : c.id}
              </h4>
              <div className="flex gap-2">
                {c.category ? <Badge variant="secondary">{c.category}</Badge> : null}
                {c.riskLevel ? (
                  <Badge
                    variant={c.riskLevel === "High" ? "destructive" : c.riskLevel === "Medium" ? "default" : "outline"}
                  >
                    {c.riskLevel === "High" ? t.high : c.riskLevel === "Medium" ? t.medium : t.low}
                  </Badge>
                ) : null}
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-3 mt-3">
              <div>
                <div className="text-xs font-medium uppercase text-muted-foreground">{t.original}</div>
                <p className="leading-relaxed mt-1">{c.originalText}</p>
              </div>
              <div>
                <div className="text-xs font-medium uppercase text-muted-foreground">{t.simplified}</div>
                <p className="leading-relaxed mt-1">{c.simplifiedText}</p>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
