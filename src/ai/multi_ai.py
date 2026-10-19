"""
Multi-AI Provider System
Uses multiple free AI providers for maximum reliability and quality.
Falls back automatically if one provider fails.
"""
import os
import json
import random
from typing import Optional, Dict, Any

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_best_gemini_model, get_best_groq_model
except ImportError:
    def get_best_gemini_model(api_key=None):
        return "gemini-2.5-flash"
    def get_best_groq_model(api_key=None):
        return "llama-3.3-70b-versatile"


class MultiAIGenerator:
    """
    Uses multiple free AI providers with automatic fallback:
    1. Groq (Llama) - Fast, 30 req/min
    2. Google Gemini - High quality, 60 req/min
    3. Together AI - Backup, 100 req/day
    4. HuggingFace - Backup, rate limited
    5. Cloudflare Workers AI - Backup, 10k req/day
    """
    
    def __init__(self):
        self.providers = []
        self._init_groq()
        self._init_gemini()
        self._init_together()
        self._init_cloudflare()
    
    def _init_groq(self):
        """Initialize Groq (primary provider)"""
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            try:
                from groq import Groq
                self.providers.append({
                    "name": "Groq",
                    "client": Groq(api_key=api_key),
                    "type": "groq",
                    "model": "llama-3.1-8b-instant",
                    "priority": 1
                })
                print("✅ Groq initialized (Primary)")
            except Exception as e:
                print(f"⚠️ Groq init failed: {e}")
    
    def _init_gemini(self):
        """Initialize Google Gemini (high quality) - DYNAMIC model selection"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                # DYNAMIC MODEL SELECTION - no hardcoded model names
                model_name = get_best_gemini_model(api_key)
                model = genai.GenerativeModel(model_name)
                self.providers.append({
                    "name": f"Gemini ({model_name})",
                    "client": model,
                    "type": "gemini",
                    "model": model_name,
                    "priority": 2
                })
                print(f"[OK] Gemini initialized ({model_name})")
            except Exception as e:
                print(f"[!] Gemini init failed: {e}")
    
    def _init_together(self):
        """Initialize Together AI (backup)"""
        api_key = os.environ.get("TOGETHER_API_KEY")
        if api_key:
            try:
                import together
                together.api_key = api_key
                self.providers.append({
                    "name": "Together",
                    "client": together,
                    "type": "together",
                    "model": "meta-llama/Llama-3-8b-chat-hf",
                    "priority": 3
                })
                print("✅ Together AI initialized (Backup)")
            except Exception as e:
                print(f"⚠️ Together init failed: {e}")
    
    def _init_cloudflare(self):
        """Initialize Cloudflare Workers AI (backup)"""
        account_id = os.environ.get("CF_ACCOUNT_ID")
        api_token = os.environ.get("CF_API_TOKEN")
        if account_id and api_token:
            self.providers.append({
                "name": "Cloudflare",
                "account_id": account_id,
                "api_token": api_token,
                "type": "cloudflare",
                "model": "@cf/meta/llama-3-8b-instruct",
                "priority": 4
            })
            print("✅ Cloudflare Workers AI initialized (Backup)")
    
    def generate(self, prompt: str, system: str = None) -> Optional[str]:
        """Generate text using available providers with fallback"""
        # Sort by priority
        sorted_providers = sorted(self.providers, key=lambda x: x["priority"])
        
        for provider in sorted_providers:
            try:
                result = self._call_provider(provider, prompt, system)
                if result:
                    print(f"✅ Generated with {provider['name']}")
                    return result
            except Exception as e:
                print(f"⚠️ {provider['name']} failed: {e}")
                continue
        
        print("❌ All providers failed")
        return None
    
    def _call_provider(self, provider: Dict, prompt: str, system: str) -> Optional[str]:
        """Call a specific provider"""
        if provider["type"] == "groq":
            return self._call_groq(provider, prompt, system)
        elif provider["type"] == "gemini":
            return self._call_gemini(provider, prompt, system)
        elif provider["type"] == "gemini_new":
            return self._call_gemini_new(provider, prompt, system)
        elif provider["type"] == "together":
            return self._call_together(provider, prompt, system)
        elif provider["type"] == "cloudflare":
            return self._call_cloudflare(provider, prompt, system)
        return None
    
    def _call_gemini_new(self, provider: Dict, prompt: str, system: str) -> str:
        """Call new Google Gemini API"""
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = provider["client"].models.generate_content(
            model=provider["model"],
            contents=full_prompt
        )
        return response.text
    
    def _call_groq(self, provider: Dict, prompt: str, system: str) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = provider["client"].chat.completions.create(
            model=provider["model"],
            messages=messages,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, provider: Dict, prompt: str, system: str) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = provider["client"].generate_content(full_prompt)
        return response.text
    
    def _call_together(self, provider: Dict, prompt: str, system: str) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = provider["client"].Complete.create(
            model=provider["model"],
            messages=messages
        )
        return response["choices"][0]["message"]["content"]
    
    def _call_cloudflare(self, provider: Dict, prompt: str, system: str) -> str:
        import requests
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{provider['account_id']}/ai/run/{provider['model']}"
        headers = {"Authorization": f"Bearer {provider['api_token']}"}
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(url, headers=headers, json={"messages": messages})
        return response.json()["result"]["response"]
    
    def generate_wyr_question(self) -> Dict[str, Any]:
        """Generate a Would You Rather question using best available AI"""
        system = """You are an expert at creating viral "Would You Rather" questions.
Return ONLY valid JSON with NO markdown: {"option_a": "...", "option_b": "...", "percentage_a": X}
Where X is 1-99."""

        prompt = """Generate a creative, engaging "Would You Rather" question.
Make it thought-provoking, funny, or controversial (but appropriate).
Examples of good questions:
- Financial vs lifestyle tradeoffs
- Superpowers vs everyday conveniences
- Embarrassing vs uncomfortable situations"""
        
        try:
            result = self.generate(prompt, system)
            if result:
                # Clean up response (remove markdown if present)
                clean = result.strip()
                if clean.startswith("```"):
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                return json.loads(clean)
        except Exception as e:
            print(f"❌ Parse error: {e}")
        
        # Fallback question
        return {
            "option_a": "Have unlimited money but no friends",
            "option_b": "Have amazing friends but always struggle financially",
            "percentage_a": 35
        }


# Singleton instance
_generator = None

def get_generator() -> MultiAIGenerator:
    global _generator
    if _generator is None:
        _generator = MultiAIGenerator()
    return _generator


if __name__ == "__main__":
    gen = MultiAIGenerator()
    question = gen.generate_wyr_question()
    print(f"Generated question: {json.dumps(question, indent=2)}")



