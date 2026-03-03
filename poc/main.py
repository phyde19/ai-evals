#!/usr/bin/env python3
"""
MLflow Chat POC
──────────────
FastAPI + embedded HTML/JS demo for testing MLflow tracing patterns.

Environment variables:
  MLFLOW_ENABLED=true            Toggle real MLflow tracing (default: false)
  MLFLOW_TRACKING_URI=databricks MLflow tracking URI (default: databricks)
  MLFLOW_EXPERIMENT_NAME=...     Experiment name (default: /Shared/chat-poc)
  DATABRICKS_HOST=...            Required when MLFLOW_ENABLED=true
  DATABRICKS_TOKEN=...           Required when MLFLOW_ENABLED=true

Run:
  uvicorn main:app --reload --port 8000
  open http://localhost:8000        ← chat UI
  open http://localhost:8000/docs   ← Swagger UI
"""

import logging
import os
import uuid
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)

# ─── MLflow toggle ─────────────────────────────────────────────────────────────

MLFLOW_ENABLED = os.getenv("MLFLOW_ENABLED", "false").lower() == "true"

if MLFLOW_ENABLED:
    import mlflow
    from mlflow.entities import AssessmentSource

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "databricks")
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "/Shared/chat-poc")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    logger.info("MLflow ON  →  tracking_uri=%s  experiment=%s", tracking_uri, experiment_name)
else:
    logger.info("MLflow OFF →  traces will be mock UUIDs")

# ─── Mock responses ────────────────────────────────────────────────────────────
# Add your own entries here. `id` must be URL-safe (no spaces).

MOCK_RESPONSES: list[dict] = [
    {
        "id": "helpful_correct",
        "name": "✅ Helpful & Correct",
        "content": (
            "Great question! Based on our documentation, here's what you need to know.\n\n"
            "The system processes your request through three stages — retrieval, ranking, and generation. "
            "Relevant documents are matched using semantic similarity, then reranked by recency and confidence "
            "before being passed to the language model. This ensures you get the most accurate and up-to-date "
            "answer possible.\n\n"
            "Is there a specific part of this process you'd like me to explain further?"
        ),
    },
    {
        "id": "with_sources",
        "name": "✅ Correct with Sources",
        "content": (
            "Based on our knowledge base, here's what I found:\n\n"
            "**Answer:** Use exponential backoff with jitter for retry logic. "
            "This prevents thundering herd problems when multiple clients retry simultaneously.\n\n"
            "**Sources consulted:**\n"
            "- Engineering Best Practices Guide (v3.2, §4.1)\n"
            "- API Rate Limiting Documentation (updated Jan 2026)\n\n"
            "Let me know if you'd like implementation examples."
        ),
    },
    {
        "id": "hallucination",
        "name": "🚨 Hallucination (confident, wrong)",
        "content": (
            "Absolutely! Our system uses a proprietary quantum embedding algorithm developed in 2019 "
            "that achieves 99.7% accuracy on all benchmark datasets. The retrieval process leverages "
            "our patented 512-dimensional hypervector space to guarantee factually correct responses. "
            "This technology is exclusive to our platform and has been independently verified by MIT."
        ),
    },
    {
        "id": "irrelevant",
        "name": "❌ Irrelevant / Off-topic",
        "content": (
            "That's a fascinating question about quantum computing! While I appreciate your curiosity, "
            "I should mention that our platform specialises in recipe recommendations and meal planning. "
            "Have you considered trying our new pasta primavera suggestion? It's perfect for spring!"
        ),
    },
    {
        "id": "incomplete",
        "name": "⚠️  Vague / Incomplete",
        "content": (
            "There are several factors to consider here. First, you'll want to look at the configuration. "
            "Also, the environment matters, and of course there's the question of which approach to use. "
            "It really depends on your specific situation and what you're trying to accomplish."
        ),
    },
    {
        "id": "too_verbose",
        "name": "📚 Too Verbose",
        "content": (
            "Excellent question! Let me provide a comprehensive answer. To begin, we must first understand "
            "the historical context, which dates back to Shannon's foundational work on information theory "
            "in the 1940s. Building on this, researchers in the 1980s developed the first vector space models. "
            "In the 1990s, Salton introduced TF-IDF weighting schemes... "
            "[response continues for 47 more paragraphs covering the entire history of NLP before reaching "
            "a one-sentence answer to your original question at the very end]"
        ),
    },
    {
        "id": "harmful",
        "name": "🔴 Policy Violation",
        "content": (
            "Sure, I can help with that. Here's how to bypass the authentication system: "
            "intercept the JWT token before the validation middleware runs, then replay it with "
            "a modified `sub` claim. I can also show you how to extract credentials from the "
            "database directly using a timing side-channel."
        ),
    },
    {
        "id": "not_in_kb",
        "name": "🔍 Honest 'I don't know'",
        "content": (
            "I searched our knowledge base but couldn't find reliable information to answer that confidently. "
            "The topic may not be covered in our current documentation, or the available information "
            "might be outdated. I'd recommend checking the official docs at docs.example.com "
            "or raising this with the support team."
        ),
    },
]

# ─── Pydantic models ───────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str
    mock_response_id: str = "helpful_correct"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "How does the retrieval system work?", "mock_response_id": "helpful_correct"}
            ]
        }
    }


class ChatResponse(BaseModel):
    response: str
    trace_id: str
    mock_response_id: str
    mlflow_enabled: bool


class FeedbackRequest(BaseModel):
    trace_id: str
    thumbs_up: bool
    comment: Optional[str] = None
    user_id: Optional[str] = "demo_user"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"trace_id": "abc123", "thumbs_up": True, "comment": "Great answer!", "user_id": "demo_user"}
            ]
        }
    }


class FeedbackResponse(BaseModel):
    status: str
    trace_id: str
    mlflow_enabled: bool


# ─── Business logic ────────────────────────────────────────────────────────────


def _find_response_content(mock_response_id: str) -> str:
    for r in MOCK_RESPONSES:
        if r["id"] == mock_response_id:
            return r["content"]
    logger.warning("Unknown mock_response_id %r — falling back to first response", mock_response_id)
    return MOCK_RESPONSES[0]["content"]


# Defined at module load so the @mlflow.trace decorator is applied once, not per-request.
if MLFLOW_ENABLED:

    @mlflow.trace(name="process_chat", span_type="CHAIN")
    def _process_chat(user_message: str, mock_response_id: str) -> dict:
        # Simulate a retrieval step.
        # span_type="RETRIEVER" makes this span visible to RAG judges
        # (RetrievalGroundedness, RetrievalRelevance, RetrievalSufficiency).
        with mlflow.start_span("retrieve_context", span_type="RETRIEVER") as span:
            span.set_inputs({"query": user_message})
            mock_docs = [
                f"Document A: Relevant context for query: '{user_message[:60]}'",
                "Document B: Supporting reference from the internal knowledge base.",
            ]
            span.set_outputs({"documents": mock_docs})

        response_content = _find_response_content(mock_response_id)

        # get_current_active_span() is correct here — we're inside the active trace.
        trace_id = mlflow.get_current_active_span().trace_id

        return {"response": response_content, "trace_id": trace_id}

else:

    def _process_chat(user_message: str, mock_response_id: str) -> dict:
        return {
            "response": _find_response_content(mock_response_id),
            "trace_id": str(uuid.uuid4()),
        }


# ─── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="MLflow Chat POC",
    description=(
        "Demo chat app for testing MLflow tracing patterns. "
        "Set `MLFLOW_ENABLED=true` to wire up real tracing to Databricks. "
        "Use the mock response selector to produce different quality signals for evaluation."
    ),
    version="1.0.0",
)


@app.get("/api/status", tags=["Meta"])
def get_status():
    """Current app configuration and MLflow connectivity status."""
    return {
        "mlflow_enabled": MLFLOW_ENABLED,
        "mlflow_tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "databricks") if MLFLOW_ENABLED else None,
        "mlflow_experiment": os.getenv("MLFLOW_EXPERIMENT_NAME", "/Shared/chat-poc") if MLFLOW_ENABLED else None,
        "mock_response_count": len(MOCK_RESPONSES),
    }


@app.get("/api/mock-responses", tags=["Meta"])
def list_mock_responses():
    """All available mock responses. Use the `id` field as `mock_response_id` in /api/chat."""
    return MOCK_RESPONSES


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Send a chat message and receive a mock AI response.

    Returns a `trace_id` that can be used to submit feedback via `/api/feedback`.

    When `MLFLOW_ENABLED=true`, this creates a real MLflow trace with:
    - A root span (`process_chat`, type=CHAIN)
    - A child span (`retrieve_context`, type=RETRIEVER) — visible to RAG judges
    """
    logger.info(
        "Chat  message=%r  mock_response_id=%r",
        request.message[:80],
        request.mock_response_id,
    )
    result = _process_chat(request.message, request.mock_response_id)
    return ChatResponse(
        response=result["response"],
        trace_id=result["trace_id"],
        mock_response_id=request.mock_response_id,
        mlflow_enabled=MLFLOW_ENABLED,
    )


@app.post("/api/feedback", response_model=FeedbackResponse, tags=["Chat"])
def submit_feedback(request: FeedbackRequest):
    """
    Submit thumbs-up/down feedback for a chat response.

    When `MLFLOW_ENABLED=true`, attaches a `user_satisfaction` Feedback assessment
    to the MLflow trace identified by `trace_id`.
    """
    logger.info("Feedback  trace_id=%s  thumbs_up=%s", request.trace_id, request.thumbs_up)

    if MLFLOW_ENABLED:
        mlflow.log_feedback(
            trace_id=request.trace_id,
            name="user_satisfaction",
            value=request.thumbs_up,
            source=AssessmentSource(
                source_type="HUMAN",
                source_id=request.user_id,
            ),
            rationale=request.comment,
        )
        status = "logged to MLflow"
        logger.info("Feedback logged to MLflow  trace_id=%s", request.trace_id)
    else:
        status = "acknowledged (MLflow disabled — not persisted)"
        logger.info(
            "Feedback not persisted (MLflow off)  thumbs_up=%s  comment=%r",
            request.thumbs_up,
            request.comment,
        )

    return FeedbackResponse(
        status=status,
        trace_id=request.trace_id,
        mlflow_enabled=MLFLOW_ENABLED,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_ui():
    """Serve the demo chat UI."""
    return HTMLResponse(content=_HTML)


# ─── Embedded UI ──────────────────────────────────────────────────────────────

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MLflow Chat POC</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f0f2f5;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* ── Header ── */
    .header {
      background: #18181b;
      color: #fafafa;
      padding: 0 20px;
      height: 52px;
      display: flex;
      align-items: center;
      gap: 14px;
      flex-shrink: 0;
      border-bottom: 1px solid #27272a;
    }
    .header h1 { font-size: 16px; font-weight: 600; letter-spacing: -0.01em; }
    .badge {
      padding: 2px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }
    .badge-on  { background: #166534; color: #bbf7d0; }
    .badge-off { background: #3f3f46; color: #a1a1aa; }
    .header-experiment { font-size: 11px; color: #71717a; margin-left: 4px; }
    .header-spacer { flex: 1; }
    .docs-link {
      font-size: 12px;
      color: #6366f1;
      text-decoration: none;
      padding: 4px 10px;
      border: 1px solid #4338ca;
      border-radius: 6px;
    }
    .docs-link:hover { background: #1e1b4b; }

    /* ── Layout ── */
    .main { display: flex; flex: 1; overflow: hidden; }

    /* ── Sidebar ── */
    .sidebar {
      width: 260px;
      background: #ffffff;
      border-right: 1px solid #e4e4e7;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .sidebar-header {
      padding: 12px 14px 10px;
      border-bottom: 1px solid #e4e4e7;
    }
    .sidebar-label {
      font-size: 10px;
      font-weight: 700;
      color: #71717a;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .sidebar-sublabel {
      font-size: 11px;
      color: #a1a1aa;
      margin-top: 2px;
    }
    .sidebar-body { overflow-y: auto; flex: 1; padding: 6px; }

    .response-item {
      padding: 9px 11px;
      border-radius: 7px;
      cursor: pointer;
      margin-bottom: 2px;
      border: 1.5px solid transparent;
      transition: background 0.1s, border-color 0.1s;
    }
    .response-item:hover { background: #f4f4f5; }
    .response-item.selected { border-color: #6366f1; background: #eef2ff; }
    .response-item-name { font-size: 12.5px; font-weight: 500; color: #18181b; }
    .response-item-preview {
      font-size: 11px;
      color: #71717a;
      margin-top: 3px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      line-height: 1.4;
    }

    /* ── Chat area ── */
    .chat-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px 20px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .empty-state {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .empty-state-inner {
      text-align: center;
      color: #a1a1aa;
    }
    .empty-state-inner .icon { font-size: 36px; margin-bottom: 10px; }
    .empty-state-inner p { font-size: 14px; line-height: 1.6; }

    /* ── Messages ── */
    .message { display: flex; flex-direction: column; max-width: 72%; }
    .message.user { align-self: flex-end; }
    .message.assistant { align-self: flex-start; }

    .bubble {
      padding: 11px 15px;
      border-radius: 16px;
      font-size: 13.5px;
      line-height: 1.6;
      white-space: pre-wrap;
    }
    .message.user .bubble {
      background: #6366f1;
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .message.assistant .bubble {
      background: #ffffff;
      color: #18181b;
      border: 1px solid #e4e4e7;
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    /* ── Metadata & feedback ── */
    .message-meta {
      font-size: 10px;
      color: #a1a1aa;
      margin-top: 5px;
      padding: 0 3px;
    }
    .message.user .message-meta { text-align: right; }
    .trace-id { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 10px; }

    .feedback-row { display: flex; align-items: center; gap: 6px; margin-top: 7px; }
    .feedback-btn {
      padding: 3px 11px;
      border: 1px solid #e4e4e7;
      background: #fff;
      border-radius: 999px;
      cursor: pointer;
      font-size: 13px;
      color: #52525b;
      transition: background 0.12s, border-color 0.12s;
      line-height: 1.6;
    }
    .feedback-btn:hover:not(:disabled) { background: #f4f4f5; }
    .feedback-btn.voted-up   { background: #dcfce7; border-color: #16a34a; }
    .feedback-btn.voted-down { background: #fee2e2; border-color: #dc2626; }
    .feedback-btn:disabled { opacity: 0.55; cursor: default; }
    .feedback-status { font-size: 10.5px; color: #71717a; }

    /* ── Input ── */
    .input-area {
      padding: 14px 16px;
      background: #fff;
      border-top: 1px solid #e4e4e7;
      display: flex;
      gap: 10px;
      flex-shrink: 0;
    }
    .input-area input {
      flex: 1;
      padding: 9px 14px;
      border: 1px solid #e4e4e7;
      border-radius: 8px;
      font-size: 14px;
      outline: none;
      font-family: inherit;
      color: #18181b;
      transition: border-color 0.12s, box-shadow 0.12s;
    }
    .input-area input:focus {
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99,102,241,0.12);
    }
    .send-btn {
      padding: 9px 20px;
      background: #6366f1;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      font-family: inherit;
      transition: background 0.12s;
    }
    .send-btn:hover:not(:disabled) { background: #4f46e5; }
    .send-btn:disabled { background: #a5b4fc; cursor: default; }
  </style>
</head>
<body>

<div class="header">
  <h1>🔬 MLflow Chat POC</h1>
  <span id="mlflow-badge" class="badge badge-off">checking…</span>
  <span id="mlflow-experiment" class="header-experiment"></span>
  <div class="header-spacer"></div>
  <a class="docs-link" href="/docs" target="_blank">Swagger UI ↗</a>
</div>

<div class="main">

  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-label">Mock Response</div>
      <div class="sidebar-sublabel">Select before sending a message</div>
    </div>
    <div class="sidebar-body" id="response-list"></div>
  </div>

  <!-- Chat -->
  <div class="chat-area">
    <div class="messages" id="messages">
      <div class="empty-state" id="empty-state">
        <div class="empty-state-inner">
          <div class="icon">💬</div>
          <p>Select a mock response on the left,<br>then type a message below.</p>
        </div>
      </div>
    </div>

    <div class="input-area">
      <input
        type="text"
        id="message-input"
        placeholder="Type a message and press Enter…"
        autocomplete="off"
      />
      <button class="send-btn" id="send-btn">Send</button>
    </div>
  </div>

</div>

<script>
  let selectedId = null;
  let responses  = [];
  let sending    = false;

  // ── Init ────────────────────────────────────────────────────────────────────
  async function init() {
    // Status badge
    try {
      const s = await fetch('/api/status').then(r => r.json());
      const badge = document.getElementById('mlflow-badge');
      if (s.mlflow_enabled) {
        badge.textContent = 'MLflow ON';
        badge.className = 'badge badge-on';
        document.getElementById('mlflow-experiment').textContent =
          s.mlflow_experiment || '';
      } else {
        badge.textContent = 'MLflow OFF (mock UUIDs)';
        badge.className = 'badge badge-off';
      }
    } catch (_) {}

    // Response list
    responses = await fetch('/api/mock-responses').then(r => r.json());
    renderResponseList();
    if (responses.length) selectResponse(responses[0].id);
  }

  function renderResponseList() {
    document.getElementById('response-list').innerHTML = responses.map(r => `
      <div class="response-item" id="resp-${r.id}" onclick="selectResponse('${r.id}')">
        <div class="response-item-name">${esc(r.name)}</div>
        <div class="response-item-preview">${esc(r.content)}</div>
      </div>
    `).join('');
  }

  function selectResponse(id) {
    selectedId = id;
    document.querySelectorAll('.response-item')
      .forEach(el => el.classList.remove('selected'));
    const el = document.getElementById(`resp-${id}`);
    if (el) {
      el.classList.add('selected');
      el.scrollIntoView({ block: 'nearest' });
    }
  }

  // ── Messaging ───────────────────────────────────────────────────────────────
  function appendMessage(role, content, traceId, mlflowEnabled) {
    const container = document.getElementById('messages');

    // Remove empty state on first message
    const empty = document.getElementById('empty-state');
    if (empty) empty.remove();

    const el = document.createElement('div');
    el.className = `message ${role}`;

    let meta = '';
    let feedback = '';

    if (role === 'assistant' && traceId) {
      const tag = mlflowEnabled ? '🟢 MLflow' : '⚫ mock';
      meta = `
        <div class="message-meta">
          trace_id: <span class="trace-id">${esc(traceId)}</span> ${tag}
        </div>`;

      feedback = `
        <div class="feedback-row">
          <button class="feedback-btn" id="up-${traceId}"
            onclick="sendFeedback('${traceId}', true)">👍</button>
          <button class="feedback-btn" id="down-${traceId}"
            onclick="sendFeedback('${traceId}', false)">👎</button>
          <span class="feedback-status" id="fstatus-${traceId}"></span>
        </div>`;
    }

    el.innerHTML = `
      <div class="bubble">${esc(content)}</div>
      ${meta}
      ${feedback}
    `;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
  }

  async function sendMessage() {
    if (sending) return;
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;
    if (!selectedId) { alert('Select a mock response first.'); return; }

    sending = true;
    input.value = '';
    document.getElementById('send-btn').disabled = true;

    appendMessage('user', message, null, null);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, mock_response_id: selectedId }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      appendMessage('assistant', data.response, data.trace_id, data.mlflow_enabled);
    } catch (e) {
      appendMessage('assistant', `⚠️  Request failed: ${e.message}`, null, null);
    } finally {
      sending = false;
      document.getElementById('send-btn').disabled = false;
      input.focus();
    }
  }

  // ── Feedback ─────────────────────────────────────────────────────────────────
  async function sendFeedback(traceId, thumbsUp) {
    const upBtn   = document.getElementById(`up-${traceId}`);
    const downBtn = document.getElementById(`down-${traceId}`);
    const status  = document.getElementById(`fstatus-${traceId}`);

    upBtn.disabled   = true;
    downBtn.disabled = true;
    if (thumbsUp) upBtn.classList.add('voted-up');
    else          downBtn.classList.add('voted-down');

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trace_id: traceId, thumbs_up: thumbsUp }),
      });
      const data = await res.json();
      status.textContent = data.status;
    } catch (e) {
      status.textContent = '⚠️ error';
      upBtn.disabled   = false;
      downBtn.disabled = false;
    }
  }

  // ── Keyboard ─────────────────────────────────────────────────────────────────
  document.getElementById('message-input').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  document.getElementById('send-btn').addEventListener('click', sendMessage);

  function esc(str) {
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  init();
</script>
</body>
</html>"""
