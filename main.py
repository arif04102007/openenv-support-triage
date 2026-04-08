"""
OpenEnv: Support Email Triage Environment
FastAPI server implementing the OpenEnv spec.
"""

import os
import uuid
import random
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local imports
import sys
sys.path.insert(0, os.path.dirname(__file__))
from data.emails import get_all_emails, get_email
from graders import grade_easy, grade_medium, grade_hard

# ─────────────────────────────────────────
# App setup
# ─────────────────────────────────────────

app = FastAPI(
    title="OpenEnv: Support Email Triage",
    description="An OpenEnv environment for customer support email triage tasks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────

class Observation(BaseModel):
    email_id: str
    subject: str
    body: str
    sender: str
    timestamp: str
    task_id: str
    instructions: str


class Action(BaseModel):
    response: str


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict


class StateResult(BaseModel):
    session_id: str
    current_task_id: str
    current_email_id: str
    steps_taken: int
    total_reward: float
    done: bool


class ResetResult(BaseModel):
    session_id: str
    observation: Observation


class TaskInfo(BaseModel):
    id: str
    name: str
    description: str
    difficulty: str


# ─────────────────────────────────────────
# Task definitions
# ─────────────────────────────────────────

TASKS = [
    TaskInfo(
        id="task_easy",
        name="Classify Email Urgency",
        description=(
            "Classify the urgency of the email as one of: low, medium, high, critical. "
            "Respond with ONLY the urgency level word."
        ),
        difficulty="easy",
    ),
    TaskInfo(
        id="task_medium",
        name="Categorize and Extract",
        description=(
            "Return a JSON object with three fields: "
            "\"category\" (one of: billing, technical, account, shipping, general), "
            "\"customer_name\" (the customer's full name), "
            "\"primary_complaint\" (one sentence describing the main issue)."
        ),
        difficulty="medium",
    ),
    TaskInfo(
        id="task_hard",
        name="Full Triage and Draft Response",
        description=(
            "Perform full triage and draft a professional support reply. "
            "Your response should: address the customer by name, acknowledge their issue, "
            "convey appropriate urgency, and outline next steps. Minimum 3 sentences."
        ),
        difficulty="hard",
    ),
]

TASK_IDS = [t.id for t in TASKS]

TASK_INSTRUCTIONS = {
    "task_easy": (
        "Your task: Classify the urgency of this support email.\n"
        "Valid values: low, medium, high, critical\n"
        "Respond with ONLY the urgency word, nothing else."
    ),
    "task_medium": (
        "Your task: Analyze this support email and return a JSON object with:\n"
        "  - \"category\": one of billing / technical / account / shipping / general\n"
        "  - \"customer_name\": the customer's full name\n"
        "  - \"primary_complaint\": one sentence summarizing the main issue\n"
        "Return ONLY valid JSON, no extra text."
    ),
    "task_hard": (
        "Your task: Perform complete email triage.\n"
        "1. Assess urgency (low/medium/high/critical)\n"
        "2. Identify category (billing/technical/account/shipping/general)\n"
        "3. Draft a professional, empathetic reply that addresses the customer by name, "
        "acknowledges their specific issue, and outlines next steps.\n"
        "Your full response should be the draft reply email."
    ),
}

# ─────────────────────────────────────────
# In-memory session store
# ─────────────────────────────────────────

sessions: dict = {}


def _build_observation(email: dict, task_id: str) -> Observation:
    return Observation(
        email_id=email["email_id"],
        subject=email["subject"],
        body=email["body"],
        sender=email["sender"],
        timestamp=email["timestamp"],
        task_id=task_id,
        instructions=TASK_INSTRUCTIONS[task_id],
    )


def _new_session(task_id: Optional[str] = None, email_id: Optional[str] = None) -> dict:
    emails = get_all_emails()
    email = get_email(email_id) if email_id else random.choice(emails)
    chosen_task = task_id if task_id in TASK_IDS else random.choice(TASK_IDS)
    return {
        "session_id": str(uuid.uuid4()),
        "email": email,
        "task_id": chosen_task,
        "steps_taken": 0,
        "total_reward": 0.0,
        "done": False,
    }


# ─────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "OpenEnv: Support Email Triage",
        "version": "1.0.0",
        "status": "ok",
        "tasks": TASK_IDS,
    }


@app.post("/reset", response_model=ResetResult)
def reset(task_id: Optional[str] = None, email_id: Optional[str] = None):
    """Start a new episode. Returns a session_id and the first observation."""
    session = _new_session(task_id=task_id, email_id=email_id)
    sessions[session["session_id"]] = session
    obs = _build_observation(session["email"], session["task_id"])
    return ResetResult(session_id=session["session_id"], observation=obs)


@app.post("/step", response_model=StepResult)
def step(session_id: str, action: Action):
    """Submit an action for the current session. Returns reward and next observation."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")

    session = sessions[session_id]

    if session["done"]:
        raise HTTPException(status_code=400, detail="Episode is done. Call /reset to start a new one.")

    email = session["email"]
    task_id = session["task_id"]
    ground_truth = email["ground_truth"]
    agent_response = action.response

    # Grade the action
    if task_id == "task_easy":
        reward = grade_easy(agent_response, ground_truth)
    elif task_id == "task_medium":
        reward = grade_medium(agent_response, ground_truth)
    elif task_id == "task_hard":
        reward = grade_hard(agent_response, ground_truth, email)
    else:
        reward = 0.0

    session["steps_taken"] += 1
    session["total_reward"] += reward
    session["done"] = True  # Each episode = 1 task attempt

    obs = _build_observation(email, task_id)

    return StepResult(
        observation=obs,
        reward=reward,
        done=True,
        info={
            "task_id": task_id,
            "email_id": email["email_id"],
            "ground_truth": ground_truth,
            "agent_response_preview": agent_response[:200],
        },
    )


@app.get("/state", response_model=StateResult)
def state(session_id: str):
    """Return the current state of a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    s = sessions[session_id]
    return StateResult(
        session_id=s["session_id"],
        current_task_id=s["task_id"],
        current_email_id=s["email"]["email_id"],
        steps_taken=s["steps_taken"],
        total_reward=s["total_reward"],
        done=s["done"],
    )


@app.get("/tasks")
def list_tasks():
    """List all available tasks."""
    return {"tasks": [t.dict() for t in TASKS]}


@app.get("/health")
def health():
    return {"status": "healthy"}
