"use client"

import { useState } from "react"
import { useApp } from "@/context/app-context"
import { analyzeDocument } from "@/lib/analysis"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { listSamples } from "@/data/samples/load-samples"
import type { LanguageCode } from "@/lib/types"

const samples = listSamples()

export function UploadPanel() {
  const { t, setAnalysis, setDoc, language } = useApp()
  const [file, setFile] = useState<File | undefined>(undefined)
  const [sampleId, setSampleId] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)

  async function handleProcess() {
    try {
      setLoading(true)
      const result = await analyzeDocument({ file, sampleId, langHint: language as LanguageCode })
      setDoc(result.doc)
      setAnalysis(result)
    } catch (e) {
      console.error("[v0] analyze error", e)
      alert("Failed to process document.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">{t.uploadOrSelect}</CardTitle>
        <CardDescription className="text-pretty">
          {t.uploadHint} • {t.uploadTypes} • {t.simulatedOCR}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <label className="text-sm font-medium" htmlFor="file">
          {t.uploadOrSelect}
        </label>
        <Input
          id="file"
          type="file"
          accept=".pdf,.docx,.txt,image/*"
          onChange={(e) => setFile(e.target.files?.[0])}
          aria-describedby="file-desc"
        />
        <div id="file-desc" className="text-xs text-muted-foreground">
          {t.uploadHint}
        </div>

        <div className="text-center text-sm text-muted-foreground">{t.or}</div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">{t.chooseSample}</label>
          <Select onValueChange={setSampleId} value={sampleId}>
            <SelectTrigger>
              <SelectValue placeholder={t.sampleDocs} />
            </SelectTrigger>
            <SelectContent>
              {samples.map((s) => (
                <SelectItem key={s.id} value={s.id}>
                  {s.title} ({s.language.toUpperCase()})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleProcess} disabled={loading || (!file && !sampleId)}>
            {loading ? t.processing : t.processDocument}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
