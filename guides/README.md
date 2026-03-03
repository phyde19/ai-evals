# MLflow 3 on Azure Databricks: System Architecture for GenAI Evaluation

## The 80/20

MLflow 3 is a metadata and observability platform — not a runtime — that organizes everything about a GenAI application's lifecycle under a single entity hierarchy rooted in **Experiments**. At its core, the system does three things: (1) captures **Traces** (structured execution logs of every call your app makes), (2) attaches **Assessments** to those traces (quality judgments from humans, LLM judges, or code), and (3) uses those assessed traces to drive two parallel feedback loops — offline **Evaluation** during development and online **Production Monitoring** in deployment. The key architectural insight is that both loops use the same primitives: the same `Scorer` interface evaluates traces identically whether called by `mlflow.genai.evaluate()` in a notebook or by the production monitoring service sampling live traffic. On Databricks specifically, the storage layer maps onto Unity Catalog (datasets are UC Delta tables, trace artifacts live in UC volumes, prompts are UC-governed), so everything inherits lakehouse access control and lineage for free.

---

## 1. The Entity Model

Everything lives inside an **Experiment** — a named container scoped to one application. The Experiment is the same entity used in classic ML (experiment tracking, runs, metrics), but in GenAI mode it organizes a different set of children.

```
Experiment (one per application)
│
├── Traces ──────────────── execution logs (the foundational primitive)
│   ├── TraceInfo           metadata: id, status, timestamps, tags (stored in DB, indexed)
│   └── TraceData           payload: tree of Spans (stored in artifact storage)
│       └── Span[]          individual operations (LLM call, retrieval, tool use)
│           ├── inputs/outputs
│           ├── attributes (model name, temperature, token counts)
│           ├── span_type (CHAT_MODEL | RETRIEVER | TOOL | AGENT | CHAIN | ...)
│           └── parent_id → forms execution tree
│
├── Assessments ─────────── attached TO a trace (or to a specific span)
│   ├── Feedback            quality judgments ("was this response good?")
│   │                       source: end_user | expert | scorer (LLM judge or code)
│   └── Expectation         ground truth ("what SHOULD the answer have been?")
│                            source: domain expert
│
├── Evaluation Datasets ─── curated test cases (stored as UC Delta tables)
│   └── Records[]           { inputs, expectations?, source?, tags? }
│                            source tracking: human | document | trace
│
├── Evaluation Runs ─────── results of running evaluate() (special type of MLflow Run)
│   ├── Traces[]             one per dataset row
│   ├── Feedback[]           scorer assessments on each trace
│   └── Aggregate Metrics    mean/min/max/pass_rate across all traces
│
├── Labeling Sessions ───── queues of traces for human review (special type of MLflow Run)
│   ├── Labeling Schemas     structured questions for reviewers
│   └── Assessments          expert-provided feedback and expectations
│
├── Logged Models ───────── application version snapshots
│   └── links to: traces, prompts, eval runs, git commits, params
│
└── Prompts ─────────────── versioned LLM prompt templates (UC-governed)
    └── aliases ("production", "staging") for deployment management
```

### Important structural observations

- **Traces are the universal join key.** Everything connects through traces. Assessments attach to traces. Evaluation datasets are created from traces. Evaluation runs produce traces. Production monitoring scores traces. The trace_id is the spine of the entire system.

- **Assessments are polymorphic but unified.** Whether feedback comes from an end-user thumbs-up, a domain expert's structured review, or an automated LLM judge, it's the same `Assessment` entity attached to the same trace. The `AssessmentSource` field distinguishes origin (`HUMAN`, `LLM_JUDGE`, `CODE`).

- **Evaluation Runs and Labeling Sessions are both MLflow Runs under the hood.** They show up in `mlflow.search_runs()`. This means the classic ML infrastructure (run comparison, metric history, parameter logging) applies to GenAI evaluation results too.

- **LoggedModel is a metadata hub, not a model store.** It links a conceptual "version" of your app to external code (git commit), configuration (params), traces it generated, prompts it used, and evaluation runs that measured it. You can optionally package deployable artifacts, but the primary role is cross-referencing.

---

## 2. Storage Architecture

MLflow splits storage by access pattern:

| What | Where | Why |
|---|---|---|
| **TraceInfo** (metadata, tags, status) | Relational database (managed by Databricks) | Fast indexed queries for search/filter |
| **TraceData** (spans, full payloads) | Artifact storage (UC volumes on Databricks) | Cost-effective for large payloads |
| **Evaluation Datasets** | Unity Catalog Delta tables | Versioning, lineage, governance, sharing |
| **Prompts** | Unity Catalog | Version control, aliases, access control |
| **Evaluation Run metrics** | MLflow Run storage | Standard metric/param/tag tracking |
| **Archived traces** | UC Delta tables (opt-in) | Long-term analytics and custom dashboards |

On Databricks, trace data access is governed by UC volume privileges. Evaluation datasets inherit UC table permissions (`CREATE TABLE` required to create). This means your security model is the same one you use for all other data assets.

---

## 3. The Scorer / Judge Abstraction

This is the core evaluation primitive and the most important abstraction to understand.

```
                    ┌──────────────────────────┐
                    │         Scorer            │  ← unified interface
                    │  receives: Trace          │
                    │  returns:  Feedback        │
                    └──────┬───────────────────┘
                           │
              ┌────────────┼────────────────┐
              │            │                │
     ┌────────▼──┐  ┌──────▼──────┐  ┌──────▼──────┐
     │ Built-in  │  │ Custom LLM  │  │  Code-based │
     │ LLM Judge │  │   Judge     │  │   Scorer    │
     └───────────┘  └─────────────┘  └─────────────┘
```

**Scorers vs. Judges — the key distinction:**
- A **Judge** is a callable that evaluates text: `is_correct(request, response, expected) → Feedback`. Judges understand text, not traces.
- A **Scorer** wraps a judge (or arbitrary code). It receives a `Trace`, extracts the relevant fields (request, response, retrieved_context), and passes them to the judge. Scorers are the adapter between the trace data model and evaluation logic.

**The same Scorer instance is used in both:**
- `mlflow.genai.evaluate()` during development (offline)
- `Scorer.register() → Scorer.start()` for production monitoring (online)

This is the architectural guarantee that dev and prod evaluation are consistent.

### Built-in Judges (what ships out of the box)

| Judge | Inputs | Needs Ground Truth? | Evaluates |
|---|---|---|---|
| `Safety` | request, response | No | Harmful/toxic content |
| `RelevanceToQuery` | request, response | No | Response relevance |
| `RetrievalGroundedness` | request, response, context | No | Hallucination detection |
| `RetrievalRelevance` | request, response, context | No | Retrieved context relevance |
| `RetrievalSufficiency` | request, response, context, expected | Yes | Context completeness |
| `Correctness` | request, response, expected | Yes | Answer accuracy |
| `Guidelines` | request, response, guidelines | No | Custom natural-language rules |
| `Fluency` | request, response | No | Grammar and flow |
| `Completeness` | request, response, expected | Yes | Addresses all questions |
| `Equivalence` | request, response, expected | Yes | Semantic match to expected |
| `ToolCallCorrectness` | request, response, expected | Yes | Correct tool calls/args |
| `ToolCallEfficiency` | request, response | No | No redundant tool calls |

**Multi-turn judges** (operate on `session` instead of single trace):
`ConversationCompleteness`, `UserFrustration`, `KnowledgeRetention`, `ConversationalGuidelines`, `ConversationalRoleAdherence`, `ConversationalSafety`, `ConversationalToolCallEfficiency`

### The LLM powering judges

By default, judges use a Databricks-hosted LLM optimized for quality assessment (backed by Azure OpenAI, with abuse monitoring opted out). You can override with any Databricks model serving endpoint: `Safety(model="databricks:/your-endpoint")`. EU workspaces automatically use EU-hosted models.

---

## 4. The Two Evaluation Loops

### Loop A: Offline Evaluation (Development)

```
┌──────────────┐    ┌──────────────┐    ┌────────────┐
│  Evaluation   │    │  predict_fn  │    │  Scorers   │
│  Dataset      │───▶│  (your app)  │───▶│  (judges)  │───▶ Evaluation Run
│  {inputs,     │    │  produces    │    │  score     │     {traces, feedback,
│   expectations}│    │  Traces      │    │  traces    │      aggregate metrics}
└──────────────┘    └──────────────┘    └────────────┘
```

`mlflow.genai.evaluate()` orchestrates this. Two modes:
1. **Direct evaluation** (recommended): MLflow calls your app → captures traces → runs scorers. Traces are identical to production, so scorers are reusable.
2. **Answer sheet**: You provide pre-computed outputs or existing traces → MLflow runs scorers on them.

Parallelized via thread pool (`MLFLOW_GENAI_EVAL_MAX_WORKERS`).

### Loop B: Production Monitoring (Online)

```
┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│  Live traffic │    │  MLflow      │    │  Registered    │
│  (production  │───▶│  Experiment  │───▶│  Scorers       │───▶ Feedback attached
│   traces)     │    │  (trace log) │    │  (sample_rate) │     to production traces
└──────────────┘    └──────────────┘    └────────────────┘
```

Scorers follow a lifecycle: `define → register(name) → start(sample_rate) → update() → stop() → delete()`. Scorers are immutable — each operation returns a new instance. Max 20 active scorers per experiment.

Sampling is configurable per-scorer:
- Safety checks: `sample_rate=1.0` (check everything)
- Expensive LLM judges: `sample_rate=0.05` (sample 5%)
- Development iteration: `sample_rate=0.3-0.5`

`backfill_scorers()` retroactively applies new scorers to historical traces.

---

## 5. The Trace Data Flow (How Data Moves Through the System)

```
 YOUR APP                    MLFLOW                          DATABRICKS
 ────────                    ──────                          ──────────
                                                             
 @mlflow.trace ──────────▶ Trace logged to ──────────────▶ TraceInfo → DB
 or autolog()               Experiment                      TraceData → UC Volume
                                │
                                │ (production)
                                ├──────────────▶ Registered Scorers sample
                                │                traces, attach Feedback
                                │
                                │ (development)
                                ├──────────────▶ evaluate() runs app,
                                │                captures traces, scores them
                                │
                                │ (human review)
                                ├──────────────▶ Labeling Session queues
                                │                traces for expert review
                                │
                                │ (dataset creation)
                                ├──────────────▶ search_traces() → filter
                                │                → merge_records() into
                                │                EvaluationDataset (UC table)
                                │
                                │ (archival)
                                └──────────────▶ enable_trace_archival()
                                                 → UC Delta table
```

### The intended developer journey

1. **Instrument** — Add `@mlflow.trace` or `mlflow.openai.autolog()` to your app. Traces flow automatically.
2. **Observe** — View traces in the MLflow UI. Debug with full execution trees.
3. **Curate** — Select representative traces → create an EvaluationDataset.
4. **Evaluate** — Run `mlflow.genai.evaluate()` with built-in judges. Get aggregate quality metrics.
5. **Improve** — Change your app (prompt, model, retrieval). Re-evaluate. Compare evaluation runs.
6. **Label** — Send ambiguous cases to domain experts via Labeling Sessions. Collect ground truth.
7. **Align** — Use expert labels to align LLM judges with human judgment.
8. **Deploy** — Link your app version (`LoggedModel`) to traces and eval results. Deploy via Agent Framework.
9. **Monitor** — `Scorer.register()` → `Scorer.start()` with the same scorers used in dev.
10. **Iterate** — Production traces reveal new issues → feed back into evaluation datasets → repeat.

---

## 6. Databricks-Specific Platform Integration

### What Databricks adds beyond open-source MLflow

| Capability | OSS MLflow | Databricks Managed MLflow |
|---|---|---|
| Trace storage | Local filesystem or configured backend | UC-governed volumes with access control |
| Evaluation datasets | In-memory or local files | UC Delta tables with versioning and lineage |
| Production monitoring | Not available | Managed service with scorer lifecycle |
| Human labeling | Not available | Review App with structured labeling sessions |
| LLM judges | Self-hosted | Databricks-hosted optimized judge models |
| Prompt registry | Basic file-based | UC-governed with aliases and sharing |
| Trace archival | Manual | Automated to UC Delta tables |
| Deployment | Manual | Agent Framework + Model Serving |
| Metric backfill | Not available | `backfill_scorers()` for historical traces |

### Auth and connectivity

From local IDE:
```
DATABRICKS_TOKEN=<pat>
DATABRICKS_HOST=https://<workspace>.azuredatabricks.net
MLFLOW_TRACKING_URI=databricks
MLFLOW_REGISTRY_URI=databricks-uc
```

From Databricks notebook: zero config — experiment is auto-created.

### Key SDK entry points

```python
pip install "mlflow[databricks]>=3.1"

import mlflow
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/my-app")

# Tracing
mlflow.openai.autolog()                    # auto-instrument OpenAI/Databricks FM APIs
@mlflow.trace                               # manual instrumentation

# Evaluation
mlflow.genai.evaluate(data=..., predict_fn=..., scorers=[...])

# Production monitoring
scorer.register(name="...").start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))

# Datasets
mlflow.genai.datasets.create_dataset(name="catalog.schema.table")

# Version tracking
mlflow.set_active_model(name="my-app-v2")
```

---

## 7. Key Concepts to Keep Straight

**Experiment vs. Run vs. Evaluation Run vs. Labeling Session**
An Experiment is the top-level container (one per app). A Run is a generic tracking unit. An Evaluation Run is a specialized Run created by `evaluate()` that holds traces + feedback + metrics. A Labeling Session is a specialized Run that holds traces queued for human review.

**Trace vs. Span**
A Trace is the complete execution record for one request. A Span is one node in the execution tree within a trace (one LLM call, one retrieval, one tool invocation). Spans have types (`CHAT_MODEL`, `RETRIEVER`, `TOOL`, `AGENT`, etc.) that scorers can use to extract the right data.

**Scorer vs. Judge**
A Judge evaluates text (`is_correct(request, response, expected) → Feedback`). A Scorer receives a Trace, extracts fields, and calls a Judge (or runs code). All Judges are used through Scorers. You can use Judges directly for ad-hoc testing, but the evaluation system operates on Scorers.

**Feedback vs. Expectation (both are Assessments)**
Feedback = "how good was this output?" (judgment). Expectation = "what should the output have been?" (ground truth). Both attach to traces. Both can come from humans or code. The distinction matters because some judges require expectations (Correctness, ToolCallCorrectness) while others don't (Safety, RelevanceToQuery).

**LoggedModel vs. Registered Model**
A `LoggedModel` is an MLflow 3 GenAI concept — a versioned metadata record pointing to your app. A Registered Model is the classic ML model registry concept in Unity Catalog. For GenAI, `LoggedModel` is the primary versioning mechanism. You can optionally register a LoggedModel to UC Model Registry for formal deployment governance.

---

## 8. What's Databricks-Only vs. What's Open Source

| Feature | Where it lives |
|---|---|
| Tracing SDK (`@mlflow.trace`, autolog) | Open source |
| `mlflow.genai.evaluate()` | Open source |
| Scorer / Judge SDK | Open source |
| `Scorer.register()` / `.start()` / `.stop()` | **Databricks only** |
| Review App / Labeling Sessions | **Databricks only** |
| Evaluation Datasets (UC-backed) | **Databricks only** |
| `backfill_scorers()` | **Databricks only** |
| Trace archival to Delta | **Databricks only** |
| Hosted LLM judge models | **Databricks only** |
| Prompt Registry (UC-governed) | **Databricks only** |
