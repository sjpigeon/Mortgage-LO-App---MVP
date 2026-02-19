---
name: Mortgage LO Knowledge Delivery – Governance Control
about: Governance control for accuracy, scope boundary enforcement, privacy, and content quality within Mortgage LO Knowledge Delivery
title: "[Governance][Mortgage-LO-Knowledge-Delivery] <Control Name>"
labels:
  - mortgage-lo-knowledge-delivery
  - governance
assignees: []
body:

  - type: markdown
    attributes:
      value: |
        ## Governance Control Overview
        Use this template for controls that enforce:
        - Education-only scope boundary
        - Content accuracy and review process
        - Data minimization (no borrower financial/identity data)
        - Model/prompt versioning
        - Output restrictions and escalation behavior
        - Logging and monitoring for quality

  - type: dropdown
    id: control_area
    attributes:
      label: Control Area
      options:
        - Scope Boundary Enforcement
        - Content Review & Approval
        - Accuracy & Hallucination Prevention
        - Data Minimization & Privacy
        - Prompt / Model Versioning
        - Output Validation & Escalation
        - Monitoring & Quality Metrics
    validations:
      required: true

  - type: textarea
    id: control_objective
    attributes:
      label: Control Objective
      description: What risk does this control reduce?
    validations:
      required: true

  - type: textarea
    id: implementation_requirements
    attributes:
      label: Implementation Requirements
      description: Technical/process requirements for the control
      placeholder: |
        - Technical enforcement:
        - Process enforcement:
        - Owners:

  - type: textarea
    id: testing_validation
    attributes:
      label: Testing & Validation Plan
      placeholder: |
        - Test cases:
        - Frequency:
        - Pass/fail criteria:

  - type: textarea
    id: evidence_artifacts
    attributes:
      label: Evidence / Artifacts
      description: What evidence demonstrates the control is working?
      placeholder: |
        - Logs:
        - Review approvals:
        - Test reports:
        - Dashboards:

  - type: textarea
    id: risk_if_uncontrolled
    attributes:
      label: Risk if Control Fails
      placeholder: |
        - Scope creep into restricted areas
        - Inaccurate borrower guidance
        - Unintended collection of sensitive data
        - Reputational harm

  - type: textarea
    id: mitigation_strategy
    attributes:
      label: Mitigation Strategy
      description: How will we prevent, detect, and respond?
---
