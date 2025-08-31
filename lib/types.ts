export type LanguageCode = "en" | "hi" | "mr"

export type Party = {
  name: string
  role: "Lessor" | "Lessee" | "Employer" | "Employee" | "PartyA" | "PartyB" | "Vendor" | "Customer" | "Other"
}

export type Clause = {
  id: string
  title: string
  originalText: string
  simplifiedText: string
  category?: "Financial" | "Legal" | "Compliance" | "Termination" | "General"
  riskLevel?: "Low" | "Medium" | "High"
}

export type ParsedDocument = {
  id: string
  title: string
  language: LanguageCode
  parties: Party[]
  effectiveDate?: string
  terminationDate?: string
  obligations: string[]
  clauses: Clause[]
  summary: string
  notes?: string[]
}

export type RiskOverview = {
  byCategory: {
    category: "Financial" | "Legal" | "Compliance" | "Termination"
    score: number // 0-100
  }[]
  recommendations: string[]
}

export type AnalysisResult = {
  doc: ParsedDocument
  risks: RiskOverview
}

export type QAItem = {
  q: string
  a: string
  tags?: string[]
}

export type Translations = {
  appName: string
  language: string
  selectLanguage: string
  uploadOrSelect: string
  uploadHint: string
  or: string
  chooseSample: string
  processDocument: string
  processing: string
  analysis: string
  summary: string
  clauses: string
  risks: string
  chatQA: string
  askQuestion: string
  send: string
  exportPDF: string
  parties: string
  effectiveDate: string
  terminationDate: string
  obligations: string
  clauseTitle: string
  original: string
  simplified: string
  riskDashboardTitle: string
  recommendations: string
  financial: string
  legal: string
  compliance: string
  termination: string
  low: string
  medium: string
  high: string
  riskLegend: string
  sampleDocs: string
  rentalAgreement: string
  employmentContract: string
  servicesAgreement: string
  switchTo: string
  tooltipRisk: string
  noDocYet: string
  exampleQuestions: string
  uploadTypes: string
  simulatedOCR: string
}
