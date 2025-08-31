"use client"

import type React from "react"
import { createContext, useContext, useMemo, useState } from "react"
import type { AnalysisResult, LanguageCode, ParsedDocument } from "@/lib/types"
import { getDictionary } from "@/lib/i18n"

type AppState = {
  language: LanguageCode
  setLanguage: (l: LanguageCode) => void
  t: ReturnType<typeof getDictionary>
  doc?: ParsedDocument
  setDoc: (d?: ParsedDocument) => void
  analysis?: AnalysisResult
  setAnalysis: (a?: AnalysisResult) => void
}

const AppContext = createContext<AppState | null>(null)

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<LanguageCode>("en")
  const [doc, setDoc] = useState<ParsedDocument | undefined>(undefined)
  const [analysis, setAnalysis] = useState<AnalysisResult | undefined>(undefined)
  const t = useMemo(() => getDictionary(language), [language])
  const value: AppState = { language, setLanguage, t, doc, setDoc, analysis, setAnalysis }
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error("useApp must be used within AppProvider")
  return ctx
}
