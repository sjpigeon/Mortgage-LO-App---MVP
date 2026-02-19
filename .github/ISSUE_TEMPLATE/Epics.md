---
name: Mortgage AI – Epic
description: High-level initiative spanning multiple features for the Mortgage LO Knowledge System
title: "[Epic][Mortgage-LO-Knowledge] <Initiative Name>"
labels:
  - mortgage-ai
  - epic
  - ai-platform
body:

  - type: markdown
    attributes:
      value: |
        ## Epic Overview
        This Epic represents a major initiative within the Mortgage Loan Officer Knowledge Delivery System.
        Epics should align to architectural milestones such as:
        - Zoom Simulation Capture
        - Knowledge Extraction Pipeline
        - Canonical Content Governance
        - RAG / LLM Orchestration
        - TTS Delivery Layer
        - Audit & Risk Controls

  - type: textarea
    id: objective
    attributes:
      label: Business Objective
      description: What business outcome does this Epic enable?
    validations:
      required: true

  - type: textarea
    id: success_metrics
    attributes:
      label: Success Metrics
      description: Quantifiable outcomes
      placeholder: |
        - % reduction in LO repetitive calls
        - % borrower self-service adoption
        - Compliance validation success rate
    validations:
      required: true

  - type: textarea
    id: scope
    attributes:
      label: Scope
      description: What is included and excluded?
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
      description: List linked feature issues
      placeholder: |
        - #123
        - #124

  - type: textarea
    id: risks
    attributes:
      label: Strategic Risks
      description: High-level risks and mitigation approach

  - type: textarea
    id: compliance_impact
    attributes:
      label: Compliance & Regulatory Impact
      description: SAFE Act, CFPB, data retention implications

---


