"use client"

import { useApp } from "@/context/app-context"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function SummaryPanel() {
  const { analysis, t } = useApp()
  if (!analysis) return <p className="text-sm text-muted-foreground">{t.noDocYet}</p>
  const { doc } = analysis

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">{doc.title}</CardTitle>
        <CardDescription>{t.summary}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <p className="leading-relaxed">{doc.summary}</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 className="font-medium">{t.parties}</h4>
            <div className="flex flex-wrap gap-2 mt-2">
              {doc.parties.map((p, i) => (
                <Badge key={i} variant="secondary">
                  {p.name}
                </Badge>
              ))}
            </div>
          </div>
          <div>
            <h4 className="font-medium">{t.effectiveDate}</h4>
            <p className="text-sm text-muted-foreground mt-2">{doc.effectiveDate || "-"}</p>
          </div>
          <div>
            <h4 className="font-medium">{t.terminationDate}</h4>
            <p className="text-sm text-muted-foreground mt-2">{doc.terminationDate || "-"}</p>
          </div>
        </div>

        {doc.obligations?.length ? (
          <div>
            <h4 className="font-medium">{t.obligations}</h4>
            <ul className="list-disc ms-5 mt-2 space-y-1">
              {doc.obligations.map((o, i) => (
                <li key={i} className="leading-6">
                  {o}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
