---
name: Mortgage LO Knowledge Delivery – Feature
about: Engineering feature within the Mortgage LO Knowledge Delivery system (education + operational guidance only)
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
        Use this template for engineering work supporting Mortgage LO Knowledge Delivery.

        **Scope boundary (non-negotiable):**
        - Use **simulation/training recordings only**
        - Do **not** enable loan origination activities (rates, eligibility, applications, underwriting)
        - Do **not** collect or store borrower financial/identity data

  - type: dropdown
    id: layer
    attributes:
      label: Architecture Layer
      options:
        - Simulation Capture
        - Transcript Processing
        - Knowledge Extraction
        - Canonical Content Library
        - RAG / Retrieval
        - LLM Orchestration
        - Text-to-Speech
        - Logging & Monitoring
        - Guardrails
    validations:
      required: true

  - type: checkboxes
    id: scope_boundary_confirmation
    attributes:
      label: Scope Boundary Confirmation
      description: These must be true for every Feature in this repository.
      options:
        - label: This feature uses internal simulation/training data only (no real borrower conversations).
          required: true
        - label: This feature does NOT generate rates/APR/payment quotes or calculators.
          required: true
        - label: This feature does NOT assess eligibility, pre-qualification, or underwriting.
          required: true
        - label: This feature does NOT intake, store, or persist borrower financial/identity data.
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
      placeholder: |
        - Inputs:
        - Outputs:
        - Data stores:
        - Interfaces (APIs/events):
        - Failure modes:

  - type: textarea
    id: tasks
    attributes:
      label: Implementation Tasks
      value: |
        - [ ] Design
        - [ ] Build
        - [ ] Unit Test
        - [ ] Integration Test
        - [ ] Security Review (as applicable)
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
      label: LLM / AI Usage Notes
      description: Provider/model used, prompt versioning, and output restrictions
      placeholder: |
        - LLM provider:
        - Model:
        - Prompt template version:
        - Retrieval inputs:
        - Output restrictions enforced by:
          - System prompt rules
          - Post-generation validator
          - Escalation templates

  - type: textarea
    id: prohibited_topics_handling
    attributes:
      label: Prohibited Topic Handling
      description: Describe how the feature handles restricted inputs/outputs.
      placeholder: |
        - Intent categories blocked:
        - Escalation message used:
        - Validation rules:

  - type: textarea
    id: logging_requirements
    attributes:
      label: Logging & Traceability Requirements
      description: Define required logging for debugging and quality assurance (non-PII).
      placeholder: |
        - Content IDs + versions retrieved
        - Model + prompt version
        - Validator decision (pass/block/escalate)
        - Timestamp + session identifier (non-PII)

  - type: textarea
    id: dependencies
    attributes:
      label: Dependencies
      placeholder: |
        - Depends on:
        - Blocks:
        - Related:
---
