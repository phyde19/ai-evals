# MLflow Entity Data Flow: A Developer Journey

> **Scenario:** You've built a knowledge retrieval AI chat app — React frontend, FastAPI backend, vector database for RAG. Users ask questions, the backend retrieves documents and sends them to an LLM, the response streams back to the browser. You want to use MLflow on Databricks to monitor and evaluate it.

---

## How to read this guide

Each section is a phase of your journey. For each phase:
- **What you do** — the action you take
- **What gets created** — the entities that come into existence
- **Where it lands** — the storage destination
- **What it enables** — what this unlocks downstream

---

## Phase 1: One-time Setup

**You:** Go to Databricks workspace → Experiments → "GenAI apps & agents" → create experiment. Set three env vars in your FastAPI server's environment.

```bash
DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
DATABRICKS_TOKEN=<your-pat>
MLFLOW_TRACKING_URI=databricks
MLFLOW_EXPERIMENT_ID=<id-from-ui>
```

**Created together:**
```
→ Experiment (1 per application, lives forever)
```

**Lands in:** Databricks-managed MLflow backend (relational DB)

**Enables:** A named home for every entity that follows. Nothing else can exist without this.

---

## Phase 2: Instrument Your FastAPI Backend

**You:** Add MLflow tracing to your FastAPI app. Since you're using OpenAI-compatible calls, autolog handles LLM calls automatically. You manually wrap your retrieval function and the top-level request handler.

```python
# main.py
import mlflow
from mlflow.entities import AssessmentSource

mlflow.openai.autolog()  # auto-traces every LLM call
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment(experiment_id=os.environ["MLFLOW_EXPERIMENT_ID"])

@app.post("/chat")
@mlflow.trace(name="chat_request", span_type="CHAIN")
async def chat(request: ChatRequest):
    context = retrieve_docs(request.message)
    response = call_llm(context, request.message)

    # Return trace_id so React can reference it later for feedback
    trace_id = mlflow.get_last_active_trace_id()
    return {"response": response, "trace_id": trace_id}

@mlflow.trace(name="retrieve_docs", span_type="RETRIEVER")
def retrieve_docs(query: str):
    # your vector DB call
    ...

# No decoration needed on call_llm — openai.autolog() handles it
```

**What this does at request time:** Every call to `/chat` automatically produces:

```
→ Trace              (1 per HTTP request)
   └── Span: chat_request     (root span, span_type=CHAIN)
       ├── Span: retrieve_docs (span_type=RETRIEVER, inputs=query, outputs=docs[])
       └── Span: openai.chat  (auto, span_type=CHAT_MODEL, tokens, latency, messages)
```

**Lands in:**
- `TraceInfo` (metadata row) → Databricks relational DB, indexed, immediately searchable
- `TraceData` (full span tree) → artifact storage (UC volume if configured), blob

**Enables:** Real-time visibility in MLflow UI. Every production request is now observable. This is the foundation — no other entity flows without Traces.

> **Key insight:** `@mlflow.trace` on `retrieve_docs` with `span_type="RETRIEVER"` is not cosmetic. RAG-specific judges (`RetrievalGroundedness`, `RetrievalRelevance`, `RetrievalSufficiency`) scan the trace for `RETRIEVER`-typed spans to extract retrieved context. If you skip this, those judges have nothing to work with.

---

## Phase 3: Collect User Feedback in Production

**You:** Your React UI shows a thumbs up / thumbs down after each response. The frontend stores the `trace_id` from the chat response and POSTs it back when the user clicks.

```python
# FastAPI feedback endpoint
@app.post("/feedback")
async def submit_feedback(trace_id: str, thumbs_up: bool, user_id: str):
    mlflow.log_feedback(
        trace_id=trace_id,
        name="user_satisfaction",
        value=thumbs_up,
        source=AssessmentSource(source_type="HUMAN", source_id=user_id),
        rationale=None
    )
```

**Created, attached to the existing Trace:**

```
Trace (already exists)
└── Feedback: user_satisfaction   ← NEW, source_type=HUMAN
    ├── value: True/False
    └── source_id: user_123
```

**Lands in:** Attached to the `Trace` in MLflow's backend. The Trace now carries a quality signal from the real user.

**Enables:**
- Filtering traces by satisfaction score in the UI (find everything users thumbed down)
- Selecting low-satisfaction traces for your evaluation dataset
- Tracking satisfaction trends over time

> **The `trace_id` handshake:** This is a deliberate API contract your backend must maintain. The React app stores `trace_id` in component state when the response arrives. When the user clicks thumbs down, it sends `trace_id` back. MLflow then finds the right Trace server-side and attaches the `Feedback` to it. Without returning `trace_id` from `/chat`, you cannot close this loop.

---

## Phase 4: Curate an Evaluation Dataset

**You:** After a week of traffic, you have hundreds of traces. Some users thumbed down. You want to turn the bad ones into a test suite.

```python
import mlflow
from mlflow.genai.datasets import create_dataset

# 1. Create the dataset container (UC Delta table is created automatically)
eval_dataset = create_dataset(name="prod_catalog.ml_schema.chat_eval_v1")

# 2. Find traces where users were unhappy
bad_traces = mlflow.search_traces(
    filter_string="tag.user_satisfaction = 'False'",
    max_results=50
)

# 3. Pull in some good ones too, for regression coverage
good_traces = mlflow.search_traces(
    filter_string="tag.user_satisfaction = 'True'",
    max_results=50
)

# 4. Merge both into the dataset
eval_dataset = eval_dataset.merge_records(bad_traces)
eval_dataset = eval_dataset.merge_records(good_traces)
```

**Created:**

```
→ EvaluationDataset  (1 UC Delta table at prod_catalog.ml_schema.chat_eval_v1)
   └── Record[]       (100 rows, each: {inputs, source: {trace: trace_id}})
```

**Lands in:** Unity Catalog Delta table. Requires `CREATE TABLE` on the UC schema. Versioned, governed, shareable with your team.

**Enables:** A stable, reusable test suite. You can now run `evaluate()` against this dataset repeatedly as you make changes to your app. The `source.trace.trace_id` field on each record keeps the lineage — you always know which production request each test case came from.

> **Note:** At this point the dataset has `inputs` (the user's question) but no `expectations` (ground truth answers). That's fine. Many judges — Safety, RelevanceToQuery, RetrievalGroundedness — don't need ground truth. You only need expectations for judges like `Correctness`. You'll add those in Phase 6.

---

## Phase 5: Run Your First Evaluation

**You:** You want to know if your app is hallucinating and whether retrieved context is relevant. Run evaluation against the dataset you just built.

```python
import mlflow
from mlflow.genai.scorers import RetrievalGroundedness, RetrievalRelevance, Safety

mlflow.set_experiment(experiment_id=os.environ["MLFLOW_EXPERIMENT_ID"])

results = mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=chat_predict_fn,   # thin wrapper around your actual app
    scorers=[
        Safety(),
        RetrievalGroundedness(),
        RetrievalRelevance(),
    ]
)
```

**Created together — all at once, automatically:**

```
→ EvaluationRun           (1 MLflow Run, created by evaluate())
   ├── Trace[]             (1 new Trace per dataset row — your app runs again)
   │    └── Span[]         (same structure as production traces)
   ├── Feedback[]          (3 per trace: safety, groundedness, relevance)
   │    ├── Feedback: safety              value: YES/NO
   │    ├── Feedback: retrieval_groundedness  value: YES/NO
   │    └── Feedback: retrieval_relevance     value: YES/NO
   └── AggregateMetrics    (groundedness_pass_rate: 0.74, safety_pass_rate: 1.0, ...)
```

**Lands in:** EvaluationRun → MLflow Run storage. The 100 new Traces and their Feedback land in the same Experiment as your production traces.

**Enables:**
- Seeing immediately that 26% of responses are hallucinating (not grounded in retrieved context)
- Drilling into individual failing traces to see which queries are problematic
- A baseline to compare against after you fix things

> **Why the app runs again, not the production traces:** `evaluate()` in "direct" mode calls your actual `predict_fn` on each dataset row to generate *fresh* Traces. This matters because your production traces were generated by whatever version of your app was live then. Evaluation re-runs your *current* code against those same inputs, so you're testing your current version, not replaying history.

---

## Phase 6: Collect Ground Truth from Domain Experts

**You:** You need someone who knows your knowledge base to review the app's answers and write what the correct answers should have been. This creates `Expectations` — ground truth you can use with `Correctness` and `Completeness` judges.

```python
import mlflow.genai.labeling as labeling
import mlflow.genai.label_schemas as schemas

# 1. Create a schema that tells reviewers what to provide
expected_response_schema = schemas.create_label_schema(
    name="correct_answer",
    schema_type="EXPECTATION",
    title="What should the correct answer be?",
    input_type=schemas.InputText(max_length=2000)
)

# 2. Create a labeling session — queue traces for your domain expert
session = labeling.create_labeling_session(
    name="hallucination-review-jan-2026",
    label_schemas=[expected_response_schema],
    assigned_users=["expert@yourcompany.com"]
)

# 3. Add the traces that failed groundedness in evaluation
failing_traces = mlflow.search_traces(
    filter_string="feedback.retrieval_groundedness = 'NO'"
)
session.add_traces(failing_traces)
```

**Created together:**

```
→ LabelingSchema    (reusable definition: "what question do we ask reviewers?")
→ LabelingSession   (an MLflow Run; queues traces for review)
   └── references Traces[] (the failing ones from Phase 5)
```

**Lands in:** LabelingSession → MLflow Run storage. LabelingSchema → MLflow backend.

**What the expert sees:** They get an email, open the Review App in their browser, see each user question + app response side-by-side, and type the correct answer in a text box.

**When they submit, created on each reviewed Trace:**

```
Trace (already exists)
└── Expectation: correct_answer   ← NEW, source_type=HUMAN
    └── value: "The correct answer is..."
```

**Enables:** Ground-truth labels that flow back onto the original Traces. You can now:
- Sync the session into your EvaluationDataset: `session.sync(dataset_name="...")`
- Re-run evaluation with `Correctness()` scorer, which now has expected answers to compare against
- Use these labeled examples to align your custom judges (Phase 7)

---

## Phase 7: Version Your App and Compare

**You:** Based on evaluation results, you improve your retrieval (better chunking, reranking). You want to compare v1 vs v2 side-by-side.

```python
import subprocess

git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()

# Register this version of your app
model_v2 = mlflow.create_external_model(
    name=f"chat-app-{git_commit}",
    model_type="rag-agent",
    params={"llm_model": "databricks-claude-sonnet-4", "retrieval_k": "8"},
    tags={"git_commit": git_commit, "change": "reranker-added"}
)

# Run evaluation linked to this version
results_v2 = mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=chat_predict_fn_v2,
    scorers=[Safety(), RetrievalGroundedness(), RetrievalRelevance(), Correctness()],
    model_id=model_v2.model_id
)
```

**Created:**

```
→ LoggedModel        (metadata record: params, tags, git commit, model_id)
→ EvaluationRun      (linked to LoggedModel via model_id)
   ├── Trace[]        (new traces for v2)
   ├── Feedback[]     (now includes Correctness scores, since we have Expectations)
   └── AggregateMetrics
```

**Lands in:** LoggedModel → MLflow entities storage. EvaluationRun → same as before.

**Enables:** Side-by-side comparison of v1 vs v2 in the MLflow UI. Did groundedness go from 74% to 91%? Did correctness improve? Did we regress on safety? All visible in the Evaluations tab, linked to the exact code that produced each result.

---

## Phase 8: Deploy Production Monitoring

**You:** v2 is deployed. You want automated quality checks running continuously on live traffic — not just when you remember to run `evaluate()`.

```python
from mlflow.genai.scorers import Safety, RetrievalGroundedness, Guidelines, ScorerSamplingConfig

mlflow.set_experiment(experiment_id=os.environ["MLFLOW_EXPERIMENT_ID"])

# Register and start scorers — these now run server-side on your live traces
safety = Safety().register(name="safety_prod")
safety = safety.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))  # check every trace

groundedness = RetrievalGroundedness().register(name="groundedness_prod")
groundedness = groundedness.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  # 50% sample

# A domain-specific rule you care about
language_check = Guidelines(
    name="english_only",
    guidelines=["The response must be in English"]
).register(name="language_prod")
language_check = language_check.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))
```

**Created:**

```
→ Scorer (registered) ×3   — server-side objects, each with a lifecycle state
   ├── safety_prod          sample_rate=1.0,  state=Active
   ├── groundedness_prod    sample_rate=0.5,  state=Active
   └── language_prod        sample_rate=1.0,  state=Active
```

**Lands in:** Registered in Databricks backend, scoped to the Experiment.

**What happens continuously without you doing anything:**

```
Live traffic → Trace created → Databricks monitoring service samples it
                                    → runs registered Scorers
                                    → Feedback[] attached to Trace
                                         (safety: YES, groundedness: YES/NO, language: YES/NO)
```

**Enables:**
- Quality trends visible in the MLflow UI over time (without running `evaluate()` manually)
- Noticing that groundedness degrades on Tuesdays (when new documents are ingested)
- `backfill_scorers()` to retroactively score last month's traces with your new `language_prod` scorer

> **The operational detail that bites people:** Scorers for production monitoring must have all imports *inside* the function body — they get serialized and run on Databricks Serverless. `import json` inside the function: fine. `from my_custom_lib import something` at the top: will fail to deserialize.

---

## The Complete Entity Flow, End-to-End

```
USER REQUEST
    │
    ▼
FastAPI /chat endpoint
    │
    ├──creates──► Trace + Spans   (lands: MLflow DB + artifact storage)
    │               │
    │               ├──async──► Production Scorers (registered) evaluate sample
    │               │               └──creates──► Feedback[] on Trace
    │               │
    │               └──via trace_id──► /feedback endpoint (user clicks 👍/👎)
    │                                       └──creates──► Feedback on Trace
    │
    │  (you, weekly)
    ▼
search_traces(filter="thumbs_down")
    │
    └──creates──► EvaluationDataset   (lands: UC Delta table)
                        │
                        ▼
                  labeling session ──► domain expert reviews in Review App
                        │                   └──creates──► Expectation on Trace
                        │
                  session.sync() ──► Expectations added to EvaluationDataset
                        │
                        ▼
               mlflow.genai.evaluate()
                        │
                        ├──creates──► EvaluationRun   (lands: MLflow Run storage)
                        │               ├── Trace[] (fresh, one per dataset row)
                        │               ├── Feedback[] (scorer outputs per trace)
                        │               └── AggregateMetrics
                        │
                        └──linked via model_id──► LoggedModel
                                                    (version snapshot, UC-governed)
```

---

## Entity Creation Cheatsheet

| Entity | Created by | Requires | Lands in |
|---|---|---|---|
| **Experiment** | You, manually (UI or SDK) | Nothing | MLflow backend |
| **Trace** | `@mlflow.trace` / autolog on each request | Experiment | MLflow DB (TraceInfo) + artifact store (TraceData) |
| **Span** | Same instrumentation as Trace | Trace (parent) | Inside TraceData (artifact store) |
| **Feedback** (user) | `mlflow.log_feedback()` on `/feedback` endpoint | trace_id | Attached to Trace in MLflow backend |
| **Feedback** (scorer) | `evaluate()` or prod monitoring service | Trace + Scorer | Attached to Trace in MLflow backend |
| **Expectation** | Domain expert via Review App, or `mlflow.log_expectation()` | Trace + LabelingSession | Attached to Trace in MLflow backend |
| **EvaluationDataset** | `create_dataset()` + `merge_records()` | UC schema with CREATE TABLE permission | Unity Catalog Delta table |
| **EvaluationRun** | `mlflow.genai.evaluate()` automatically | Experiment + EvaluationDataset | MLflow Run storage |
| **LabelingSchema** | `create_label_schema()` | Nothing | MLflow backend |
| **LabelingSession** | `create_labeling_session()` | Experiment + Traces to review | MLflow Run storage |
| **LoggedModel** | `create_external_model()` or `set_active_model()` | Experiment | MLflow entities storage |
| **Prompt** | `mlflow.genai.register_prompt()` | Nothing | Unity Catalog Prompt Registry |
| **Scorer (registered)** | `scorer.register()` → `scorer.start()` | Experiment + instrumented app | Databricks backend (serverless) |
