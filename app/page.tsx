"use client"

import { AppProvider, useApp } from "@/context/app-context"
import { LanguageSwitcher } from "@/components/language-switcher"
import { UploadPanel } from "@/components/upload-panel"
import { SummaryPanel } from "@/components/analysis/summary"
import { ClausesPanel } from "@/components/analysis/clauses"
import { RiskDashboard } from "@/components/analysis/risk-dashboard"
import { ChatPanel } from "@/components/chat/chat-panel"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ExportButton } from "@/components/export-button"

function AppShell() {
  const { t } = useApp()

  return (
    <main className="min-h-dvh bg-background text-foreground">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-balance" aria-label={t.appName}>
            LegalSense AI
          </h1>
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            <ExportButton />
          </div>
        </div>
      </header>

      <section className="container mx-auto px-4 py-6 grid gap-6">
        <UploadPanel />

        <div id="report-root" className="grid gap-6">
          <Tabs defaultValue="summary" className="w-full">
            <TabsList>
              <TabsTrigger value="summary">{t.summary}</TabsTrigger>
              <TabsTrigger value="clauses">{t.clauses}</TabsTrigger>
              <TabsTrigger value="risks">{t.risks}</TabsTrigger>
              <TabsTrigger value="qa">{t.chatQA}</TabsTrigger>
            </TabsList>
            <TabsContent value="summary" className="mt-4">
              <SummaryPanel />
            </TabsContent>
            <TabsContent value="clauses" className="mt-4">
              <ClausesPanel />
            </TabsContent>
            <TabsContent value="risks" className="mt-4">
              <RiskDashboard />
            </TabsContent>
            <TabsContent value="qa" className="mt-4">
              <ChatPanel />
            </TabsContent>
          </Tabs>
        </div>
      </section>

      <footer className="border-t">
        <div className="container mx-auto px-4 py-4 text-sm text-muted-foreground">
          © {new Date().getFullYear()} LegalSense AI
        </div>
      </footer>
    </main>
  )
}

export default function Page() {
  return (
    <AppProvider>
      <AppShell />
    </AppProvider>
  )
}
