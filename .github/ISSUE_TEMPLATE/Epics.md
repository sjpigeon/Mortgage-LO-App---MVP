---
name: Mortgage LO Knowledge Delivery – Epic
about: High-level initiative spanning multiple features for the Mortgage LO Knowledge Delivery system
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

        This system includes:
        - Zoom-based simulation capture
        - Transcript processing & structured knowledge extraction
        - Canonical content governance
        - Retrieval-Augmented Generation (RAG)
        - LLM orchestration
        - Text-to-Speech (TTS) delivery
        - Audit & compliance guardrails

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
      description: Define quantifiable outcomes (efficiency, compliance, adoption, etc.)
    validations:
      required: true

  - type: textarea
    id: scope
    attributes:
      label: Scope
      description: Clearly define what is included and excluded.
    validations:
      required: true

  - type: textarea
    id: architectural_alignment
    attributes:
      label: Architecture Milestones
      description: Which system layers are impacted?
      placeholder: |
        - Capture
        - Processing
        - Governance
        - RAG
        - TTS
        - Audit

  - type: textarea
    id: child_issues
    attributes:
      label: Child Features / Issues
      description: Link related feature issues (e.g., #123, #124)

  - type: textarea
    id: risks
    attributes:
      label: Strategic Risks
      description: High-level risks and mitigation strategy

  - type: textarea
    id: compliance_impact
    attributes:
      label: Compliance & Regulatory Impact
      description: SAFE Act, CFPB, retention, AI governance implications
---


