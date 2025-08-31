import type { AnalysisResult, Clause, LanguageCode, ParsedDocument, RiskOverview } from "./types"
import { detectLanguageBySample } from "./lang-detect"
import { loadSampleById } from "@/data/samples/load-samples"

const HIGH_RISK_TERMS = [
  "penalty",
  "indemnify",
  "terminate immediately",
  "liability",
  "non-compete",
  "arbitration",
  "late fee",
]
const MEDIUM_RISK_TERMS = ["auto-renew", "exclusive", "confidentiality", "governing law", "jurisdiction"]
const DATE_REGEX = /\b(20\d{2}|19\d{2})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b/

export async function simulateOCR(file: File): Promise<string> {
  const isImage = file.type.startsWith("image/")
  if (!isImage) return ""
  return "Scanned legal agreement image. Parties: Party A and Party B. Effective Date: 2025-01-01. Contains indemnify and arbitration clauses."
}

export async function parseUploaded(file: File, langHint?: LanguageCode): Promise<ParsedDocument> {
  const text = await readFileText(file)
  const ocrText = await simulateOCR(file)
  const content = (text || "") + (ocrText ? "\n" + ocrText : "")
  const language = langHint || detectLanguageBySample(content) || "en"
  return basicExtract(content || "Sample Agreement", language, file.name)
}

export async function parseSample(sampleId: string): Promise<ParsedDocument> {
  const sample = await loadSampleById(sampleId)
  return sample
}

function tokenize(text: string) {
  return text.toLowerCase()
}

function scoreRiskForClause(text: string): "Low" | "Medium" | "High" {
  const t = tokenize(text)
  if (HIGH_RISK_TERMS.some((term) => t.includes(term))) return "High"
  if (MEDIUM_RISK_TERMS.some((term) => t.includes(term))) return "Medium"
  return "Low"
}

function basicExtract(raw: string, language: LanguageCode, title: string): ParsedDocument {
  const parties: { name: string; role: any }[] = []
  if (raw.toLowerCase().includes("lessor") || raw.toLowerCase().includes("lessee")) {
    parties.push({ name: "Lessor", role: "Lessor" }, { name: "Lessee", role: "Lessee" })
  } else {
    parties.push({ name: "Party A", role: "PartyA" }, { name: "Party B", role: "PartyB" })
  }

  const mDate = raw.match(DATE_REGEX)
  const effectiveDate = mDate ? mDate[0] : undefined
  const obligations = extractObligations(raw)
  const clauseCandidates = splitClauses(raw)
  const clauses: Clause[] = clauseCandidates.map((c, i) => ({
    id: `c-${i + 1}`,
    title: `Clause ${i + 1}`,
    originalText: c,
    simplifiedText: simplifyText(c),
    category: categorizeClause(c),
    riskLevel: scoreRiskForClause(c),
  }))

  const summary = summarize(raw)
  return {
    id: `doc-${Date.now()}`,
    title: title.replace(/\.[a-zA-Z0-9]+$/, "") || "Document",
    language,
    parties,
    effectiveDate,
    obligations,
    clauses,
    summary,
    notes: findNotes(raw),
  }
}

function extractObligations(text: string): string[] {
  const lines = text.split(/\n|\. /).filter(Boolean)
  return lines.filter((l) => /(shall|must|agree|responsible|warrant)/i.test(l)).slice(0, 6)
}

function splitClauses(text: string): string[] {
  const parts = text
    .split(/\n{2,}|(?:^|\n)\d+\.\s+/)
    .map((s) => s.trim())
    .filter(Boolean)
  return parts.slice(0, 8)
}

function categorizeClause(text: string): "Financial" | "Legal" | "Compliance" | "Termination" | "General" {
  const t = text.toLowerCase()
  if (t.includes("payment") || t.includes("fee") || t.includes("rent") || t.includes("penalty")) return "Financial"
  if (t.includes("terminate") || t.includes("termination")) return "Termination"
  if (t.includes("law") || t.includes("jurisdiction") || t.includes("liability") || t.includes("arbitration"))
    return "Legal"
  if (t.includes("compliance") || t.includes("regulation") || t.includes("confidential")) return "Compliance"
  return "General"
}

function simplifyText(text: string): string {
  return (
    text
      .replace(/\bhereinafter\b/gi, "from now on")
      .replace(/\bindemnify\b/gi, "cover costs for")
      .replace(/\bnotwithstanding\b/gi, "despite")
      .replace(/\bforce majeure\b/gi, "events beyond control")
      .slice(0, 260) + (text.length > 260 ? "…" : "")
  )
}

function summarize(text: string): string {
  const s = text.split(/\n/).slice(0, 6).join(" ")
  return s.length > 360 ? s.slice(0, 360) + "…" : s
}

function findNotes(text: string): string[] {
  const notes: string[] = []
  if (/auto-?renew/i.test(text)) notes.push("Auto-renew detected. Consider calendar reminders.")
  if (/indemnif/i.test(text)) notes.push("Indemnity present. Understand financial exposure.")
  if (/late fee/i.test(text)) notes.push("Late fee present. Review payment schedules.")
  return notes
}

export function computeRisk(doc: ParsedDocument): RiskOverview {
  const buckets: Record<"Financial" | "Legal" | "Compliance" | "Termination", number[]> = {
    Financial: [],
    Legal: [],
    Compliance: [],
    Termination: [],
  }
  doc.clauses.forEach((c) => {
    const val = c.riskLevel === "High" ? 85 : c.riskLevel === "Medium" ? 55 : 20
    const k = (c.category || "General") as keyof typeof buckets
    if (buckets[k]) buckets[k].push(val)
  })
  const avg = (arr: number[]) => (arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 10)
  const byCategory = (Object.keys(buckets) as (keyof typeof buckets)[]).map((cat) => ({
    category: cat as any,
    score: avg(buckets[cat]),
  }))
  const recommendations = generateRecommendations(doc)
  return { byCategory, recommendations }
}

function generateRecommendations(doc: ParsedDocument): string[] {
  const recs: string[] = []
  if (doc.clauses.some((c) => /arbitration/i.test(c.originalText)))
    recs.push("Arbitration clause: confirm seat and rules.")
  if (doc.clauses.some((c) => /termination/i.test(c.originalText)))
    recs.push("Termination: clarify notice periods and grounds.")
  if (doc.clauses.some((c) => /penalty|late fee/i.test(c.originalText)))
    recs.push("Financial penalties: negotiate caps or grace periods.")
  if (!doc.effectiveDate) recs.push("Missing effective date: ensure dates are explicit.")
  return recs.length ? recs : ["No major risks detected."]
}

async function readFileText(file: File): Promise<string> {
  if (file.type === "application/pdf") {
    const arrayBuffer = await file.arrayBuffer()
    const asText = new TextDecoder().decode(arrayBuffer).replace(/\0/g, "")
    return (
      asText ||
      "PDF document with clauses about payment, termination, confidentiality, and governing law. Effective Date: 2025-06-01."
    )
  } else if (file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
    return "DOCX agreement content. Parties: Lessor and Lessee. Rent and late fee terms; termination on breach; jurisdiction in Mumbai."
  } else if (file.type.startsWith("image/")) {
    return ""
  } else {
    return await file.text()
  }
}

export async function analyzeDocument(input: {
  file?: File
  sampleId?: string
  langHint?: LanguageCode
}): Promise<AnalysisResult> {
  let doc: ParsedDocument
  if (input.sampleId) {
    doc = await parseSample(input.sampleId)
  } else if (input.file) {
    doc = await parseUploaded(input.file, input.langHint)
  } else {
    throw new Error("No document input provided")
  }
  const risks = computeRisk(doc)
  return { doc, risks }
}
