# MLflow 3 on Databricks: A Systems Perspective

## The 80/20 View

MLflow on Databricks is a **lifecycle management system for GenAI applications** built around a single central primitive: the **Trace**. Every other entity in the system — datasets, evaluation runs, scorers, human labels, app versions — either produces, consumes, or annotates traces. The platform is organized into **Experiments** (one per application), which act as namespaces containing all artifacts across an app's full lifecycle. The fundamental design insight is that *the same quality measurement machinery* (scorers) runs both in development (offline, on-demand) and in production (online, scheduled, sampled) — this symmetry is what allows a coherent signal about application quality to flow across the entire SDLC. On Databricks specifically, the platform layers on top of Unity Catalog (governance, versioning, SQL queryability) and Managed MLflow (no infrastructure to run), turning what is otherwise an OSS tool into a governed, enterprise LLMOps platform.

---

## The Entity Graph

Every entity in MLflow belongs to an **Experiment**. Think of an Experiment as the directory for one application. The entities are:

```
Experiment
├── Observability
│   └── Trace                       ← the central primitive
│       ├── TraceInfo               ← metadata row (relational DB, indexed)
│       ├── TraceData               ← spans tree (artifact store, blob)
│       └── Assessment[]            ← quality signals attached to trace
│           ├── Feedback            ← judgment ("was this correct?")
│           └── Expectation         ← ground truth ("the correct answer is...")
│
├── Evaluation
│   ├── EvaluationDataset           ← versioned test case collection (Unity Catalog)
│   └── EvaluationRun               ← results of running scorers over a dataset
│       ├── Trace[]                 ← one trace per dataset row
│       ├── Feedback[]              ← scorer outputs attached to each trace
│       └── AggregateMetrics        ← mean/pass-rate rolled up across all traces
│
├── Human Labeling
│   ├── LabelingSession             ← queue of traces for domain experts to review
│   └── LabelingSchema              ← structured question definition (what to ask)
│
└── Application Versioning
    ├── LoggedModel                 ← snapshot of an app version (metadata hub or deployable)
    └── Prompt                      ← versioned LLM prompt template
```

**Key structural insight:** `EvaluationRun` and `LabelingSession` are both **MLflow Runs** under the hood. They are different uses of the same storage entity and can both be queried via `mlflow.search_runs()`. This is an important abstraction collapse — the "run" is the general-purpose container for "something that happened against this experiment."

---

## Storage Architecture: Two Layers

MLflow splits every Trace into two storage tiers for performance and cost reasons:

```
TraceInfo  →  Relational database (indexed rows)
               • trace_id, status, timestamps, tags, previews
               • Fast: supports search, filter, pagination
               • Small: one row per trace

TraceData  →  Artifact store (blob/object storage)
               • The full span tree: every LLM call, tool use, retrieval
               • Cheap: unlimited volume, not queried relationally
               • Large: can be MBs for complex agent executions
```

This explains why `mlflow.search_traces()` is fast (it queries TraceInfo rows) but fetching individual trace details loads from artifact storage. When you search by tag, timestamp, or status, you're querying the relational layer. When you open a trace to inspect its spans, you're pulling from the artifact layer.

### Unity Catalog Trace Storage (Beta)

On Databricks, traces can optionally be stored in **Unity Catalog Delta tables** instead of the default MLflow control plane. This changes several things:

| Dimension | Default (MLflow control plane) | Unity Catalog (OTEL format) |
|---|---|---|
| Access control | Experiment-level ACLs | UC schema/table permissions |
| Queryability | `mlflow.search_traces()` SDK | Direct SQL via Databricks SQL Warehouse |
| Retention | Managed by MLflow service | Unlimited (Delta table) |
| Trace ID format | `tr-<UUID>` | URI format (OTEL-compatible) |
| Interoperability | MLflow ecosystem | Any OpenTelemetry client |

Choosing UC storage is a governance decision: it gives you SQL queryability and UC-governed access, at the cost of slightly more setup. Evaluation Datasets are **always** stored in Unity Catalog.

---

## The Assessment System: How Quality Signals Work

An **Assessment** is the atomic quality signal in MLflow. All quality measurements — from LLM judges, from end users, from domain experts — are stored as the same data structure (Assessment) and attached to the same entity (Trace). There are two subtypes:

**Feedback** — a judgment about quality:
- Source: automated scorer, end user interaction, domain expert in review app
- Examples: `safety: pass`, `correctness: 0.8`, `thumbs_up: true`
- Used for: tracking quality over time, identifying regressions

**Expectation** — a ground truth label:
- Source: domain experts only (human judgment required)
- Examples: `expected_response: "..."`, `required_facts: [...]`
- Used for: reference answers in scorer evaluation, building evaluation datasets

Both live on the Trace. The same trace can simultaneously carry assessments from an automated scorer, a thumbs-up from an end user, and a corrected answer from a domain expert — all coexisting on the same object.

This matters architecturally because it means **the feedback loop is closed at the Trace level**: you always know, for a given execution, what quality signals have been collected about it, regardless of their source.

---

## The Scorer Abstraction

A **Scorer** is an adapter between a Trace and an evaluation function. This is the most important abstraction in the evaluation system.

```
                    ┌─────────────────────────────────┐
                    │           SCORER                │
                    │                                 │
  Trace  ──────────►│  1. Extract fields from trace   │
                    │     (inputs, outputs, spans...)  │
                    │                                 │
                    │  2. Evaluate                    │
                    │     (LLM judge OR code logic)   │
                    │                                 │
                    │  3. Return Feedback             │──────► attached to Trace
                    │     (score/pass/label)          │
                    └─────────────────────────────────┘
```

A **Judge** is a lower-level primitive that scorers can call. Judges (`mlflow.genai.judges.is_correct`, etc.) are pure text-in/judgment-out functions — they understand text, not traces. Scorers are what bridge the two. This distinction matters: a judge evaluates meaning, a scorer decides *which parts of a trace* to pass to which judge.

### Scorer Taxonomy

| Type | Mechanism | When to use |
|---|---|---|
| **Built-in judges** | Databricks-hosted LLM, pre-prompted | Fastest start; covers RAG, safety, tool calls |
| **Guidelines judges** | Built-in judge + custom natural language rules | Domain-specific pass/fail criteria without code |
| **Custom judges** (`make_judge`) | LLM with your prompt template | Full control over evaluation logic, multi-level scores |
| **Code-based scorers** (`@scorer`) | Pure Python | Deterministic checks: format validation, exact match, regex, latency |

### The Dev/Prod Symmetry

The most architecturally significant property of scorers: **the same scorer runs in both development and production.** This is not just API consistency — it is the mechanism that makes quality signals comparable across environments.

```
Development:
  mlflow.genai.evaluate(data=dataset, predict_fn=my_app, scorers=[safety, correctness])
  │
  └─► Runs app on every dataset row → Traces → Scorers → Feedback → EvaluationRun

Production:
  safety.register(name="safety_prod").start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))
  │
  └─► Runs scorer on sampled live traces → Feedback attached to production Traces
```

In both cases, a Scorer receives a Trace and writes Feedback to it. The infrastructure differs (your laptop vs. Databricks serverless), but the unit of work is identical. This is what allows you to say "our production safety score is consistent with what we measured in evaluation."

### Scorer Lifecycle (Production)

Scorers registered for production monitoring are **immutable** server-side objects with a lifecycle:

```
Unregistered → Registered → Active → Stopped → Deleted
                .register()  .start()   .stop()   delete_scorer()
```

Immutability means `.start()`, `.update()`, `.stop()` all return *new* instances; the original is never mutated. Up to 20 scorers can be active per experiment simultaneously. `backfill_scorer()` retroactively applies a scorer to historical traces — useful when you add a new quality dimension and want historical signal.

---

## The Data Flow: Development → Production Loop

MLflow is designed around a quality improvement flywheel. Here is the intended data flow across the full lifecycle:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   PRODUCTION                                                        │
│                                                                     │
│   App executes ──► Traces logged ──► Scheduled scorers run         │
│                         │                    │                      │
│                         │              Feedback attached            │
│                         │                    │                      │
│                         ▼                    ▼                      │
│             Bad traces surface          Quality trends              │
│             in experiment UI            in dashboards               │
│                         │                                           │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          │  select representative/problematic traces
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   LABELING (optional)                                               │
│                                                                     │
│   LabelingSession created ──► Domain experts review in Review App  │
│         │                             │                             │
│         │                     Expectations written                  │
│         │                     (ground truth labels)                 │
│         │                             │                             │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          │  traces (+ expectations) exported
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   EVALUATION DATASET                                                │
│                                                                     │
│   EvaluationDataset (versioned, in Unity Catalog)                  │
│         │                                                           │
│         │  curated inputs ± ground truth                            │
│         │                                                           │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   DEVELOPMENT                                                       │
│                                                                     │
│   mlflow.genai.evaluate(                                            │
│     data=dataset,           ← evaluation dataset                   │
│     predict_fn=my_app_v2,   ← new version of the app              │
│     scorers=[...],          ← same scorers as production           │
│     model_id="models:/v2"   ← link results to this app version     │
│   )                                                                 │
│         │                                                           │
│         ▼                                                           │
│   EvaluationRun created                                             │
│   ├── Traces (one per dataset row)                                  │
│   ├── Feedback (scorer outputs per trace)                           │
│   └── AggregateMetrics (mean correctness, pass rates, etc.)        │
│                                                                     │
│   Compare v2 metrics vs. v1 ──► Did it improve?                    │
│         │                                                           │
│         ├── Yes ──► promote, redeploy                              │
│         └── No  ──► iterate: tweak prompt, model, retrieval        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
          │
          │  promote to production
          ▼
       (loop)
```

---

## Application Versioning: LoggedModel and Prompt

These two entities answer "which version of the app produced this trace?"

**LoggedModel** is a version snapshot of the entire application. It can be:
1. A **metadata hub** — just a pointer linking a conceptual version to a Git commit, a set of traces it generated, and evaluation runs that tested it. No code packaged.
2. A **deployable artifact** — actual code + config packaged for deployment via Databricks Model Serving.

LoggedModels link to: the traces they generated, the prompts they used, and the evaluation runs that tested them. This gives you full lineage: "version 3 of my app → generated these 10,000 production traces → was evaluated in these 5 evaluation runs → used this prompt template."

**Prompts** are versioned LLM prompt templates with `{{variable}}` interpolation. They have a Git-like version history and support aliases (`"production"`, `"staging"`) for deployment management. Prompts are tracked in the Prompt Registry (part of Unity Catalog) and linked to LoggedModels and EvaluationRuns.

---

## Databricks-Specific Integration Points

When running MLflow on Databricks (as opposed to OSS self-hosted), several things change architecturally:

### What Databricks Manages For You
- **MLflow Tracking Server** — fully managed, no infrastructure setup
- **Artifact Store** — traces stored in Databricks-managed object storage
- **LLM Judge Infrastructure** — built-in judges run on Databricks-hosted models (Azure OpenAI or Databricks Foundation Models); no API keys needed
- **Serverless Compute** — production scorer monitoring runs on Databricks Serverless (no cluster to manage)

### Unity Catalog as the Governance Layer
Unity Catalog governs the entities that need enterprise-grade access control and lineage:
- **Evaluation Datasets** — always stored as UC Delta tables; require `CREATE TABLE` on a UC schema
- **Traces (optional)** — can be stored in UC for SQL queryability and fine-grained access control
- **Logged Models** — registered in UC Model Registry (`"databricks-uc"` as registry URI)
- **Prompts** — stored in UC Prompt Registry

### Authentication for Local Development
From a local IDE/notebook outside Databricks, the connection to managed MLflow is established via environment variables:

```bash
DATABRICKS_HOST=https://<workspace>.azuredatabricks.net
DATABRICKS_TOKEN=<PAT or OAuth token>
MLFLOW_TRACKING_URI=databricks
MLFLOW_REGISTRY_URI=databricks-uc
MLFLOW_EXPERIMENT_ID=<experiment-id>
```

`MLFLOW_TRACKING_URI=databricks` is the single toggle that routes all MLflow SDK calls to the managed Databricks MLflow backend instead of a local server.

### LLM Judges and Data Residency
Built-in judges use third-party LLMs under the hood (including Azure OpenAI operated by Microsoft). Databricks has opted out of abuse monitoring, so no prompts or responses are retained by Azure OpenAI. EU workspaces use EU-hosted models. If this is unacceptable, you can point any judge at your own Databricks Model Serving endpoint:

```python
Correctness(model="databricks:/my-hosted-judge-endpoint")
```

---

## The Two UIs

### MLflow Experiment UI
The primary operational interface. Surfaces all entities within an Experiment:
- **Traces tab** — search, filter, inspect individual traces and their spans; select traces to export to evaluation datasets
- **Evaluations tab** — evaluation run results, metric comparisons across versions; labeling sessions
- **Scorers tab** — create, configure, and schedule scorers for production monitoring
- **Models/Prompts tabs** — application version management

### Review App
A separate lightweight web UI purpose-built for domain experts who are not engineers. It presents traces from a LabelingSession and collects structured assessments according to LabelingSchemas. Domain experts see the app's inputs and outputs (not spans/internals) and answer the questions defined by the schema. Their answers are written back as Assessments on the original Traces.

---

## What MLflow Is Not

To complete the mental model, it helps to be explicit about what MLflow does *not* do on Databricks:

- **Not a model training platform** — it tracks experiments and versions; training happens in your code/notebooks
- **Not an agent execution framework** — it observes and evaluates agents; orchestration is Mosaic AI Agent Framework, LangGraph, etc.
- **Not a deployment platform** — LoggedModels link to deployed endpoints; actual serving is Databricks Model Serving
- **Not a data pipeline** — evaluation datasets are curated manually or from traces; no ETL pipelines
- **Not a real-time alerting system** — production monitoring runs on a delay (15-20 min latency); it's for quality trending, not incident response

---

## Summary: The Abstraction Stack

```
Unity Catalog          ← governance, versioning, SQL access
       │
MLflow Experiment      ← namespace for one application
       │
  ┌────┴────────────────────────────────────────┐
  │                                             │
Traces               ←→              Scorers
(execution records)       (quality measurement functions)
  │                                             │
Assessments          ←─── runs over ──────────►│
(feedback + expectations)                      │
  │                                             │
  ├── EvaluationDatasets (curated test cases)  │
  ├── EvaluationRuns (batch quality results)   │
  ├── LabelingSessions (human review queues)   │
  └── LoggedModels / Prompts (version records) │
```

The Trace is what every other entity rotates around. Scorers are the engine that generates quality signal from traces. Assessments are the quality signal itself. Everything else is organizing infrastructure for the lifecycle.
