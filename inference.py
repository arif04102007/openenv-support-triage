"""
inference.py — Baseline inference script for OpenEnv: Support Email Triage
Must be run from the project root.

Usage:
    python inference.py

Environment variables required:
    API_BASE_URL   - The LLM API endpoint (OpenAI-compatible)
    MODEL_NAME     - The model identifier
    HF_TOKEN       - Hugging Face / API key
"""

import os
import json
import time
import requests
from openai import OpenAI

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is required.")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

TASK_IDS = ["task_easy", "task_medium", "task_hard"]
EMAIL_IDS = ["E001", "E002", "E003", "E004", "E005", "E006", "E007", "E008"]

# ─────────────────────────────────────────
# Helper: call the environment
# ─────────────────────────────────────────

def env_reset(task_id: str, email_id: str) -> dict:
    resp = requests.post(
        f"{ENV_BASE_URL}/reset",
        params={"task_id": task_id, "email_id": email_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(session_id: str, response: str) -> dict:
    resp = requests.post(
        f"{ENV_BASE_URL}/step",
        params={"session_id": session_id},
        json={"response": response},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ─────────────────────────────────────────
# Helper: call the LLM
# ─────────────────────────────────────────

def call_llm(system_prompt: str, user_message: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=512,
        temperature=0.2,
    )
    return completion.choices[0].message.content.strip()


# ─────────────────────────────────────────
# Main inference loop
# ─────────────────────────────────────────

def run_inference():
    results = []
    total_score = 0.0
    num_episodes = 0

    print(f"\n{'='*60}")
    print("OpenEnv: Support Email Triage — Baseline Inference")
    print(f"Model: {MODEL_NAME}")
    print(f"{'='*60}\n")

    for task_id in TASK_IDS:
        task_scores = []
        print(f"\n[TASK] {task_id.upper()}")
        print("-" * 40)

        for email_id in EMAIL_IDS:
            try:
                # Reset episode
                reset_data = env_reset(task_id=task_id, email_id=email_id)
                session_id = reset_data["session_id"]
                obs = reset_data["observation"]

                # Build prompt
                system_prompt = (
                    "You are a helpful customer support AI assistant. "
                    "Follow the instructions exactly as given."
                )
                user_message = (
                    f"INSTRUCTIONS:\n{obs['instructions']}\n\n"
                    f"EMAIL FROM: {obs['sender']}\n"
                    f"SUBJECT: {obs['subject']}\n\n"
                    f"BODY:\n{obs['body']}"
                )

                # Get LLM response
                agent_response = call_llm(system_prompt, user_message)

                # Step environment
                step_data = env_step(session_id=session_id, response=agent_response)
                reward = step_data["reward"]

                task_scores.append(reward)
                total_score += reward
                num_episodes += 1

                print(f"  Email {email_id}: score={reward:.4f}")
                results.append({
                    "task_id": task_id,
                    "email_id": email_id,
                    "score": reward,
                    "agent_response": agent_response[:300],
                })

                time.sleep(0.5)  # be kind to the API

            except Exception as e:
                print(f"  Email {email_id}: ERROR — {e}")
                results.append({
                    "task_id": task_id,
                    "email_id": email_id,
                    "score": 0.0,
                    "error": str(e),
                })

        avg = sum(task_scores) / len(task_scores) if task_scores else 0.0
        print(f"  → Task average: {avg:.4f}")

    # ─── Summary ───
    overall_avg = total_score / num_episodes if num_episodes > 0 else 0.0
    print(f"\n{'='*60}")
    print(f"OVERALL AVERAGE SCORE: {overall_avg:.4f}")
    print(f"Total episodes run: {num_episodes}")
    print(f"{'='*60}\n")

    # Save results
    with open("inference_results.json", "w") as f:
        json.dump(
            {
                "model": MODEL_NAME,
                "overall_avg": overall_avg,
                "num_episodes": num_episodes,
                "results": results,
            },
            f,
            indent=2,
        )
    print("Results saved to inference_results.json")
    return overall_avg


if __name__ == "__main__":
    run_inference()
