/**
 * Design Document Template for my-yc Startups
 *
 * This template defines the structure that Jason AI will use to create
 * standardized startup design documents. Each field is easily editable
 * and serves as input for the Modal agents.
 */

export interface StartupDesignDoc {
  // Basic Information
  title: string
  executive_summary: string

  // Problem & Solution
  problem_statement: string
  target_market: string
  user_persona: string
  value_proposition: string

  // Product Details
  mvp_features: string[]
  technical_requirements: string
  tech_stack: string[]

  // Business Model
  success_metrics: string[]
  monetization_strategy?: string

  // Implementation
  immediate_next_steps: string[]
  development_timeline?: string

  // Metadata
  category?: string
  complexity_level?: 'simple' | 'moderate' | 'complex'
  estimated_dev_time?: string
}

export const DESIGN_DOC_TEMPLATE: Partial<StartupDesignDoc> = {
  title: "My Startup",
  executive_summary: "Brief 2-3 sentence overview of what this startup does and its core value proposition.",
  problem_statement: "Clear definition of the specific problem being solved.",
  target_market: "Description of the target market size and characteristics.",
  user_persona: "Detailed description of the ideal user/customer.",
  value_proposition: "What unique value this product provides to users.",
  mvp_features: [
    "Essential feature 1",
    "Essential feature 2",
    "Essential feature 3"
  ],
  technical_requirements: "High-level technical approach and architecture.",
  tech_stack: [
    "Frontend: Next.js + TypeScript",
    "Backend: Node.js/Python",
    "Database: PostgreSQL/MongoDB",
    "Deployment: Vercel/Railway"
  ],
  success_metrics: [
    "User acquisition rate",
    "User engagement metrics",
    "Revenue/conversion metrics"
  ],
  immediate_next_steps: [
    "Set up project repository",
    "Create basic UI/UX wireframes",
    "Implement core features",
    "Deploy MVP version"
  ],
  category: "web-app",
  complexity_level: "moderate",
  estimated_dev_time: "2-4 weeks"
}

/**
 * Validation function to check if a design doc is complete
 */
export function validateDesignDoc(doc: Partial<StartupDesignDoc>): {
  isValid: boolean
  missingFields: string[]
} {
  const requiredFields: (keyof StartupDesignDoc)[] = [
    'title',
    'executive_summary',
    'problem_statement',
    'target_market',
    'user_persona',
    'value_proposition',
    'mvp_features',
    'technical_requirements',
    'success_metrics',
    'immediate_next_steps'
  ]

  const missingFields = requiredFields.filter(field =>
    !doc[field] ||
    (Array.isArray(doc[field]) && (doc[field] as any[]).length === 0)
  )

  return {
    isValid: missingFields.length === 0,
    missingFields
  }
}

/**
 * Convert design doc to markdown format for README
 */
export function designDocToMarkdown(doc: StartupDesignDoc): string {
  return `# ${doc.title}

> ${doc.executive_summary}

## 🎯 Problem Statement

${doc.problem_statement}

## 👥 Target Market & User Persona

**Target Market:** ${doc.target_market}

**User Persona:** ${doc.user_persona}

## 💡 Value Proposition

${doc.value_proposition}

## 🚀 MVP Features

${doc.mvp_features.map(feature => `- ${feature}`).join('\n')}

## 🛠️ Technical Requirements

${doc.technical_requirements}

### Tech Stack
${doc.tech_stack.map(tech => `- ${tech}`).join('\n')}

## 📊 Success Metrics

${doc.success_metrics.map(metric => `- ${metric}`).join('\n')}

${doc.monetization_strategy ? `## 💰 Monetization Strategy\n\n${doc.monetization_strategy}\n\n` : ''}

## 🎯 Immediate Next Steps

${doc.immediate_next_steps.map(step => `- [ ] ${step}`).join('\n')}

${doc.development_timeline ? `## ⏱️ Development Timeline\n\n${doc.development_timeline}\n\n` : ''}

---

*🤖 This startup was designed by AI agents via [my-yc](https://my-yc.com) platform*
`
}