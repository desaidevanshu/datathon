from openai import OpenAI
import os

client = OpenAI(
  base_url="https://api.featherless.ai/v1",
  api_key="rc_1095bc11f96bb0033f875fa4519e617739bd8928d89c5ac01f11480594adddbe",
)

print("Fetching available models...")
try:
    models = client.models.list()
    full_list = [m.id for m in models.data]
    print(f"Total models available: {len(full_list)}")
    
    # Search patterns
    patterns = ["Llama-3.1", "Llama-3", "Mistral-7B"]
    
    print("\n--- MATCHING MODELS ---")
    found_any = False
    for p in patterns:
        matches = [m for m in full_list if p in m]
        if matches:
            found_any = True
            print(f"\nPattern '{p}':")
            for m in matches:
                print(f"  > {m}")
        else:
            print(f"\nPattern '{p}': NO MATCHES")

    if not found_any:
        print("\nFallback: First 20 models:")
        for m in full_list[:20]:
            print(f" - {m}")
            
except Exception as e:
    print(f"Error fetching models: {e}")
