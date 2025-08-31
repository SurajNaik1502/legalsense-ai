"use client"

import type React from "react"
import { useState } from "react"
import { useApp } from "@/context/app-context"
import { qa } from "@/data/qa/common-qa"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

type Msg = { role: "user" | "assistant"; content: string }

export function ChatPanel() {
  const { t, language, analysis } = useApp()
  const [messages, setMessages] = useState<Msg[]>([])
  const examples = qa[language]

  function answer(q: string) {
    const found = examples.find(
      (item) => normalize(item.q).includes(normalize(q)) || normalize(q).includes(normalize(item.q)),
    )
    if (found) return found.a
    if (analysis) {
      const clause = analysis.doc.clauses.find((c) => normalize(serializeClause(c)).includes(normalize(q)))
      if (clause) {
        return `${clause.simplifiedText}\n\n${t.original}: ${clause.originalText}`
      }
      return analysis.doc.summary
    }
    return "No context available."
  }

  function onSend(e: React.FormEvent) {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const input = form.elements.namedItem("q") as HTMLInputElement
    const q = input.value.trim()
    if (!q) return
    const a = answer(q)
    setMessages((prev) => [...prev, { role: "user", content: q }, { role: "assistant", content: a }])
    input.value = ""
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.chatQA}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={onSend} className="flex gap-2">
          <Input name="q" placeholder={t.askQuestion} aria-label={t.askQuestion} />
          <Button type="submit">{t.send}</Button>
        </form>
        <div className="space-y-2">
          <div className="text-xs text-muted-foreground">{t.exampleQuestions}:</div>
          <div className="flex flex-wrap gap-2">
            {examples.slice(0, 3).map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() =>
                  setMessages((prev) => [
                    ...prev,
                    { role: "user", content: ex.q },
                    { role: "assistant", content: ex.a },
                  ])
                }
                className="text-left text-sm border rounded px-2 py-1 hover:bg-accent"
                aria-label={ex.q}
              >
                {ex.q}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-3">
          {messages.map((m, i) => (
            <div key={i} className={`rounded p-3 ${m.role === "user" ? "bg-blue-50" : "bg-muted"}`}>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant={m.role === "user" ? "default" : "secondary"}>{m.role}</Badge>
              </div>
              <p className="leading-relaxed whitespace-pre-wrap">{m.content}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function normalize(s: string) {
  return s.toLowerCase().replace(/\s+/g, " ").trim()
}

function serializeClause(c: { title?: string; originalText: string; simplifiedText: string }) {
  return `${c.title ?? ""} ${c.originalText} ${c.simplifiedText}`
}
