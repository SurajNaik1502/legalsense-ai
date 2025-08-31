"use client"

import { useState } from "react"
import { useApp } from "@/context/app-context"
import { apiService } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { listSamples } from "@/data/samples/load-samples"
import { useToast } from "@/hooks/use-toast"
import type { LanguageCode, AnalysisResult } from "@/lib/types"

const samples = listSamples()

export function UploadPanel() {
  const { t, setAnalysis, setDoc, language } = useApp()
  const { toast } = useToast()
  const [file, setFile] = useState<File | undefined>(undefined)
  const [sampleId, setSampleId] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [currentDocumentId, setCurrentDocumentId] = useState<string | undefined>(undefined)

  async function handleProcess() {
    if (!file && !sampleId) {
      toast({
        title: "Error",
        description: "Please select a file or choose a sample document.",
        variant: "destructive",
      })
      return
    }

    try {
      setLoading(true)
      
      if (file) {
        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024 // 10MB in bytes
        if (file.size > maxSize) {
          throw new Error("File size exceeds 10MB limit")
        }

        // Upload and process real document
        const uploadResponse = await apiService.uploadDocument(file, language)
        if (!uploadResponse.success) {
          throw new Error(uploadResponse.message || "Failed to upload document")
        }
        
        setCurrentDocumentId(uploadResponse.document_id)
        
        // Check document info and status
        const docInfo = await apiService.getDocumentInfo(uploadResponse.document_id)
        if (!docInfo.success || docInfo.document_info.processing_status === 'failed') {
          throw new Error("Document processing failed")
        }
        
        // Analyze the uploaded document
        const analysisResponse = await apiService.analyzeDocument(uploadResponse.document_id, language)
        if (!analysisResponse.success || !analysisResponse.analysis) {
          throw new Error(analysisResponse.message || "Analysis failed")
        }
        
        setDoc(analysisResponse.analysis.doc)
        setAnalysis(analysisResponse.analysis)
        
        toast({
          title: "Success",
          description: "Document processed successfully!",
          duration: 3000,
        })
      } else if (sampleId) {
        // Use sample data for demonstration
        const sample = samples.find(s => s.id === sampleId)
        if (!sample) {
          throw new Error("Sample document not found")
        }

        setDoc(sample)
        // Create a mock analysis result for samples
        const mockAnalysis: AnalysisResult = {
          doc: sample,
          risks: {
            byCategory: [
              { category: "Financial", score: 25 },
              { category: "Legal", score: 30 },
              { category: "Compliance", score: 20 },
              { category: "Termination", score: 15 }
            ],
            recommendations: [
              "Standard terms detected",
              "Consider legal review for compliance",
              "Monitor termination clauses"
            ]
          }
        }
        setAnalysis(mockAnalysis)
        
        toast({
          title: "Sample Loaded",
          description: "Sample document loaded for demonstration.",
          duration: 3000,
        })
      }
    } catch (e) {
      console.error("[v0] analyze error", e)
      toast({
        title: "Error",
        description: e instanceof Error ? e.message : "Failed to process document.",
        variant: "destructive",
      })
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
