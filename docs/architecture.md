# Mortgage LO Knowledge Delivery  
## System Architecture (Education + Operational Guidance Only)

---

## 1. Scope Definition

Mortgage LO Knowledge Delivery is an **education and operational guidance platform**.

It:

- Uses internal simulation/training recordings only  
- Extracts structured knowledge from Loan Officer simulations  
- Generates borrower-facing educational responses  
- Enforces strict guardrails to prevent loan origination activities  

It does **NOT**:

- Quote rates, APR, or payment amounts  
- Assess eligibility or qualification  
- Accept applications  
- Collect or store borrower financial or identity data  
- Perform underwriting logic  

This boundary is enforced technically via guardrails and validation layers.

---

## 2. High-Level Architecture Overview

---

## 3. Architecture Layers (Aligned to Project v2 Fields)

### 3.1 Simulation Capture
- Internal training sessions only
- No real borrower conversations
- Recordings used solely to extract reusable knowledge

---

### 3.2 Transcript Processing
- Remove filler language
- Normalize terminology
- Separate speaker roles
- Retain raw transcript for reference (internal only)

---

### 3.3 Knowledge Extraction
LLM transforms transcripts into structured artifacts:

Example output:

```json
{
  "topic": "Document checklist for W2 borrower",
  "summary": "...",
  "key_steps": [],
  "faq_items": [],
  "escalation_triggers": []
}


