import type { LanguageCode } from "./types"

export function detectLanguageBySample(text: string): LanguageCode | undefined {
  const t = text || ""
  const hasDevanagari = /[\u0900-\u097F]/.test(t)
  if (!hasDevanagari) return "en"
  if (/है|और|के|जबकि|से|लिए/.test(t)) return "hi"
  if (/आहे|आणि|च्या|पासून|साठी/.test(t)) return "mr"
  return "hi"
}
