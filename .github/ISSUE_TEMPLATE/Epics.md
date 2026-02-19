---
name: Mortgage LO Knowledge Delivery – Epic
about: High-level initiative spanning multiple features for the Mortgage LO Knowledge Delivery system (education + operational guidance only)
title: "[Epic][Mortgage-LO-Knowledge-Delivery] <Initiative Name>"
labels:
  - mortgage-lo-knowledge-delivery
  - epic
  - ai-platform
assignees: []
body:

  - type: markdown
    attributes:
      value: |
        ## Epic Overview
        This Epic represents a major initiative within the Mortgage LO Knowledge Delivery system.

        **Scope boundary (non-negotiable):**
        - This effort is **education + operational guidance only**
        - It uses **internal simulation/training recordings** (no real borrower conversations)
        - It must **not** enable loan origination activities (rates, eligibility, applications, underwriting)

  - type: textarea
    id: objective
    attributes:
      label: Business Objective
      description: What measurable business outcome does this Epic enable?
    validations:
      required: true

  - type: textarea
    id: success_metrics
    attributes:
      label: Success Metrics
      description: Define quantifiable outcomes (efficiency, adoption, quality, etc.)
      placeholder: |
        - Reduce repetitive LO explanations by X%
        - Borrower self-serve completion rate of FAQs by X%
        - Content accuracy score (review pass rate) of X%
    validations:
      required: true

  - type: textarea
    id: scope
    attributes:
      label: Scope
      description: Clearly define what is included and excluded.
      placeholder: |
        In scope:
        - Education content generation from simulations
        - Canonical content library + approvals
        - RAG-based response generation
        - TTS delivery

        Out of scope:
        - Rates/APR/payment quotes or calculators
        - Eligibility, pre-qualification, underwriting logic
        - Application intake or collection of borrower financial data
    validations:
      required: true

  - type: textarea
    id: scope_boundary_enforcement
    attributes:
      label: Scope Boundary Enforcement
      description: How will this Epic technically enforce the education-only boundary?
      placeholder: |
        - Intent classifier blocks restricted categories
        - Hard-coded escalation responses for restricted topics
        - Input sanitation prevents collection of financial/identity data
        - Response validation blocks prohibited outputs
    validations:
      required: true

  - type: textarea
    id: architectural_alignment
    attributes:
      label: Architecture Milestones
      description: Which system layers are impacted?
      placeholder: |
        - Simulation capture
        - Transcript processing & knowledge extraction
        - Canonical content governance
        - RAG / retrieval
        - LLM orchestration
        - TTS delivery
        - Logging & monitoring

  - type: textarea
    id: child_issues
    attributes:
      label: Child Features / Issues
      description: Link related feature issues (e.g., #123, #124)

  - type: textarea
    id: risks
    attributes:
      label: Strategic Risks
      description: High-level risks and mitigation strategy (accuracy, scope creep, privacy)
---
