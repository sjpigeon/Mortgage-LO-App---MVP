---
name: Mortgage LO Knowledge Delivery – Feature
about: Engineering feature within the Mortgage LO Knowledge Delivery system
title: "[Feature][Mortgage-LO-Knowledge-Delivery] <Feature Name>"
labels:
  - mortgage-lo-knowledge-delivery
  - feature
assignees: []
body:

  - type: markdown
    attributes:
      value: |
        ## Feature Overview
        Use this template for engineering work supporting the Mortgage LO Knowledge Delivery system.

        Examples:
        - Zoom recording automation
        - Transcript normalization
        - Structured knowledge extraction
        - Canonical content storage
        - RAG indexing
        - LLM orchestration
        - TTS integration
        - Logging and audit controls

  - type: dropdown
    id: layer
    attributes:
      label: Architecture Layer
      options:
        - Zoom Simulation Capture
        - Transcript Processing
        - Knowledge Extraction
        - Canonical Content Library
        - RAG / Retrieval
        - LLM Orchestration
        - Text-to-Speech
        - Audit & Logging
        - Guardrails
    validations:
      required: true

  - type: textarea
    id: problem_statement
    attributes:
      label: Problem Statement
    validations:
      required: true

  - type: textarea
    id: technical_design
    attributes:
      label: Technical Design Notes
      description: APIs, schemas, services, data models, integrations

  - type: textarea
    id: tasks
    attributes:
      label: Implementation Tasks
      value: |
        - [ ] Design
        - [ ] Build
        - [ ] Unit Test
        - [ ] Security Review
        - [ ] Compliance Validation
        - [ ] Deploy

  - type: textarea
    id: acceptance_criteria
    attributes:
      label: Acceptance Criteria
    validations:
      required: true

  - type: textarea
    id: ai_governance
    attributes:
      label: LLM / AI Governance
      description: Model provider, versioning, prompt control, restrictions

  - type: textarea
    id: audit_requirements
    attributes:
      label: Audit Logging Requirements
      description: Define required logging for traceability

  - type: textarea
    id: dependencies
    attributes:
      label: Dependencies
---
