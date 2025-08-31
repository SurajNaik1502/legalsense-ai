"use client"

import { Button } from "@/components/ui/button"
import { useState } from "react"
import jsPDF from "jspdf"
import html2canvas from "html2canvas"
import { useApp } from "@/context/app-context"

export function ExportButton() {
  const [busy, setBusy] = useState(false)
  const { t, analysis } = useApp()
  async function exportPDF() {
    const el = document.getElementById("report-root")
    if (!el) return
    setBusy(true)
    try {
      const canvas = await html2canvas(el, { scale: 2, useCORS: true })
      const img = canvas.toDataURL("image/png")
      const pdf = new jsPDF("p", "mm", "a4")
      const pageWidth = pdf.internal.pageSize.getWidth()
      const imgHeight = (canvas.height * pageWidth) / canvas.width
      pdf.addImage(img, "PNG", 0, 0, pageWidth, imgHeight)
      pdf.save(`${analysis?.doc.title || "report"}.pdf`)
    } catch (e) {
      console.error("[v0] PDF export error", e)
      alert("PDF export failed.")
    } finally {
      setBusy(false)
    }
  }
  return (
    <Button onClick={exportPDF} disabled={busy}>
      {busy ? "…" : t.exportPDF}
    </Button>
  )
}
