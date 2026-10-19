#!/usr/bin/env python3
"""
Test All AI Model Discovery Methods
====================================

Tests that all 4 providers can dynamically discover their models.

Provider        Discovery Method             Fallback Only If
--------        ----------------             ----------------
Gemini          genai.list_models()          API fails
Groq            client.models.list()         API fails
HuggingFace     huggingface.co/api/models    API fails
OpenRouter      /api/v1/models               API fails
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gemini_discovery():
    """Test Gemini model discovery using genai.list_models()"""
    print("\n" + "="*60)
    print("TESTING: Gemini Model Discovery")
    print("Method: genai.list_models()")
    print("="*60)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] GEMINI_API_KEY not set - will use fallback")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        models = genai.list_models()
        print("\n[+] Discovery SUCCESS! Available Gemini models:")
        
        count = 0
        for model in models:
            model_name = model.name.replace("models/", "")
            methods = getattr(model, "supported_generation_methods", [])
            if "generateContent" in methods:
                tier = "FLASH" if "flash" in model_name.lower() else "PRO" if "pro" in model_name.lower() else "OTHER"
                print(f"    - {model_name} [{tier}]")
                count += 1
        
        print(f"\n[+] Total generative models found: {count}")
        return True
        
    except Exception as e:
        print(f"[X] Discovery FAILED: {e}")
        return False


def test_groq_discovery():
    """Test Groq model discovery using client.models.list()"""
    print("\n" + "="*60)
    print("TESTING: Groq Model Discovery")
    print("Method: client.models.list()")
    print("="*60)
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[!] GROQ_API_KEY not set - will use fallback")
        return False
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        models_response = client.models.list()
        print("\n[+] Discovery SUCCESS! Available Groq models:")
        
        count = 0
        for model in models_response.data:
            model_id = model.id
            tier = "70B" if "70b" in model_id.lower() else "8B" if "8b" in model_id.lower() else "OTHER"
            print(f"    - {model_id} [{tier}]")
            count += 1
        
        print(f"\n[+] Total models found: {count}")
        return True
        
    except Exception as e:
        print(f"[X] Discovery FAILED: {e}")
        return False


def test_huggingface_discovery():
    """Test HuggingFace model discovery using the API"""
    print("\n" + "="*60)
    print("TESTING: HuggingFace Model Discovery")
    print("Method: huggingface.co/api/models")
    print("="*60)
    
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        print("[!] HUGGINGFACE_API_KEY not set - will use fallback")
        return False
    
    try:
        import requests
        
        response = requests.get(
            "https://huggingface.co/api/models",
            params={
                "pipeline_tag": "text-generation",
                "sort": "downloads",
                "direction": -1,
                "limit": 50,
                "filter": "conversational"
            },
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15
        )
        
        if response.status_code == 200:
            models_data = response.json()
            print("\n[+] Discovery SUCCESS! Top instruction-tuned models:")
            
            count = 0
            for model in models_data[:20]:  # Show top 20
                model_id = model.get("modelId", "")
                downloads = model.get("downloads", 0)
                is_instruct = any(kw in model_id.lower() for kw in ["instruct", "chat", "-it"])
                if is_instruct:
                    print(f"    - {model_id} [{downloads:,} downloads]")
                    count += 1
            
            print(f"\n[+] Total instruction-tuned models in top 50: {count}")
            return True
        else:
            print(f"[X] API returned status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"[X] Discovery FAILED: {e}")
        return False


def test_openrouter_discovery():
    """Test OpenRouter model discovery using /api/v1/models"""
    print("\n" + "="*60)
    print("TESTING: OpenRouter Model Discovery")
    print("Method: /api/v1/models")
    print("="*60)
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[!] OPENROUTER_API_KEY not set - will use fallback")
        return False
    
    try:
        import requests
        
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            print("\n[+] Discovery SUCCESS! Free models found:")
            
            free_count = 0
            for model in models_data:
                model_id = model.get("id", "")
                if ":free" in model_id.lower():
                    print(f"    - {model_id}")
                    free_count += 1
            
            print(f"\n[+] Total free models: {free_count}")
            print(f"[+] Total all models: {len(models_data)}")
            return True
        else:
            print(f"[X] API returned status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"[X] Discovery FAILED: {e}")
        return False


def test_quota_optimizer_integration():
    """Test that QuotaOptimizer uses all discovery methods correctly"""
    print("\n" + "="*60)
    print("TESTING: QuotaOptimizer Integration")
    print("="*60)
    
    try:
        from quota.quota_optimizer import (
            get_quota_optimizer, 
            get_best_gemini_model, 
            get_best_groq_model
        )
        
        optimizer = get_quota_optimizer()
        
        print("\n[+] Testing get_gemini_models()...")
        gemini_models = optimizer.get_gemini_models(
            api_key=os.environ.get("GEMINI_API_KEY"),
            force_refresh=True  # Force fresh discovery
        )
        print(f"    Result: {gemini_models[:3]}..." if len(gemini_models) > 3 else f"    Result: {gemini_models}")
        
        print("\n[+] Testing get_groq_models()...")
        groq_models = optimizer.get_groq_models(
            api_key=os.environ.get("GROQ_API_KEY"),
            force_refresh=True
        )
        print(f"    Result: {groq_models[:3]}..." if len(groq_models) > 3 else f"    Result: {groq_models}")
        
        print("\n[+] Testing get_huggingface_models()...")
        hf_models = optimizer.get_huggingface_models(
            api_key=os.environ.get("HUGGINGFACE_API_KEY"),
            force_refresh=True
        )
        print(f"    Result: {hf_models[:3]}..." if len(hf_models) > 3 else f"    Result: {hf_models}")
        
        print("\n[+] Testing get_openrouter_free_models()...")
        or_models = optimizer.get_openrouter_free_models(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            force_refresh=True
        )
        print(f"    Result: {or_models[:3]}..." if len(or_models) > 3 else f"    Result: {or_models}")
        
        print("\n[+] Testing centralized getters...")
        print(f"    get_best_gemini_model(): {get_best_gemini_model()}")
        print(f"    get_best_groq_model(): {get_best_groq_model()}")
        
        optimizer.print_status()
        return True
        
    except Exception as e:
        print(f"[X] Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all discovery tests"""
    print("\n" + "#"*60)
    print("#  AI MODEL DISCOVERY TEST SUITE")
    print("#  Testing all 4 providers' dynamic model discovery")
    print("#"*60)
    
    # Load environment variables
    env_file = os.path.join(os.path.dirname(__file__), 'config', 'env_for_deployment.txt')
    if os.path.exists(env_file):
        print(f"\n[*] Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if value and key not in os.environ:
                        os.environ[key] = value
                        print(f"    Loaded: {key}={'*' * min(len(value), 10)}...")
    
    results = {}
    
    # Run all tests
    results['Gemini'] = test_gemini_discovery()
    results['Groq'] = test_groq_discovery()
    results['HuggingFace'] = test_huggingface_discovery()
    results['OpenRouter'] = test_openrouter_discovery()
    results['QuotaOptimizer'] = test_quota_optimizer_integration()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for provider, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {provider}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n  Total: {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] All discovery methods working!")
        return 0
    else:
        print("\n[WARNING] Some discovery methods failed (will use fallbacks)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

