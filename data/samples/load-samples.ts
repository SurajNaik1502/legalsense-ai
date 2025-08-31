import enRental from "./en/rental-agreement.json"
import enEmployment from "./en/employment-contract.json"
import enServices from "./en/services-agreement.json"
import hiRental from "./hi/rental-agreement.json"
import hiEmployment from "./hi/employment-contract.json"
import hiServices from "./hi/services-agreement.json"
import mrRental from "./mr/rental-agreement.json"
import mrEmployment from "./mr/employment-contract.json"
import mrServices from "./mr/services-agreement.json"
import type { ParsedDocument } from "@/lib/types"

const all: Record<string, ParsedDocument> = {
  "sample-en-rental": enRental as any,
  "sample-en-employment": enEmployment as any,
  "sample-en-services": enServices as any,
  "sample-hi-rental": hiRental as any,
  "sample-hi-employment": hiEmployment as any,
  "sample-hi-services": hiServices as any,
  "sample-mr-rental": mrRental as any,
  "sample-mr-employment": mrEmployment as any,
  "sample-mr-services": mrServices as any,
}

export async function loadSampleById(id: string): Promise<ParsedDocument> {
  if (!all[id]) throw new Error("Sample not found")
  return all[id]
}

export function listSamples() {
  return Object.values(all)
}
