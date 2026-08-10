import type { LucideIcon } from 'lucide-react'
import { Apple, HeartPulse, Pill, ShieldAlert, Syringe, Waves } from 'lucide-react'

export interface Suggestion {
  icon: LucideIcon
  label: string
  question: string
}

export const suggestions: Suggestion[] = [
  {
    icon: Pill,
    label: 'Medicine use',
    question: 'Why is Warfarin prescribed?',
  },
  {
    icon: ShieldAlert,
    label: 'Side effects',
    question: 'What are the side effects of Ibuprofen?',
  },
  {
    icon: Apple,
    label: 'Food & diet',
    question: 'What foods should I avoid while taking Warfarin?',
  },
  {
    icon: Waves,
    label: 'Interactions',
    question: 'Can Warfarin interact with other medicines?',
  },
  {
    icon: Syringe,
    label: 'Dosage',
    question: 'What is the dosage information for Warfarin?',
  },
  {
    icon: HeartPulse,
    label: 'General',
    question: 'What should I know before taking Metformin?',
  },
]
