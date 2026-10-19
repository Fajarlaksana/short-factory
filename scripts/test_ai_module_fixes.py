#!/usr/bin/env python3
"""
Quick test to verify v17.9.7 AI module fixes work correctly.
"""

import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/analytics')
sys.path.insert(0, 'src/core')

def test_all_modules():
    """Test all AI modules with correct method signatures."""
    results = []
    
    # Test 1: ScriptAnalyzer
    try:
        from script_analyzer import ScriptAnalyzer
        analyzer = ScriptAnalyzer()
        result = analyzer.analyze_script({
            'hook': 'STOP - This will change your life',
            'phrases': ['Most people fail at this', 'Here is the real reason why'],
            'cta': 'Comment below what you think'
        })
        score = result.get('overall_score', 'N/A')
        print(f"[OK] ScriptAnalyzer.analyze_script() = {score}/100")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] ScriptAnalyzer: {e}")
        results.append(False)
    
    # Test 2: RetentionPredictor
    try:
        from retention_predictor import RetentionPredictor
        predictor = RetentionPredictor()
        result = predictor.predict_retention({
            'hook': 'STOP scrolling right now',
            'phrases': ['First reason', 'Second reason', 'Third reason'],
            'cta': 'Comment your thoughts',
            'category': 'money'
        })
        score = result.get('overall_retention', 'N/A')
        print(f"[OK] RetentionPredictor.predict_retention() = {score}%")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] RetentionPredictor: {e}")
        results.append(False)
    
    # Test 3: EngagementPredictor
    try:
        from engagement_predictor import EngagementPredictor
        predictor = EngagementPredictor()
        result = predictor.predict_engagement({
            'hook': 'Why do 90% of people fail?',
            'phrases': ['Reason one is mindset', 'Reason two is habits'],
            'cta': 'Comment if you agree!',
            'category': 'money'
        })
        score = result.get('overall_engagement', 'N/A')
        print(f"[OK] EngagementPredictor.predict_engagement() = {score}/100")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] EngagementPredictor: {e}")
        results.append(False)
    
    # Test 4: ViralityCalculator
    try:
        from virality_calculator import ViralityCalculator
        calc = ViralityCalculator()
        result = calc.calculate_virality({
            'hook': 'STOP - This secret changes everything',
            'phrases': ['Point one', 'Point two', 'Point three'],
            'cta': 'Comment your goal!',
            'category': 'money',
            'topic': 'wealth building strategies'
        })
        score = result.get('overall_score', 'N/A')
        grade = result.get('grade', 'N/A')
        print(f"[OK] ViralityCalculator.calculate_virality() = {score}/100 ({grade})")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] ViralityCalculator: {e}")
        results.append(False)
    
    # Test 5: AIQualityGate
    try:
        from ai_quality_gate import AIQualityGate
        gate = AIQualityGate()
        passed, report = gate.check({
            'hook': 'STOP - Secret nobody tells you',
            'phrases': ['First insight', 'Second insight'],
            'cta': 'Comment below',
            'category': 'money',
            'topic': 'financial freedom'
        })
        score = report.get('overall_score', 'N/A')
        print(f"[OK] AIQualityGate.check() = passed={passed}, score={score}/100")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] AIQualityGate: {e}")
        results.append(False)
    
    # Test 6: ContentOptimizer
    try:
        from content_optimizer import ContentOptimizer
        opt = ContentOptimizer()
        result = opt.optimize({
            'hook': 'Hi',
            'phrases': ['Test phrase'],
            'cta': '',
            'topic': 'money tips',
            'category': 'finance'
        })
        modules = len(result.get('modules_used', []))
        print(f"[OK] ContentOptimizer.optimize() = {modules} modules used")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] ContentOptimizer: {e}")
        results.append(False)
    
    # Summary
    print("")
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"[ALL PASSED] {passed}/{total} AI modules work correctly!")
        return True
    else:
        print(f"[FAILED] {passed}/{total} passed")
        return False

if __name__ == "__main__":
    success = test_all_modules()
    sys.exit(0 if success else 1)

