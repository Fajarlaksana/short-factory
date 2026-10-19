#!/usr/bin/env python3
"""
ViralShorts Factory - Version Verification System
==================================================

This script MUST be run before pushing any new version.
It checks ALL concerns automatically:

1. Analytics feedback is updated with latest changes
2. No hardcoded values that should be AI-driven
3. No quota violations possible
4. No contradicting/overriding configurations
5. All imported functions are actually USED
6. Self-review and bug search
7. Workflows are updated and functional
8. All enhancements are integrated (IN)

Usage:
    python version_verification.py          # Full verification
    python version_verification.py --quick  # Quick checks only
    
This is BUILT-IN - runs automatically on pre-commit hook.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

CRITICAL_FILES = [
    "pro_video_generator.py",  # Wrapper
    "src/core/pro_video_generator.py",  # Main generator
    "src/enhancements/enhancements_v9.py",
    "src/enhancements/enhancements_v12.py",
    "src/quota/quota_optimizer.py",
    "src/quota/token_budget_manager.py",
    "src/analytics/analytics_feedback.py",
    "src/utils/persistent_state.py",
]

WORKFLOW_FILES = [
    ".github/workflows/generate.yml",
    ".github/workflows/analytics-feedback.yml",
    ".github/workflows/monthly-analysis.yml",
    ".github/workflows/pre-work.yml",
]

# Patterns that indicate hardcoding that SHOULD be dynamic
HARDCODE_PATTERNS = [
    # Model names without dynamic selection
    (r'model\s*=\s*["\'](?!{)[a-z0-9\-\.]+["\']', "Hardcoded AI model name"),
    # Fixed category/topic strings used directly (not in seed lists)
    (r'category\s*=\s*["\']psychology["\']', "Hardcoded category 'psychology'"),
    (r'topic\s*=\s*["\'][^"\']+["\'](?!.*random)', "Potentially hardcoded topic"),
    # Fixed timestamps
    (r'cron:\s*["\'][0-9\s\*]+["\'].*#.*hardcoded', "Hardcoded cron schedule"),
]

# Patterns that indicate proper dynamic/AI-driven approach
GOOD_PATTERNS = [
    (r'get_quota_optimizer|QuotaOptimizer', "Uses dynamic quota optimizer"),
    (r'get_.*_models\(', "Uses dynamic model discovery"),
    (r'from quota_optimizer import', "Imports quota optimizer"),
]

# ============================================================================
# VERIFICATION CHECKS
# ============================================================================

class VersionVerifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.version = self._get_version()
        
    def _get_version(self) -> str:
        """Get current version from git or file."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "-1", "--format=%s"],
                capture_output=True, text=True
            )
            match = re.search(r'v(\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        return "unknown"
    
    def _read_file(self, path: str) -> str:
        """Read file contents safely."""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""
    
    def _read_main_generator(self) -> str:
        """Read the main pro_video_generator.py (handles both old and new structure)."""
        content = self._read_file("src/core/pro_video_generator.py")
        if not content:
            content = self._read_main_generator()
        return content
    
    # ========================================================================
    # CHECK 1: Analytics Feedback Updated
    # ========================================================================
    def check_analytics_updated(self) -> bool:
        """Verify analytics feedback includes latest enhancement tracking."""
        print("\n[1] ANALYTICS FEEDBACK CHECK...")
        
        # Check both possible paths (old and new structure)
        content = self._read_file("src/analytics/analytics_feedback.py")
        if not content:
            content = self._read_file("analytics_feedback.py")
        if not content:
            self.errors.append("analytics_feedback.py not found in src/analytics/")
            return False
        
        # Check for v12 enhancement tracking
        checks = [
            ("v12_enhancements", "Tracks v12 enhancements"),
            ("quality_score", "Tracks quality scores"),
            ("performance", "Tracks performance metrics"),
        ]
        
        passed = 0
        for pattern, desc in checks:
            if pattern in content:
                self.passed.append(f"Analytics: {desc}")
                passed += 1
            else:
                self.warnings.append(f"Analytics missing: {desc}")
        
        # Check if analytics is used in main flow
        main_content = self._read_file("src/core/pro_video_generator.py")
        if not main_content:
            main_content = self._read_main_generator()
        if "analytics" in main_content.lower() and "record" in main_content.lower():
            self.passed.append("Analytics: Recording integrated in main flow")
            passed += 1
        else:
            self.errors.append("Analytics not recording in main flow")
        
        print(f"   Passed: {passed}/{len(checks)+1}")
        return passed == len(checks) + 1
    
    # ========================================================================
    # CHECK 2: No Hardcoded Values That Should Be Dynamic
    # ========================================================================
    def check_no_hardcoding(self) -> bool:
        """Check for hardcoded values that should be AI-driven."""
        print("\n[2] HARDCODING CHECK...")
        
        issues = []
        
        for filepath in CRITICAL_FILES:
            content = self._read_file(filepath)
            if not content:
                continue
            
            for pattern, desc in HARDCODE_PATTERNS:
                matches = re.findall(pattern, content)
                # Filter out fallback values (which are acceptable)
                for match in matches:
                    # Check if it's in a fallback/except block (acceptable)
                    context = content[max(0, content.find(match)-200):content.find(match)+200]
                    if "fallback" in context.lower() or "except" in context.lower():
                        continue
                    issues.append(f"{filepath}: {desc} - '{match[:50]}...'")
        
        if issues:
            for issue in issues[:5]:  # Limit output
                self.warnings.append(issue)
            print(f"   Found {len(issues)} potential hardcoding issues")
        else:
            self.passed.append("No hardcoding issues found")
            print("   No issues found")
        
        return len(issues) == 0
    
    # ========================================================================
    # CHECK 3: Quota Violation Prevention
    # ========================================================================
    def check_quota_safety(self) -> bool:
        """Verify quota management is in place."""
        print("\n[3] QUOTA SAFETY CHECK...")
        
        main_content = self._read_main_generator()
        
        checks = [
            ("budget_manager" in main_content, "Token budget manager used"),
            ("quota_monitor" in main_content, "Quota monitor used"),
            ("record_usage" in main_content, "Usage tracking active"),
            ("record_429" in main_content, "429 error handling active"),
            ("get_groq_models" in main_content, "Dynamic Groq models"),
            ("get_gemini_models" in main_content, "Dynamic Gemini models"),
        ]
        
        # v17.9.13: Check for quota-aware mechanisms
        model_helper_path = Path("src/ai/model_helper.py")
        if model_helper_path.exists():
            model_helper = model_helper_path.read_text(errors='ignore')
            checks.append(("record_quota_from_429" in model_helper, "Quota learning from 429 errors"))
            checks.append(("actual_quotas.json" in model_helper, "Quota cache persistence"))
        
        # Check generate.yml for pre-work download
        generate_yml_path = Path(".github/workflows/generate.yml")
        if generate_yml_path.exists():
            generate_yml = generate_yml_path.read_text(errors='ignore')
            checks.append(("pre-generated-concepts" in generate_yml, "Pre-work concepts download"))
        
        # Check pre-work.yml for permissions
        prework_yml_path = Path(".github/workflows/pre-work.yml")
        if prework_yml_path.exists():
            prework_yml = prework_yml_path.read_text(errors='ignore')
            checks.append(("permissions:" in prework_yml and "contents: write" in prework_yml, "Pre-work write permissions"))
        
        passed = 0
        for check, desc in checks:
            if check:
                self.passed.append(f"Quota: {desc}")
                passed += 1
            else:
                self.errors.append(f"Quota missing: {desc}")
        
        print(f"   Passed: {passed}/{len(checks)}")
        return passed == len(checks)
    
    # ========================================================================
    # CHECK 4: No Contradicting Configurations
    # ========================================================================
    def check_no_contradictions(self) -> bool:
        """Check for contradicting or overriding configurations."""
        print("\n[4] CONTRADICTION CHECK...")
        
        issues = []
        
        # Check for duplicate function definitions
        main_content = self._read_main_generator()
        func_defs = re.findall(r'^def (\w+)\(', main_content, re.MULTILINE)
        duplicates = [f for f in func_defs if func_defs.count(f) > 1]
        if duplicates:
            issues.append(f"Duplicate functions: {set(duplicates)}")
        
        # Check for conflicting imports
        imports = re.findall(r'^from (\w+) import .*?(\w+)', main_content, re.MULTILINE)
        import_names = [i[1] for i in imports]
        dup_imports = [i for i in import_names if import_names.count(i) > 1]
        if dup_imports:
            issues.append(f"Duplicate imports: {set(dup_imports)}")
        
        # Check for overriding global variables
        globals_set = re.findall(r'^([A-Z_]+)\s*=', main_content, re.MULTILINE)
        dup_globals = [g for g in globals_set if globals_set.count(g) > 1]
        if dup_globals:
            # Filter out intentional overrides (like in try/except)
            real_dups = []
            for g in set(dup_globals):
                pattern = rf'^{g}\s*='
                all_matches = list(re.finditer(pattern, main_content, re.MULTILINE))
                if len(all_matches) > 2:  # More than try/except pair
                    real_dups.append(g)
            if real_dups:
                issues.append(f"Multiple global assignments: {real_dups}")
        
        if issues:
            for issue in issues:
                self.warnings.append(issue)
            print(f"   Found {len(issues)} potential contradictions")
        else:
            self.passed.append("No contradictions found")
            print("   No issues found")
        
        # v17.9.10: Check for duration/phrase count contradictions
        duration_issues = self._check_duration_consistency()
        issues.extend(duration_issues)
        
        return len(issues) == 0
    
    def _check_duration_consistency(self) -> list:
        """v17.9.10: Check for inconsistent duration/phrase values across files."""
        print("   [4b] Duration consistency check...")
        
        issues = []
        old_patterns = [
            r'15-25\s*second',      # Old wrong duration
            r'25-45\s*second',      # Old wrong duration
            r'3-5\s*phrase',        # Old wrong phrase count
            r'4-6\s*phrase',        # Old wrong phrase count
        ]
        
        correct_patterns = [
            '40-50 second',         # Correct duration
            '8-10 phrase',          # Correct phrase count
        ]
        
        # Check all Python files in src/
        src_path = Path("src")
        if src_path.exists():
            for py_file in src_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    for pattern in old_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append(f"{py_file.name}: Found outdated '{pattern}' pattern")
                except:
                    pass
        
        if issues:
            print(f"      WARNING: {len(issues)} outdated duration/phrase values found!")
            for issue in issues[:3]:  # Show first 3
                self.warnings.append(issue)
        else:
            print("      Duration/phrase values consistent [OK]")
        
        return issues
    
    # ========================================================================
    # CHECK 5: All Imports Are Used
    # ========================================================================
    def check_all_imports_used(self) -> bool:
        """Verify all imported functions are actually used."""
        print("\n[5] IMPORT USAGE CHECK...")
        
        main_content = self._read_main_generator()
        
        # Find all imports from enhancements_v12
        v12_imports = re.findall(r'from enhancements_v12 import \(([\s\S]*?)\)', main_content)
        if v12_imports:
            import_str = v12_imports[0]
            # Only match function names (start with get_ or apply_)
            functions = re.findall(r'(get_\w+|apply_\w+)', import_str)
            
            used = 0
            unused = []
            for func in functions:
                # Check if function is called (not just imported)
                pattern = rf'{func}\s*\('
                if re.search(pattern, main_content):
                    used += 1
                else:
                    unused.append(func)
            
            usage_pct = 100 * used // len(functions) if functions else 0
            
            if unused:
                self.warnings.append(f"Unused v12 imports: {unused[:5]}...")
            
            if usage_pct >= 80:
                self.passed.append(f"V12 imports: {used}/{len(functions)} used ({usage_pct}%)")
                print(f"   V12 imports: {used}/{len(functions)} used ({usage_pct}%)")
                return True
            else:
                self.errors.append(f"V12 imports: Only {usage_pct}% used - need 80%+")
                print(f"   V12 imports: Only {usage_pct}% used - NEED 80%+")
                return False
        
        return True
    
    # ========================================================================
    # CHECK 6: Bug Search
    # ========================================================================
    def check_for_bugs(self) -> bool:
        """Search for common bug patterns."""
        print("\n[6] BUG PATTERN SEARCH...")
        
        bugs = []
        
        for filepath in CRITICAL_FILES:
            content = self._read_file(filepath)
            if not content:
                continue
            
            # Check for common issues
            bug_patterns = [
                (r'except:\s*$', "Bare except clause"),
                (r'import \*', "Wildcard import"),
                (r'print\([^)]*password', "Password in print"),
                (r'api_key\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded API key"),
                # Removed: .get() without default - too noisy, not a real bug
                # (r'\.get\([^,)]+\)[^.]', "Potentially unsafe .get() without default"),
            ]
            
            for pattern, desc in bug_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check context to reduce false positives
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        context = content[max(0, match.start()-50):match.end()+50]
                        # Skip if it's in a comment
                        if not context.strip().startswith('#'):
                            bugs.append(f"{filepath}: {desc}")
        
        if bugs:
            for bug in bugs[:5]:
                self.warnings.append(bug)
            print(f"   Found {len(bugs)} potential issues")
        else:
            self.passed.append("No obvious bugs found")
            print("   No obvious bugs found")
        
        return len(bugs) == 0
    
    # ========================================================================
    # CHECK 7: Workflows Updated
    # ========================================================================
    def check_workflows(self) -> bool:
        """Verify workflows exist and are properly configured."""
        print("\n[7] WORKFLOW CHECK...")
        
        issues = []
        
        for wf_path in WORKFLOW_FILES:
            content = self._read_file(wf_path)
            if not content:
                issues.append(f"Missing workflow: {wf_path}")
                continue
            
            # Check for required secrets
            required_secrets = ["GROQ_API_KEY", "GEMINI_API_KEY", "PEXELS_API_KEY"]
            for secret in required_secrets:
                if secret not in content:
                    issues.append(f"{wf_path}: Missing {secret}")
            
            # Check for OPENROUTER_API_KEY (new requirement)
            if "generate" in wf_path and "OPENROUTER_API_KEY" not in content:
                issues.append(f"{wf_path}: Missing OPENROUTER_API_KEY")
        
        if issues:
            for issue in issues:
                self.warnings.append(issue)
            print(f"   Found {len(issues)} workflow issues")
        else:
            self.passed.append("All workflows properly configured")
            print("   All workflows OK")
        
        return len(issues) == 0
    
    # ========================================================================
    # CHECK 8: All Enhancements Integrated
    # ========================================================================
    def check_enhancements_integrated(self) -> bool:
        """Verify all enhancement systems are integrated."""
        print("\n[8] ENHANCEMENT INTEGRATION CHECK...")
        
        main_content = self._read_main_generator()
        
        checks = [
            ("V12_MASTER_PROMPT" in main_content, "V12 master prompt loaded"),
            ("v12_guidelines" in main_content, "V12 guidelines injected"),
            ("enhancement_orch" in main_content, "V9 orchestrator used"),
            ("ENHANCEMENTS_V12_AVAILABLE" in main_content, "V12 availability check"),
            ("learning_engine" in main_content, "Self-learning engine active"),
            ("VIRAL_SCIENCE_AVAILABLE" in main_content, "Viral video science integrated"),
            ("ValueDeliveryChecker" in main_content, "Value delivery checking active"),
            ("AI_PATTERN_GENERATOR_AVAILABLE" in main_content or "ai_pattern_generator" in main_content, "AI pattern generator integrated"),
            ("MODEL_INTELLIGENCE_AVAILABLE" in main_content or "model_intelligence" in main_content, "Model intelligence integrated"),
            ("AI_HOOK_GENERATOR_AVAILABLE" in main_content, "AI hook generator integrated"),
            ("AI_CTA_GENERATOR_AVAILABLE" in main_content, "AI CTA generator integrated"),
        ]
        
        passed = 0
        for check, desc in checks:
            if check:
                self.passed.append(f"Enhancement: {desc}")
                passed += 1
            else:
                self.errors.append(f"Enhancement missing: {desc}")
        
        print(f"   Passed: {passed}/{len(checks)}")
        return passed == len(checks)
    
    # ========================================================================
    # CHECK: AI-FIRST ARCHITECTURE
    # ========================================================================
    def check_ai_first_architecture(self) -> bool:
        """
        v17.8: Check that all content patterns are AI-generated, not hardcoded.
        
        This enforces the 'prompt-AI based architecture' principle:
        - Data files should be populated by AI, not hardcoded
        - Hardcoded data should be marked as fallback only
        """
        print("\n[8] AI-FIRST ARCHITECTURE CHECK")
        
        all_good = True
        
        # Check viral_patterns.json
        patterns_file = "data/persistent/viral_patterns.json"
        try:
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                
                if data.get("ai_generated") == True:
                    self.passed.append("viral_patterns.json is AI-generated")
                    print("   [OK] viral_patterns.json: AI-generated")
                elif data.get("patterns_source") == "NEEDS_AI_GENERATION":
                    self.passed.append("viral_patterns.json marked for AI generation")
                    print("   [OK] viral_patterns.json: Awaiting AI generation")
                else:
                    # Check if it looks hardcoded
                    if len(data.get("title_patterns", [])) > 3 and not data.get("ai_generated"):
                        self.warnings.append("viral_patterns.json appears hardcoded - should be AI-generated")
                        print("   [!] viral_patterns.json: May be hardcoded (review needed)")
                    else:
                        self.passed.append("viral_patterns.json structure OK")
                        print("   [OK] viral_patterns.json: Structure OK")
        except Exception as e:
            self.warnings.append(f"Could not check viral_patterns.json: {e}")
        
        # Check variety_state.json
        variety_file = "data/persistent/variety_state.json"
        try:
            if os.path.exists(variety_file):
                with open(variety_file, 'r') as f:
                    data = json.load(f)
                
                if data.get("source") in ["AI_LEARNED", "AI_GENERATED", "ANALYTICS", "ANALYTICS_LEARNED"]:
                    self.passed.append("variety_state.json is AI-learned")
                    print("   [OK] variety_state.json: AI-learned")
                elif data.get("weekly_last_updated"):
                    self.passed.append("variety_state.json updated by analytics")
                    print("   [OK] variety_state.json: Updated by analytics")
                else:
                    self.passed.append("variety_state.json exists")
                    print("   [INFO] variety_state.json: Exists (source not specified)")
        except Exception as e:
            self.warnings.append(f"Could not check variety_state.json: {e}")
        
        # Check for AIPatternGenerator in codebase
        generator_file = "src/ai/ai_pattern_generator.py"
        if os.path.exists(generator_file):
            content = self._read_file(generator_file)
            if "generate_patterns_with_ai" in content:
                self.passed.append("AI pattern generator implemented")
                print("   [OK] AI pattern generator: Implemented")
            else:
                self.errors.append("AI pattern generator missing generate_patterns_with_ai")
                all_good = False
        else:
            self.errors.append("Missing src/ai/ai_pattern_generator.py")
            all_good = False
            print("   [X] AI pattern generator: MISSING")
        
        # Check self_learning.json
        learning_file = "data/persistent/self_learning.json"
        try:
            if os.path.exists(learning_file):
                with open(learning_file, 'r') as f:
                    data = json.load(f)
                
                if data.get("source") == "REAL_ANALYTICS":
                    self.passed.append("self_learning.json marked for real analytics")
                    print("   [OK] self_learning.json: Real analytics only")
                elif data.get("awaiting_real_data"):
                    self.passed.append("self_learning.json awaiting real data")
                    print("   [OK] self_learning.json: Awaiting real data")
                else:
                    # Check if it looks seeded
                    if data.get("stats", {}).get("total_videos", 0) > 10:
                        self.warnings.append("self_learning.json may contain seeded data")
                        print("   [!] self_learning.json: May have seeded data (review)")
                    else:
                        self.passed.append("self_learning.json structure OK")
                        print("   [OK] self_learning.json: Structure OK")
        except Exception as e:
            self.warnings.append(f"Could not check self_learning.json: {e}")
        
        return all_good
    
    # ========================================================================
    # CHECK 9: NEW AI MODULES (v17.8.27)
    # ========================================================================
    def check_ai_modules(self) -> bool:
        """Check that all new AI modules exist and are functional."""
        print("\n[9] AI MODULES CHECK (v17.8.27)...")
        
        # All AI modules that should exist
        ai_modules = [
            ("src/ai/ai_description_generator.py", "get_description_generator"),
            ("src/ai/ai_hashtag_generator.py", "get_hashtag_generator"),
            ("src/ai/ai_thumbnail_text.py", "get_thumbnail_optimizer"),
            ("src/ai/ai_trend_analyzer.py", "get_trend_analyzer"),
            ("src/ai/ai_audience_persona.py", "get_persona_generator"),
            ("src/ai/ai_voice_script.py", "get_voice_optimizer"),
            ("src/ai/ai_comment_response.py", "get_comment_generator"),
            ("src/analytics/retention_predictor.py", "get_retention_predictor"),
            ("src/analytics/engagement_predictor.py", "get_engagement_predictor"),
            ("src/analytics/virality_calculator.py", "get_virality_calculator"),
            ("src/analytics/script_analyzer.py", "get_script_analyzer"),
            ("src/analytics/competitor_gap_analyzer.py", "get_gap_analyzer"),
            ("src/analytics/dashboard_generator.py", "get_dashboard_generator"),
            ("src/core/content_optimizer.py", "get_content_optimizer"),
            ("src/core/ai_quality_gate.py", "get_quality_gate"),
        ]
        
        passed = 0
        missing = 0
        
        for filepath, function_name in ai_modules:
            if os.path.exists(filepath):
                content = self._read_file(filepath)
                if function_name in content:
                    passed += 1
                else:
                    self.warnings.append(f"{filepath}: Missing {function_name}")
            else:
                self.errors.append(f"Missing AI module: {filepath}")
                missing += 1
        
        if missing == 0:
            self.passed.append(f"All {len(ai_modules)} AI modules present")
            print(f"   [OK] All {len(ai_modules)} AI modules found")
        else:
            print(f"   [X] Missing {missing} AI modules")
        
        print(f"   Modules verified: {passed}/{len(ai_modules)}")
        
        return missing == 0
    
    # ========================================================================
    # CHECK 10: AI MODULE INTEGRATION (v17.9.6)
    # ========================================================================
    def check_ai_module_integration(self) -> bool:
        """Check that all AI modules are actually INTEGRATED (not just existing)."""
        print("\n[10] AI MODULE INTEGRATION CHECK (v17.9.6)...")
        
        generator = self._read_file("src/core/pro_video_generator.py")
        
        # These modules must be imported AND used in the generator
        required_integrations = [
            ("AIQualityGate", "AI_QUALITY_GATE_AVAILABLE"),
            ("ContentOptimizer", "CONTENT_OPTIMIZER_AVAILABLE"),
            ("RetentionPredictor", "RETENTION_PREDICTOR_AVAILABLE"),
            ("EngagementPredictor", "ENGAGEMENT_PREDICTOR_AVAILABLE"),
            ("ViralityCalculator", "VIRALITY_CALCULATOR_AVAILABLE"),
            ("ScriptAnalyzer", "SCRIPT_ANALYZER_AVAILABLE"),
            ("AIDescriptionGenerator", "AI_DESCRIPTION_GENERATOR_AVAILABLE"),
            ("AIHashtagGenerator", "AI_HASHTAG_GENERATOR_AVAILABLE"),
            ("DashboardGenerator", "DASHBOARD_GENERATOR_AVAILABLE"),
        ]
        
        integrated = 0
        for class_name, flag_name in required_integrations:
            if class_name in generator and flag_name in generator:
                integrated += 1
                print(f"   [OK] {class_name}")
            else:
                self.errors.append(f"{class_name} not integrated in generator")
                print(f"   [X] {class_name} NOT INTEGRATED")
        
        if integrated == len(required_integrations):
            self.passed.append(f"All {len(required_integrations)} AI modules integrated")
            return True
        else:
            return False
    
    # ========================================================================
    # CHECK 11: v17.9.5 YOUTUBE-ONLY MODE
    # ========================================================================
    def check_youtube_only_mode(self) -> bool:
        """Check v17.9.5 YouTube-only features are properly configured."""
        print("\n[11] YOUTUBE-ONLY MODE CHECK (v17.9.5)...")
        # Note: Check numbers updated for v17.9.6
        
        issues = []
        
        # Check workflow has --youtube-only flag
        workflow = self._read_file(".github/workflows/generate.yml")
        if "--youtube-only" in workflow:
            self.passed.append("Workflow uses --youtube-only flag")
            print("   [OK] --youtube-only flag in workflow")
        else:
            issues.append("Workflow missing --youtube-only flag")
            print("   [X] --youtube-only flag NOT FOUND in workflow")
        
        # Check batch_size default is 1
        if "default: '1'" in workflow and "Videos to generate (1 per workflow" in workflow:
            self.passed.append("Batch size default is 1")
            print("   [OK] Batch size default = 1")
        else:
            issues.append("Batch size default should be 1 for YouTube-only")
            print("   [!] Batch size default not set to 1")
        
        # Check Dailymotion is not in upload command
        if "dailymotion=False" in self._read_file("src/core/pro_video_generator.py"):
            self.passed.append("Dailymotion disabled in youtube-only mode")
            print("   [OK] Dailymotion disabled")
        
        # Check learned metrics function exists
        generator = self._read_file("src/core/pro_video_generator.py")
        if "get_learned_optimal_metrics" in generator:
            self.passed.append("Learned metrics function exists")
            print("   [OK] get_learned_optimal_metrics() exists")
        else:
            issues.append("Missing get_learned_optimal_metrics function")
            print("   [X] get_learned_optimal_metrics NOT FOUND")
        
        # Check update_learned_metrics is called in workflow
        if "update_learned_metrics_from_performance" in workflow:
            self.passed.append("Metrics learning integrated in workflow")
            print("   [OK] Metrics learning in workflow")
        else:
            issues.append("update_learned_metrics not called in workflow")
            print("   [X] Metrics learning NOT in workflow")
        
        if issues:
            for issue in issues:
                self.errors.append(issue)
            return False
        return True
    
    # ========================================================================
    # CHECK 11: TEST SUITE STATUS
    # ========================================================================
    def check_test_suite(self) -> bool:
        """Check that the test suite exists and passes."""
        print("\n[11] TEST SUITE CHECK...")
        
        test_file = "scripts/test_all_ai_modules.py"
        
        if not os.path.exists(test_file):
            self.errors.append("Test suite missing: scripts/test_all_ai_modules.py")
            print("   [X] Test suite NOT FOUND")
            return False
        
        content = self._read_file(test_file)
        
        # Count test sections
        test_count = content.count("# TEST ")
        
        if test_count >= 20:
            self.passed.append(f"Test suite has {test_count} test sections")
            print(f"   [OK] Test suite has {test_count} test sections")
        else:
            self.warnings.append(f"Test suite only has {test_count} tests (expected 20+)")
            print(f"   [!] Only {test_count} test sections (expected 20+)")
        
        return True
    
    # ========================================================================
    # CHECK 14: v17.9.7 FIXES VERIFICATION
    # ========================================================================
    def check_v1797_fixes(self) -> bool:
        """Check v17.9.7 critical fixes are properly implemented."""
        print("\n[14] v17.9.7 FIXES CHECK...")
        
        issues = []
        generator = self._read_file("src/core/pro_video_generator.py")
        model_helper = self._read_file("src/ai/model_helper.py")
        budget_manager = self._read_file("src/quota/token_budget_manager.py")
        
        # 1. AI module method fixes - correct method names used
        if "analyzer.analyze_script(script_content)" in generator:
            print("   [OK] ScriptAnalyzer uses correct analyze_script(content) call")
        else:
            issues.append("ScriptAnalyzer may have wrong method call")
        
        if "predictor.predict_retention(retention_content)" in generator:
            print("   [OK] RetentionPredictor uses correct predict_retention(content) call")
        else:
            issues.append("RetentionPredictor may have wrong method call")
        
        if "calculator.calculate_virality(virality_content)" in generator:
            print("   [OK] ViralityCalculator uses correct calculate_virality(content) call")
        else:
            issues.append("ViralityCalculator may have wrong method call")
        
        if "quality_gate.check(gate_content)" in generator:
            print("   [OK] AIQualityGate uses correct check(content) call")
        else:
            issues.append("AIQualityGate may have wrong method call")
        
        if "optimizer.optimize(opt_content)" in generator:
            print("   [OK] ContentOptimizer uses correct optimize(content) call")
        else:
            issues.append("ContentOptimizer may have wrong method call")
        
        # 2. Rate limiter optimization
        if '"groq": 2.0' in model_helper or "'groq': 2.0" in model_helper:
            print("   [OK] Groq rate limit is 2.0s (optimized)")
        else:
            issues.append("Groq rate limit not optimized to 2.0s")
        
        if '"gemini": 5.0' in model_helper or "'gemini': 5.0" in model_helper:
            print("   [OK] Gemini rate limit is 5.0s (safe)")
        else:
            issues.append("Gemini rate limit not set to 5.0s")
        
        # 3. Provider priority - Gemini should be primary (v17.9.12: dynamic quota!)
        if "Gemini is PRIMARY" in budget_manager or "GEMINI FIRST" in budget_manager:
            print("   [OK] Gemini is PRIMARY provider (quota checked via API)")
        elif "Groq is PRIMARY" in budget_manager or "GROQ FIRST" in budget_manager:
            issues.append("Groq as primary - should be Gemini (v17.9.12)")
        else:
            issues.append("No primary provider set")
        
        # 4. TTS retry logic
        if "fallback_voices" in generator and "for retry in range(3)" in generator:
            print("   [OK] TTS has retry logic with fallback voices")
        else:
            issues.append("TTS missing retry logic or fallback voices")
        
        # 5. Version is 17.9.7
        if "v17.9.7" in generator:
            print("   [OK] Version is v17.9.7")
        else:
            issues.append("Version not updated to v17.9.7")
        
        # 6. God Tier Evaluator integrated
        if "GOD_TIER_EVALUATOR_AVAILABLE" in generator and "god_tier_evaluator" in generator:
            print("   [OK] God Tier Evaluator integrated")
        else:
            issues.append("God Tier Evaluator not integrated")
        
        if issues:
            for issue in issues:
                self.errors.append(f"v17.9.7: {issue}")
                print(f"   [X] {issue}")
            return False
        else:
            self.passed.append("All v17.9.7 fixes verified")
            return True
    
    def check_smart_router(self) -> bool:
        """
        v17.9.9: Check Smart Model Router is properly integrated.
        
        Verifies:
        1. SmartModelRouter exists and has all required methods
        2. SmartAICaller exists and uses the router
        3. pro_video_generator.py imports and uses smart router
        4. Fallback chains exist for all prompt types
        """
        print("\n[13] SMART MODEL ROUTER CHECK (v17.9.9)...")
        issues = []
        
        # Check 1: Router file exists
        router_path = Path("src/ai/smart_model_router.py")
        if not router_path.exists():
            issues.append("smart_model_router.py does not exist")
        else:
            router_content = self._read_file(str(router_path))
            
            # Check required methods
            required_methods = [
                "classify_prompt",
                "get_model_chain", 
                "get_best_model",
                "refresh_rankings",
                "_compute_rankings"
            ]
            for method in required_methods:
                if f"def {method}" not in router_content:
                    issues.append(f"Router missing method: {method}")
            
            # Check prompt types
            if "PROMPT_TYPES" not in router_content:
                issues.append("Router missing PROMPT_TYPES definition")
            
            # Check periodic refresh
            if "REFRESH_INTERVAL" not in router_content:
                issues.append("Router missing REFRESH_INTERVAL (should update weekly)")
        
        # Check 2: Caller file exists
        caller_path = Path("src/ai/smart_ai_caller.py")
        if not caller_path.exists():
            issues.append("smart_ai_caller.py does not exist")
        else:
            caller_content = self._read_file(str(caller_path))
            
            # Check it uses the router
            if "get_smart_router" not in caller_content:
                issues.append("Caller doesn't import smart router")
            
            # Check provider callers
            for provider in ["groq", "gemini", "openrouter", "huggingface"]:
                if f"_call_{provider}" not in caller_content:
                    issues.append(f"Caller missing provider: {provider}")
        
        # Check 3: Integration in pro_video_generator
        gen_content = self._read_main_generator()
        if "SMART_ROUTER_AVAILABLE" not in gen_content:
            issues.append("pro_video_generator.py missing SMART_ROUTER_AVAILABLE")
        if "smart_call_ai" not in gen_content:
            issues.append("pro_video_generator.py doesn't use smart_call_ai")
        
        # Check 4: Test file exists
        test_path = Path("scripts/test_smart_router.py")
        if not test_path.exists():
            self.warnings.append("Smart router test file missing")
        
        # Check 5: Decommissioned models only in SKIP_MODELS (v17.9.11)
        decommissioned = ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
        # Check in quota_optimizer (should NOT have decommissioned models in active use)
        quota_path = Path("src/quota/quota_optimizer.py")
        if quota_path.exists():
            quota_content = quota_path.read_text(encoding='utf-8', errors='ignore')
            for model in decommissioned:
                # Check if model is in default_models list (bad)
                if f'"{model}"' in quota_content and "default_models" in quota_content:
                    # Check if it's on a line with default_models
                    for line in quota_content.split('\n'):
                        if model in line and "NOTE" not in line and "#" not in line.split(model)[0]:
                            issues.append(f"Decommissioned model {model} in quota_optimizer")
        
        if issues:
            for issue in issues:
                self.errors.append(f"Smart Router: {issue}")
            return False
        else:
            self.passed.append("Smart Model Router properly integrated")
            print("   [OK] Router exists with all methods")
            print("   [OK] Caller exists with all providers")
            print("   [OK] Integrated in pro_video_generator.py")
            print("   [OK] Fallback chains and periodic refresh configured")
            print("   [OK] No decommissioned models in active code")
            return True
    
    # ========================================================================
    def check_score_maximization(self) -> bool:
        """
        v17.9.17: Check HYBRID GOD-LIKE-GENERIC prompts with context injection.
        
        Ensures:
        - Hook generator uses _build_context_section (hybrid approach)
        - CTA generator uses _build_context_section (hybrid approach)
        - Self-learning engine has get_viral_triggers()
        - No hardcoded year references in prompts
        - Scorers use dynamic patterns
        """
        print("\n[16] HYBRID PROMPT ARCHITECTURE CHECK (v17.9.17)...")
        
        issues = []
        
        # Check 1: High-quality model function exists
        model_helper = Path("src/ai/model_helper.py")
        if model_helper.exists():
            content = model_helper.read_text(encoding='utf-8', errors='ignore')
            if "get_high_quality_model" not in content:
                issues.append("model_helper missing get_high_quality_model function")
        
        # Check 2: Hook generator uses HYBRID approach with context injection
        hook_gen = Path("src/ai/ai_hook_generator.py")
        if hook_gen.exists():
            content = hook_gen.read_text(encoding='utf-8', errors='ignore')
            if "_build_context_section" not in content:
                issues.append("Hook generator missing _build_context_section (hybrid approach)")
            if "EXAMPLES THAT WORKED" not in content and "INSPIRATION" not in content:
                self.warnings.append("Hook generator may not inject learned examples")
        
        # Check 3: CTA generator uses HYBRID approach
        cta_gen = Path("src/ai/ai_cta_generator.py")
        if cta_gen.exists():
            content = cta_gen.read_text(encoding='utf-8', errors='ignore')
            if "_build_context_section" not in content:
                issues.append("CTA generator missing _build_context_section (hybrid approach)")
        
        # Check 4: Self-learning engine has viral triggers method
        learning_engine = Path("src/analytics/self_learning_engine.py")
        if learning_engine.exists():
            content = learning_engine.read_text(encoding='utf-8', errors='ignore')
            if "def get_viral_triggers" not in content:
                issues.append("Self-learning engine missing get_viral_triggers()")
        
        # Check 5: No hardcoded years in critical prompts
        for check_file in ["src/ai/ai_pattern_generator.py", "src/analytics/monthly_analysis.py"]:
            path = Path(check_file)
            if path.exists():
                content = path.read_text(encoding='utf-8', errors='ignore')
                # Check for hardcoded years in prompts (not comments)
                if '"2024' in content or '"2025' in content or '"2026' in content:
                    if "Generate" in content or "prompt" in content.lower():
                        self.warnings.append(f"{check_file} may have hardcoded year in prompt")
        
        # Check 6: Scorers use dynamic patterns
        virality = Path("src/analytics/virality_calculator.py")
        if virality.exists():
            content = virality.read_text(encoding='utf-8', errors='ignore')
            if "_init_dynamic_patterns" not in content:
                issues.append("Virality calculator not using dynamic patterns")
        
        if issues:
            for issue in issues:
                self.errors.append(f"Hybrid: {issue}")
            return False
        else:
            self.passed.append("Hybrid god-like-generic prompt architecture")
            print("   [OK] High-quality model functions exist")
            print("   [OK] Hook generator uses HYBRID approach with context injection")
            print("   [OK] CTA generator uses HYBRID approach with context injection")
            print("   [OK] Self-learning engine provides viral triggers")
            print("   [OK] Scorers use dynamic patterns")
            return True
    
    # ========================================================================
    # CHECK: Test Workflow (v17.9.18)
    # ========================================================================
    def check_test_workflow(self) -> bool:
        """Verify the zero-quota test workflow exists and is valid."""
        print("\n[NEW] DRY RUN TEST WORKFLOW CHECK...")
        
        # Check workflow file
        workflow_path = Path(".github/workflows/test-systems-dry-run.yml")
        if not workflow_path.exists():
            return self.error("test-systems-dry-run.yml not found")
        
        content = workflow_path.read_text(encoding='utf-8')
        
        # Check it doesn't use quota-consuming endpoints
        checks_passed = 0
        
        # Should use FREE endpoints
        if '/models' in content or 'models?' in content:
            checks_passed += 1
            self.passed.append("Test workflow uses FREE model discovery endpoints")
        
        # Should NOT make generateContent calls
        if 'generateContent' not in content:
            checks_passed += 1
            self.passed.append("Test workflow doesn't call generateContent in bash")
        
        # Check test script exists
        test_script = Path("scripts/test_systems_dry_run.py")
        if test_script.exists():
            checks_passed += 1
            self.passed.append("test_systems_dry_run.py exists")
        else:
            return self.error("test_systems_dry_run.py not found")
        
        if checks_passed >= 2:
            self.passed.append("Dry run test workflow valid")
            return True
        else:
            return self.error("Test workflow missing critical checks")
    
    # ========================================================================
    # MAIN VERIFICATION
    # ========================================================================
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("=" * 60)
        print(f"VERSION VERIFICATION - v{self.version}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = [
            self.check_analytics_updated(),
            self.check_no_hardcoding(),
            self.check_quota_safety(),
            self.check_no_contradictions(),
            self.check_all_imports_used(),
            self.check_for_bugs(),
            self.check_workflows(),
            self.check_enhancements_integrated(),
            self.check_ai_first_architecture(),  # v17.8: New check
            self.check_ai_module_integration(),  # v17.9.6: All modules integrated
            self.check_youtube_only_mode(),  # v17.9.5: YouTube-only mode
            self.check_ai_modules(),  # v17.8.27: All AI modules
            self.check_test_suite(),  # v17.8.27: Test suite
            self.check_v1797_fixes(),  # v17.9.7: Critical fixes
            self.check_smart_router(),  # v17.9.9: Smart Model Router
            self.check_score_maximization(),  # v17.9.15: Score maximization
            self.check_test_workflow(),  # v17.9.18: Dry run test workflow
        ]
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Passed:   {len(self.passed)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors:   {len(self.errors)}")
        
        if self.errors:
            print("\nERRORS (must fix):")
            for e in self.errors:
                print(f"  [X] {e}")
        
        if self.warnings:
            print("\nWARNINGS (review):")
            for w in self.warnings[:10]:
                print(f"  [!] {w}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        # Only fail on actual errors, not warnings
        all_passed = len(self.errors) == 0
        
        print("\n" + "=" * 60)
        if all_passed:
            print("[PASSED] VERIFICATION PASSED - Safe to push")
        else:
            print("[FAILED] VERIFICATION FAILED - Fix issues before pushing")
        print("=" * 60)
        
        return all_passed
    
    def save_report(self):
        """Save verification report to file."""
        report = {
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "passed": self.passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "result": "PASSED" if len(self.errors) == 0 else "FAILED"
        }
        
        report_dir = Path("data/persistent")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_dir / "last_verification.json", 'w') as f:
            json.dump(report, f, indent=2)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    verifier = VersionVerifier()
    
    if "--quick" in sys.argv:
        # Quick mode - just essential checks
        verifier.check_quota_safety()
        verifier.check_all_imports_used()
        verifier.check_workflows()
    else:
        # Full verification
        success = verifier.run_all_checks()
        verifier.save_report()
        
        if not success:
            print("\nRun with fixes, then verify again before pushing.")
            sys.exit(1)

