from openai import OpenAI
import sys

client = OpenAI(
  base_url="https://api.featherless.ai/v1",
  api_key="rc_1095bc11f96bb0033f875fa4519e617739bd8928d89c5ac01f11480594adddbe",
)

candidates = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "google/gemma-2-9b-it"
]

print("Testing model candidates...")

for model in candidates:
    print(f"\nTrying: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        print(f"[SUCCESS] {model} is working!")
        print(f"Response: {response.choices[0].message.content}")
        # Write to success file to serve as signal
        with open("working_model.txt", "w") as f:
            f.write(model)
        sys.exit(0)
    except Exception as e:
        print(f"[FAIL] {model}: {e}")

print("\nNo working candidate found.")
sys.exit(1)
