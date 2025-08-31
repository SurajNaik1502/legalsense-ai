import type { QAItem } from "@/lib/types"

export const qa: Record<"en" | "hi" | "mr", QAItem[]> = {
  en: [
    {
      q: "What is the notice period?",
      a: "Typically 30 days unless otherwise stated in the Termination clause.",
      tags: ["termination"],
    },
    {
      q: "Are there any penalties?",
      a: "Yes, late payment penalties may apply. See Payment Terms.",
      tags: ["financial"],
    },
    {
      q: "Who bears liability?",
      a: "Liability may be allocated to the tenant or vendor depending on clauses.",
      tags: ["legal"],
    },
    { q: "Is there arbitration?", a: "Yes, disputes may be resolved by binding arbitration.", tags: ["legal"] },
  ],
  hi: [
    { q: "नोटिस अवधि क्या है?", a: "आम तौर पर 30 दिन, जब तक समाप्ति धारा में अलग न हो।", tags: ["termination"] },
    { q: "क्या कोई जुर्माना है?", a: "हाँ, देर से भुगतान पर जुर्माना लागू हो सकता है।", tags: ["financial"] },
    { q: "दायित्व कौन उठाएगा?", a: "दायित्व संबंधित धाराओं के अनुसार पक्षों में बाँटा जा सकता है।", tags: ["legal"] },
    {
      q: "क्या मध्यस्थता है?",
      a: "हाँ, कई मामलों में विवाद का समाधान बाध्यकारी मध्यस्थता द्वारा किया जा सकता है।",
      tags: ["legal"],
    },
  ],
  mr: [
    { q: "नोटीस कालावधी किती आहे?", a: "साधारणत: ३० दिवस, जोपर्यंत समाप्ती कलमात वेगळे नमूद नाही.", tags: ["termination"] },
    { q: "काही दंड आहेत का?", a: "होय, उशीरा देयकांसाठी दंड लागू शकतो. पेमेंट टर्म्स पहा.", tags: ["financial"] },
    { q: "दायित्व कोण उचलेल?", a: "दायित्व संबंधित कलमानुसार पक्षांमध्ये वाटले जाऊ शकते.", tags: ["legal"] },
    { q: "मध्यस्थी आहे का?", a: "होय, वादांचे निराकरण बाध्यकारी मध्यस्थीने केले जाऊ शकते.", tags: ["legal"] },
  ],
}
