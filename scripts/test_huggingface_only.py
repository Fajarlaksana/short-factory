#!/usr/bin/env python3
"""
HuggingFace-Only Video Generation Test

Tests video generation using ONLY HuggingFace as the AI provider.
- No Gemini, Groq, or OpenRouter
- No regeneration attempts
- Full enhancement verification
"""

import os
import sys
import json
from datetime import datetime

# Add src paths - same as the main wrapper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'enhancements'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'analytics'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'quota'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'platforms'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'ai'))

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('utf-8', errors='replace').decode('utf-8'))


def test_huggingface_discovery():
    """Test that HuggingFace model discovery works."""
    safe_print("[2/6] Testing HuggingFace Model Discovery...")
    try:
        from quota.quota_optimizer import get_quota_optimizer
        quota_opt = get_quota_optimizer()
        hf_key = os.environ.get('HUGGINGFACE_API_KEY', '')
        hf_models = quota_opt.get_huggingface_models(hf_key, force_refresh=True)
        safe_print(f"[+] Found {len(hf_models)} HuggingFace models:")
        for m in hf_models[:5]:
            safe_print(f"    - {m}")
        return ("HuggingFace Dynamic Discovery", "PASS", f"{len(hf_models)} models found")
    except Exception as e:
        safe_print(f"[!] Model discovery error: {e}")
        return ("HuggingFace Dynamic Discovery", "FAIL", str(e))


def test_huggingface_api_call():
    """Test that HuggingFace API calls work using huggingface_hub library."""
    safe_print("")
    safe_print("[3/6] Testing HuggingFace API Call...")
    
    hf_key = os.environ.get('HUGGINGFACE_API_KEY', '')
    
    if not hf_key:
        return ("HuggingFace API Call", "FAIL", "No API key")
    
    # Use huggingface_hub library (REST API is deprecated)
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        safe_print("    Installing huggingface_hub...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"])
        from huggingface_hub import InferenceClient
    
    # Use dynamically discovered models
    try:
        from quota.quota_optimizer import get_quota_optimizer
        quota_opt = get_quota_optimizer()
        test_models = quota_opt.get_huggingface_models(hf_key)
        safe_print(f"    Using {len(test_models)} discovered models")
    except Exception as e:
        safe_print(f"    Discovery failed, using fallbacks: {e}")
        test_models = [
            "google/gemma-2-2b-it",
            "Qwen/Qwen2.5-1.5B-Instruct",
            "HuggingFaceH4/zephyr-7b-beta",
        ]
    
    client = InferenceClient(token=hf_key)
    
    for model in test_models[:5]:
        try:
            safe_print(f"    Trying {model}...")
            response = client.chat_completion(
                messages=[{"role": "user", "content": "Generate a viral YouTube Short topic in one sentence."}],
                model=model,
                max_tokens=50
            )
            content = response.choices[0].message.content
            if content:
                # Safely display (avoid emoji encoding issues)
                safe_content = content.encode('ascii', 'ignore').decode('ascii')[:80]
                safe_print(f"[+] Response: {safe_content}...")
                return ("HuggingFace API Call", "PASS", f"{model} works")
        except Exception as e:
            err_str = str(e)[:100]
            safe_print(f"    Error: {err_str}")
            continue
    
    return ("HuggingFace API Call", "FAIL", "All models failed")


def test_video_generation():
    """Test the full video generation pipeline."""
    safe_print("")
    safe_print("[4/6] Testing Video Generation...")
    safe_print("-" * 60)
    
    # Run the actual video generation using subprocess
    # This is cleaner than trying to import the async main function
    import subprocess
    
    # Change to project root
    project_root = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(project_root)
    
    # Build command
    cmd = [
        sys.executable, 
        "pro_video_generator.py",
        "--count", "1",
        "--no-upload",
        "--test-mode"
    ]
    
    safe_print(f"Running: {' '.join(cmd)}")
    safe_print("-" * 60)
    
    try:
        # Run with environment that only has HuggingFace key
        env = os.environ.copy()
        env['GEMINI_API_KEY'] = ''
        env['GROQ_API_KEY'] = ''
        env['OPENROUTER_API_KEY'] = ''
        env['PYTHONUNBUFFERED'] = '1'
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        safe_print("-" * 60)
        safe_print("STDOUT:")
        safe_print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
        
        if result.stderr:
            safe_print("-" * 60)
            safe_print("STDERR:")
            safe_print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        
        if result.returncode == 0:
            # Check if video was generated
            import glob
            videos = glob.glob("output/*.mp4") + glob.glob("test_output/*.mp4")
            if videos:
                return ("Video Generation", "PASS", f"{len(videos)} video(s) created")
            else:
                return ("Video Generation", "PARTIAL", "Process succeeded but no video file")
        else:
            return ("Video Generation", "FAIL", f"Exit code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        return ("Video Generation", "FAIL", "Timeout after 10 minutes")
    except Exception as e:
        return ("Video Generation", "FAIL", str(e))


def check_enhancements():
    """Check which enhancements are integrated."""
    safe_print("")
    safe_print("[5/6] Checking Enhancement Integration...")
    
    results = []
    
    # Check variety state
    variety_file = 'data/persistent/variety_state.json'
    if os.path.exists(variety_file):
        try:
            with open(variety_file) as f:
                variety = json.load(f)
            safe_print(f"[+] Variety State: {len(variety)} keys loaded")
            results.append(("Variety State", "PASS", f"{len(variety)} keys"))
        except Exception as e:
            results.append(("Variety State", "FAIL", str(e)))
    else:
        results.append(("Variety State", "INFO", "No previous state"))
    
    # Check viral patterns
    patterns_file = 'data/persistent/viral_patterns.json'
    if os.path.exists(patterns_file):
        try:
            with open(patterns_file) as f:
                patterns = json.load(f)
            safe_print(f"[+] Viral Patterns: {len(patterns)} keys loaded")
            results.append(("Viral Patterns", "PASS", f"{len(patterns)} keys"))
        except Exception as e:
            results.append(("Viral Patterns", "FAIL", str(e)))
    else:
        results.append(("Viral Patterns", "INFO", "No previous patterns"))
    
    # Check self-learning state
    learning_file = 'data/persistent/self_learning.json'
    if os.path.exists(learning_file):
        try:
            with open(learning_file) as f:
                learning = json.load(f)
            safe_print(f"[+] Self-Learning: {len(learning)} keys")
            results.append(("Self-Learning", "PASS", f"{len(learning)} keys"))
        except Exception as e:
            results.append(("Self-Learning", "FAIL", str(e)))
    else:
        results.append(("Self-Learning", "INFO", "No learning data yet"))
    
    return results


def main():
    safe_print("=" * 60)
    safe_print("  HUGGINGFACE-ONLY VIDEO GENERATION TEST")
    safe_print("=" * 60)
    safe_print("")
    
    # Track all results
    all_results = []
    
    # Step 1: Check environment
    safe_print("[1/6] Checking Environment...")
    hf_key = os.environ.get('HUGGINGFACE_API_KEY', '')
    safe_print(f"[+] HUGGINGFACE_API_KEY: {'SET' if hf_key else 'NOT SET'}")
    safe_print(f"[+] GEMINI_API_KEY: {'SET' if os.environ.get('GEMINI_API_KEY') else 'cleared'}")
    safe_print(f"[+] GROQ_API_KEY: {'SET' if os.environ.get('GROQ_API_KEY') else 'cleared'}")
    safe_print(f"[+] OPENROUTER_API_KEY: {'SET' if os.environ.get('OPENROUTER_API_KEY') else 'cleared'}")
    
    if not hf_key:
        safe_print("[!] ERROR: HUGGINGFACE_API_KEY not set!")
        all_results.append(("Environment Check", "FAIL", "No HuggingFace key"))
    else:
        all_results.append(("Environment Check", "PASS", "Keys configured"))
    
    # Step 2: Test model discovery
    all_results.append(test_huggingface_discovery())
    
    # Step 3: Test API call
    all_results.append(test_huggingface_api_call())
    
    # Step 4: Test video generation
    all_results.append(test_video_generation())
    
    # Step 5: Check enhancements
    all_results.extend(check_enhancements())
    
    # Step 6: Summary
    safe_print("")
    safe_print("[6/6] Test Summary")
    safe_print("-" * 60)
    safe_print(f"{'Test':<35} {'Status':<8} {'Details'}")
    safe_print("-" * 60)
    
    for name, status, details in all_results:
        icon = "[OK]" if status == "PASS" else "[X]" if status == "FAIL" else "[i]"
        safe_print(f"{name:<35} {icon} {status:<6} {str(details)[:30]}")
    
    safe_print("-" * 60)
    
    passed = sum(1 for _, s, _ in all_results if s == "PASS")
    failed = sum(1 for _, s, _ in all_results if s == "FAIL")
    safe_print(f"Total: {passed} passed, {failed} failed")
    
    # Save results
    os.makedirs('test_output', exist_ok=True)
    
    with open('test_output/enhancement_report.json', 'w') as f:
        json.dump({
            "test_type": "huggingface_only",
            "timestamp": datetime.now().isoformat(),
            "results": all_results,
            "passed": passed,
            "failed": failed
        }, f, indent=2)
    
    safe_print("")
    safe_print("=" * 60)
    safe_print("Test complete! Results saved to test_output/enhancement_report.json")
    safe_print("=" * 60)
    
    # Return success if no failures
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
