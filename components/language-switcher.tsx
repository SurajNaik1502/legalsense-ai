"use client"

import { useApp } from "@/context/app-context"
import type { LanguageCode } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export function LanguageSwitcher() {
  const { language, setLanguage, t } = useApp()
  const langs: { code: LanguageCode; label: string }[] = [
    { code: "en", label: "English" },
    { code: "hi", label: "हिंदी" },
    { code: "mr", label: "मराठी" },
  ]
  const current = langs.find((l) => l.code === language)?.label

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" aria-label={`${t.selectLanguage}: ${current}`}>
          {t.language}: {current}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {langs.map((l) => (
          <DropdownMenuItem key={l.code} onSelect={() => setLanguage(l.code)} aria-label={`${t.switchTo} ${l.label}`}>
            {l.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
