# test_ollama_connection.py

import ollama

response = ollama.chat(
    model='llama3.2',  # Use 'llama3' or 'llama3.2' depending on what you're running
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print("\n=== Ollama LLM Response ===")
print(response['message']['content'])