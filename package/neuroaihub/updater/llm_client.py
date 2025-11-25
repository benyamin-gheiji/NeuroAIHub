from openai import OpenAI
import json
import time

class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

        try:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.validate_connection()
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize LLM client: {e}")
        
    def validate_connection(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            print(f"✅ Connected to LLM model: {self.model}")
        except Exception as e:
            raise RuntimeError(f"⚠️ LLM connection test failed: {e}")

    def generate(self, prompt: str, temperature: float = 0.0, max_retries: int = 3) -> str:
        """Generate plain text completion with retry logic."""
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful and precise AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=5000
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"⚠️ LLM request failed (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(2 * attempt)
                else:
                    raise RuntimeError(f"LLM request failed after {max_retries} attempts: {e}")

    def generate_json( self, system_prompt: str = "", user_prompt: str = "", schema_hint: dict = None, temperature: float = 0.0, 
                      max_retries: int = 3, max_tokens: int = 5000) -> dict:
        for attempt in range(1, max_retries + 1):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                if user_prompt:
                    messages.append({"role": "user", "content": user_prompt})

                if schema_hint:
                    messages.append({
                        "role": "user",
                        "content": f"Return ONLY valid JSON matching this schema: {json.dumps(schema_hint)}"
                    })

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                output = response.choices[0].message.content.strip()
                output_clean = output.replace("```json", "").replace("```", "").strip()

                try:
                    return json.loads(output_clean)
                except json.JSONDecodeError:
                    print("⚠️ LLM returned invalid JSON")

            except Exception as e:
                print(f"⚠️ JSON generation failed (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(2 * attempt)
                else:
                    return {"error": f"Failed after {max_retries} attempts", "raw": output_clean if 'output_clean' in locals() else ""}