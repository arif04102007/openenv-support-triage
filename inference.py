import os
import json
import time
import requests
from openai import OpenAI

# Required Environment Variables
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME")
HF_TOKEN = os.environ.get("HF_TOKEN")
ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

if not all([API_BASE_URL, MODEL_NAME, HF_TOKEN]):
    raise ValueError("Missing API_BASE_URL, MODEL_NAME, or HF_TOKEN in environment.")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

TASK_IDS = ["task_easy", "task_medium", "task_hard"]
EMAIL_IDS = ["E001", "E002", "E003", "E004", "E005", "E006", "E007", "E008"]

def run_inference():
    total_score = 0.0
    num_episodes = 0
    print("[START]") # Mandatory Start Tag

    for task_id in TASK_IDS:
        for email_id in EMAIL_IDS:
            try:
                # Reset
                resp = requests.post(f"{ENV_BASE_URL}/reset", params={"task_id": task_id, "email_id": email_id}, timeout=30)
                data = resp.json()
                session_id, obs = data["session_id"], data["observation"]

                # LLM Call
                prompt = f"TASK: {obs['instructions']}\n\nEMAIL: {obs['body']}"
                completion = client.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=[{"role": "user", "content": prompt}]
                )
                agent_res = completion.choices[0].message.content.strip()

                # Step
                step_resp = requests.post(f"{ENV_BASE_URL}/step", params={"session_id": session_id}, json={"response": agent_res})
                reward = step_resp.json()["reward"]

                total_score += reward
                num_episodes += 1

                # Mandatory Structured Step Log
                print(f"[STEP] {json.dumps({'task_id': task_id, 'email_id': email_id, 'reward': round(reward, 4), 'done': True})}")
                time.sleep(0.2)
            except Exception as e:
                print(f"[STEP] {json.dumps({'task_id': task_id, 'reward': 0.0, 'error': str(e)})}")

    avg = total_score / num_episodes if num_episodes > 0 else 0.0
    print(f"[END] {json.dumps({'overall_score': round(avg, 4), 'total_episodes': num_episodes})}")

if __name__ == "__main__":
    run_inference()