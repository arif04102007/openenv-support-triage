# 📧 OpenEnv: Support Email Triage

**Team:** AI Avengers  
**OpenEnv Hackathon — Round 1**

---

## Overview

An OpenEnv environment that simulates a real-world **Tier-1 customer support** workflow.
An AI agent receives customer emails and must triage them across three tasks of increasing difficulty.

---

## Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| `task_easy` | Easy | Classify email urgency: `low / medium / high / critical` |
| `task_medium` | Medium | Extract category, customer name, and primary complaint as JSON |
| `task_hard` | Hard | Full triage + draft a professional reply email |

All tasks score between **0.0 and 1.0** with partial credit.

---

## Observation Space

```json
{
  "email_id": "E001",
  "subject": "URGENT: Cannot access my account",
  "body": "Full email body text...",
  "sender": "john.smith@example.com",
  "timestamp": "2024-03-15T09:23:00Z",
  "task_id": "task_easy",
  "instructions": "Classify the urgency..."
}
```

## Action Space

```json
{
  "response": "Agent's answer string"
}
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check + task list |
| `POST` | `/reset?task_id=&email_id=` | Start new episode |
| `POST` | `/step?session_id=` | Submit action, get reward |
| `GET` | `/state?session_id=` | Get current session state |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/health` | Health check |

---

## Reward Function

**Easy:** Full credit (1.0) for exact urgency match. Partial (0.4) for 1 level off.

**Medium:** Average of 3 sub-scores:
- Category classification (0 or 1)
- Customer name extraction (0, 0.5, or 1)
- Complaint keyword overlap (0–1)

**Hard:** Average of 5 sub-scores:
- Urgency mentioned in response (0 or 0.5)
- Issue category addressed (0 or 1)
- Customer name used (0 or 1)
- Empathy/professionalism keywords (0–1)
- Issue keyword coverage (0–1)

---

## Setup & Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 7860

# In a separate terminal, run inference
export HF_TOKEN=your_token_here
export API_BASE_URL=https://api-inference.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export ENV_BASE_URL=http://localhost:7860
python inference.py
```

## Docker

```bash
docker build -t openenv-support-triage .
docker run -p 7860:7860 openenv-support-triage
```

---

## Dataset

8 curated support emails spanning all categories:
- **Categories:** billing, technical, account, shipping, general
- **Urgency levels:** low, medium, high, critical
- All emails have ground truth labels for objective grading

---

## Environment Variables (inference.py)

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | OpenAI-compatible LLM endpoint |
| `MODEL_NAME` | Model identifier (e.g., `Qwen/Qwen2.5-72B-Instruct`) |
| `HF_TOKEN` | Hugging Face API key |
| `ENV_BASE_URL` | URL where the FastAPI server is running |
