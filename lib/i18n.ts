import en from "@/data/translations/en.json"
import hi from "@/data/translations/hi.json"
import mr from "@/data/translations/mr.json"
import type { LanguageCode, Translations } from "./types"

const dict: Record<LanguageCode, Translations> = { en, hi, mr }

export function getDictionary(lang: LanguageCode): Translations {
  return dict[lang]
}
