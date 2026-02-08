from openai import OpenAI

# User's provided snippet
print("Connecting to Featherless AI...")
try:
    client = OpenAI(
      base_url="https://api.featherless.ai/v1",
      api_key="rc_1095bc11f96bb0033f875fa4519e617739bd8928d89c5ac01f11480594adddbe",
    )

    response = client.chat.completions.create(
      model='meta-llama/Llama-3.1-8B-Instruct',
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
      ],
    )
    print("\n[SUCCESS] Response received:")
    print(response.model_dump()['choices'][0]['message']['content'])
except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
