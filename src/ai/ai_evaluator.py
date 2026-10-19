#!/usr/bin/env python3
"""
AI Video Content Evaluator - Uses Groq to evaluate video content quality
PRODUCTION USE: Filters out bad quality content and provides guardrails.
Also used in development for feedback.

Key Functions:
1. evaluate_question() - Check if question is viral-worthy
2. check_content_safety() - Filter inappropriate content
3. should_upload() - Final gate before uploading
"""
import os
import json
from typing import Dict, Optional

# Try to import Groq
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


class AIEvaluator:
    """Evaluates video content for virality and engagement potential."""
    
    def __init__(self):
        self.groq_client = None
        self._model = None  # v17.9.10: Cache dynamic model
        if HAS_GROQ:
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                self.groq_client = Groq(api_key=api_key)
    
    def _get_model(self) -> str:
        """v17.9.10: Get model dynamically with caching."""
        if self._model:
            return self._model
        try:
            from model_helper import get_dynamic_groq_model
            self._model = get_dynamic_groq_model()
        except ImportError:
            try:
                from src.ai.model_helper import get_dynamic_groq_model
                self._model = get_dynamic_groq_model()
            except:
                self._model = "llama-3.3-70b-versatile"  # Emergency fallback
        return self._model
    
    def evaluate_question(self, option_a: str, option_b: str) -> Dict:
        """
        Evaluate a Would You Rather question for viral potential.
        Returns scores and suggestions.
        """
        if not self.groq_client:
            return {"error": "No Groq client available"}
        
        prompt = f'''You are a YouTube Shorts viral content expert. Evaluate this "Would You Rather" question:

Option A: {option_a}
Option B: {option_b}

Rate on a scale of 1-10 and provide brief feedback:

1. **Engagement Potential**: Will people want to comment their choice?
2. **Controversy Level**: Is it debatable without being offensive?
3. **Relatability**: Can most viewers relate to the choices?
4. **Shareability**: Would someone share this with friends?
5. **Hook Factor**: Does it grab attention in first 2 seconds?

Return ONLY valid JSON:
{{
    "engagement": <1-10>,
    "controversy": <1-10>,
    "relatability": <1-10>,
    "shareability": <1-10>,
    "hook_factor": <1-10>,
    "overall_score": <1-10>,
    "verdict": "<one of: VIRAL, GOOD, AVERAGE, WEAK>",
    "improvement_tip": "<one sentence suggestion to make it more viral>"
}}'''

        try:
            response = self.groq_client.chat.completions.create(
                model=self._get_model(),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content)
            
        except Exception as e:
            return {"error": str(e)}
    
    def evaluate_video_components(self, 
                                   topic: str,
                                   option_a: str,
                                   option_b: str,
                                   theme_name: str,
                                   has_broll: bool,
                                   has_music: bool,
                                   has_sfx: bool) -> Dict:
        """
        Evaluate all components of a video for quality.
        """
        if not self.groq_client:
            return {"error": "No Groq client available"}
        
        prompt = f'''You are a YouTube Shorts production expert. Evaluate this video setup:

CONTENT:
- Topic/Question: Would you rather {option_a} OR {option_b}?
- Visual Theme: {theme_name}
- Has B-roll video: {"Yes" if has_broll else "No"}
- Has Background Music: {"Yes" if has_music else "No"}  
- Has Sound Effects: {"Yes" if has_sfx else "No"}

Rate each component 1-10 and give the overall video potential:

Return ONLY valid JSON:
{{
    "topic_score": <1-10>,
    "topic_feedback": "<brief feedback on the question>",
    "production_score": <1-10>,
    "production_feedback": "<feedback on audio/visual elements>",
    "overall_potential": <1-10>,
    "verdict": "<VIRAL POTENTIAL / GOOD / NEEDS WORK / WEAK>",
    "top_improvement": "<single most important improvement needed>"
}}'''

        try:
            response = self.groq_client.chat.completions.create(
                model=self._get_model(),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content)
            
        except Exception as e:
            return {"error": str(e)}
    
    def suggest_better_question(self, current_a: str, current_b: str) -> Optional[Dict]:
        """
        Suggest a more viral version of the question.
        """
        if not self.groq_client:
            return None
        
        prompt = f'''Current "Would You Rather" question:
A: {current_a}
B: {current_b}

This question is not viral enough. Create a MORE ENGAGING version that:
1. Has higher stakes or more extreme choices
2. Is more controversial (but appropriate)
3. Makes people NEED to pick a side
4. Would make viewers comment and debate

Return ONLY valid JSON:
{{
    "option_a": "<improved option A - max 60 chars>",
    "option_b": "<improved option B - max 60 chars>",
    "why_better": "<one sentence explaining why this is more viral>"
}}'''

        try:
            response = self.groq_client.chat.completions.create(
                model=self._get_model(),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"   ⚠️ Could not get suggestion: {e}")
            return None


def evaluate_and_print(option_a: str, option_b: str, theme: str = "Unknown",
                       has_broll: bool = True, has_music: bool = True, has_sfx: bool = True):
    """Convenience function to evaluate and print results."""
    evaluator = AIEvaluator()
    
    print("\n" + "="*60)
    print("🤖 AI CONTENT EVALUATION")
    print("="*60)
    
    # Evaluate question
    print("\n📝 Evaluating question...")
    q_result = evaluator.evaluate_question(option_a, option_b)
    
    if "error" not in q_result:
        print(f"   Engagement: {q_result.get('engagement', '?')}/10")
        print(f"   Controversy: {q_result.get('controversy', '?')}/10")
        print(f"   Relatability: {q_result.get('relatability', '?')}/10")
        print(f"   Shareability: {q_result.get('shareability', '?')}/10")
        print(f"   Hook Factor: {q_result.get('hook_factor', '?')}/10")
        print(f"   ⭐ OVERALL: {q_result.get('overall_score', '?')}/10 - {q_result.get('verdict', '?')}")
        print(f"   💡 Tip: {q_result.get('improvement_tip', 'N/A')}")
    else:
        print(f"   ⚠️ Evaluation failed: {q_result['error']}")
    
    # Evaluate full video
    print("\n🎬 Evaluating video setup...")
    v_result = evaluator.evaluate_video_components(
        f"{option_a} vs {option_b}",
        option_a, option_b, theme,
        has_broll, has_music, has_sfx
    )
    
    if "error" not in v_result:
        print(f"   Topic Score: {v_result.get('topic_score', '?')}/10")
        print(f"   Production Score: {v_result.get('production_score', '?')}/10")
        print(f"   ⭐ POTENTIAL: {v_result.get('overall_potential', '?')}/10 - {v_result.get('verdict', '?')}")
        print(f"   📝 Topic: {v_result.get('topic_feedback', 'N/A')}")
        print(f"   🎥 Production: {v_result.get('production_feedback', 'N/A')}")
        print(f"   💡 Top Fix: {v_result.get('top_improvement', 'N/A')}")
    else:
        print(f"   ⚠️ Evaluation failed: {v_result['error']}")
    
    # If score is low, suggest improvement
    overall = q_result.get('overall_score', 5)
    if overall < 7:
        print("\n🔄 Getting improvement suggestion...")
        suggestion = evaluator.suggest_better_question(option_a, option_b)
        if suggestion:
            print(f"   Better A: {suggestion.get('option_a', 'N/A')}")
            print(f"   Better B: {suggestion.get('option_b', 'N/A')}")
            print(f"   Why: {suggestion.get('why_better', 'N/A')}")
    
    print("\n" + "="*60)
    
    return q_result, v_result


class ProductionGuardrails:
    """
    PRODUCTION USE: Gate-keep content before upload.
    Ensures quality, safety, and brand consistency.
    """
    
    # Minimum scores required for upload
    MIN_OVERALL_SCORE = 5  # Out of 10
    MIN_SAFETY_SCORE = 8   # Content safety is critical
    
    # Content safety filters
    BANNED_TOPICS = [
        "death", "suicide", "murder", "abuse", "violence",
        "drugs", "alcohol", "gambling", "weapons",
        "sex", "nsfw", "porn", "nude",
        "racist", "nazi", "hate", "slur",
        "poop", "vomit", "diarrhea", "fart",  # Gross content
    ]
    
    def __init__(self):
        self.evaluator = AIEvaluator()
    
    def check_content_safety(self, option_a: str, option_b: str) -> Dict:
        """
        Check if content is safe for all audiences.
        
        Returns:
            {
                "is_safe": bool,
                "safety_score": int,
                "reason": str (if not safe)
            }
        """
        text = f"{option_a} {option_b}".lower()
        
        # Rule-based check first (fast)
        for banned in self.BANNED_TOPICS:
            if banned in text:
                return {
                    "is_safe": False,
                    "safety_score": 0,
                    "reason": f"Contains banned topic: '{banned}'"
                }
        
        # AI-based check for edge cases (if Groq available)
        if self.evaluator.groq_client:
            try:
                prompt = f'''Is this "Would You Rather" question appropriate for ALL ages on YouTube?
                
Question: "{option_a}" OR "{option_b}"

Return ONLY valid JSON:
{{
    "is_appropriate": <true or false>,
    "safety_score": <1-10, 10 being totally safe>,
    "concern": "<any concern or 'none'>"
}}'''
                
                response = self.evaluator.groq_client.chat.completions.create(
                    model=self._get_model(),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.1
                )
                
                content = response.choices[0].message.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                result = json.loads(content)
                return {
                    "is_safe": result.get("is_appropriate", True) and result.get("safety_score", 10) >= self.MIN_SAFETY_SCORE,
                    "safety_score": result.get("safety_score", 10),
                    "reason": result.get("concern", "none")
                }
                
            except Exception as e:
                # If AI check fails, rely on rule-based (already passed)
                pass
        
        return {"is_safe": True, "safety_score": 10, "reason": "none"}
    
    def should_upload(self, option_a: str, option_b: str, 
                     has_broll: bool = True, has_music: bool = True) -> Dict:
        """
        FINAL DECISION: Should this video be uploaded?
        
        Returns:
            {
                "should_upload": bool,
                "score": int,
                "reason": str
            }
        """
        # Step 1: Safety check
        safety = self.check_content_safety(option_a, option_b)
        if not safety.get("is_safe", True):
            return {
                "should_upload": False,
                "score": 0,
                "reason": f"Safety: {safety.get('reason', 'Content not safe')}"
            }
        
        # Step 2: Quality check
        quality = self.evaluator.evaluate_question(option_a, option_b)
        overall = quality.get("overall_score", 5)
        
        if overall < self.MIN_OVERALL_SCORE:
            return {
                "should_upload": False,
                "score": overall,
                "reason": f"Quality too low: {overall}/10 (min: {self.MIN_OVERALL_SCORE})"
            }
        
        # Step 3: Production check - require at least basic production
        if not has_music and not has_broll:
            return {
                "should_upload": False,
                "score": overall,
                "reason": "Missing both music and b-roll - production quality too low"
            }
        
        return {
            "should_upload": True,
            "score": overall,
            "reason": f"Score: {overall}/10 - {quality.get('verdict', 'APPROVED')}"
        }


if __name__ == "__main__":
    # Test evaluation
    print("🧪 Testing AI Evaluator")
    evaluate_and_print(
        "Live 10 years younger in eternal health",
        "Have 10 extra years of lifespan naturally",
        theme="Electric Blue",
        has_broll=True,
        has_music=False,
        has_sfx=True
    )
    
    # Test production guardrails
    print("\n🛡️ Testing Production Guardrails")
    guardrails = ProductionGuardrails()
    
    # Test safe content
    result = guardrails.should_upload(
        "Have unlimited money",
        "Have unlimited time",
        has_broll=True, has_music=True
    )
    print(f"Safe content: {result}")
    
    # Test unsafe content
    result = guardrails.should_upload(
        "Watch someone vomit",
        "Have diarrhea in public",
        has_broll=True, has_music=True
    )
    print(f"Unsafe content: {result}")
