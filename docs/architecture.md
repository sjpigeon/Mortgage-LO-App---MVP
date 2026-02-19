flowchart LR
  A[Simulation Capture<br/>(Training system + Zoom recording)] --> B[Transcript Processing<br/>(cleanup, speaker separation)]
  B --> C[Knowledge Extraction<br/>(LLM transforms transcript to structured artifacts)]
  C --> D[Canonical Content Library<br/>(approved, versioned content blocks)]
  D --> E[RAG / Retrieval<br/>(embed + search content blocks)]
  E --> F[LLM Orchestration<br/>(response constrained to retrieved content)]
  F --> G[Guardrails<br/>(intent classifier + output validator + escalation templates)]
  G --> H[TTS<br/>(convert final text to audio)]
  F --> I[Logging & Monitoring<br/>(non-PII trace, prompt/model versions, validator outcome)]
  G --> I
  H --> I
