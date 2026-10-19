#!/usr/bin/env python3
"""
ViralShorts Factory - VIRAL VIDEO SCIENCE ENGINE
=================================================

Based on extensive research of what makes short-form content go viral.
This module implements the PSYCHOLOGICAL and STRUCTURAL secrets that 
top creators use to generate billions of views.

CORE PRINCIPLES:
================

1. THE PROMISE-PAYOFF CONTRACT
   - Every video makes an implicit PROMISE in the hook
   - The video MUST deliver on that promise
   - Failure to deliver = lost trust = no follows = no virality
   
   BAD: "Here's a life-changing strategy..." (never explains it)
   GOOD: "The 2-minute rule: Start any task for just 2 minutes. Your brain
          can't resist continuing once started. Try it with exercise."

2. THE INFORMATION SANDWICH
   - HOOK: Create curiosity gap
   - MEAT: Deliver actual specific value
   - CTA: Give them something to do/think about

3. THE SPECIFICITY PRINCIPLE
   - Vague = Boring
   - Specific = Interesting + Credible
   
   BAD: "Many people struggle with productivity"
   GOOD: "MIT researchers found 73% of people check their phone within 3
          minutes of feeling bored"

4. THE RE-WATCH FACTOR
   - Best viral content has something that makes you watch again
   - Hidden details, surprising twist, emotional moment

5. THE SOCIAL CURRENCY
   - People share content that makes them look smart/funny/informed
   - Ask: "Would someone share this to look good?"
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ViralVideoStructure:
    """The structure of a viral video."""
    hook: str                  # 1-2 seconds - STOP THE SCROLL
    tension_build: str         # 3-5 seconds - Create anticipation
    value_delivery: str        # 6-15 seconds - THE ACTUAL CONTENT (must be specific!)
    reinforcement: str         # 2-3 seconds - Drive the point home
    call_to_action: str        # 1-2 seconds - What should they do now?
    rewatch_trigger: str       # Why would someone watch again?


# =============================================================================
# CONTENT TYPE TEMPLATES - Each guarantees VALUE DELIVERY
# =============================================================================

CONTENT_TEMPLATES = {
    "life_hack": """
You are a productivity expert creating a SHORT video (40-50 seconds, 8-10 phrases).

CRITICAL RULE: You must provide a SPECIFIC, ACTIONABLE hack that viewers 
can USE IMMEDIATELY. No vague advice. No "there's a method..." without 
explaining the method.

TEMPLATE:
HOOK: Surprising claim that creates curiosity (2 seconds)
PROBLEM: Briefly state the common problem (3 seconds)
SOLUTION: THE ACTUAL HACK - specific steps or technique (8 seconds)
PROOF: Quick mention of why it works or who uses it (3 seconds)
CTA: Challenge viewer to try it (2 seconds)

EXAMPLE OF WHAT WE WANT:
"Want to fall asleep in under 2 minutes? Navy SEALs use this.
Relax your face muscles completely. Drop your shoulders.
Exhale and relax your chest. Clear your mind by imagining 
you're lying in a dark room. Works for 96% of people after 
6 weeks. Try it tonight."

EXAMPLE OF WHAT WE DON'T WANT:
"There's an amazing sleep technique you should learn.
Scientists say it really works. You can find more info online.
Follow for more tips."

Generate a complete life hack video script:
TOPIC: {topic}

Output JSON:
{{
    "hook": "The attention-grabbing opening (max 12 words)",
    "full_script": "The COMPLETE script with actual value (50-80 words)",
    "specific_action": "The ONE thing viewer should do",
    "why_it_works": "Brief explanation of mechanism",
    "call_to_action": "What should they comment/do?"
}}
""",

    "scary_fact": """
You are a fascinating facts creator. Your goal is to share GENUINELY 
surprising information that makes people think "wow, I never knew that!"

CRITICAL RULE: The fact must be SPECIFIC with numbers/details. And you 
must explain WHY it matters or WHAT it means for the viewer.

TEMPLATE:
HOOK: The shocking claim (2 seconds)
CONTEXT: Set the scene (3 seconds)
THE FACT: The specific information with details (8 seconds)
IMPLICATION: What this means for the viewer (4 seconds)
CTA: Thought-provoking question (2 seconds)

EXAMPLE OF WHAT WE WANT:
"You've walked past 36 murderers in your lifetime.
Based on population data and murder rates, the average city 
dweller crosses paths with 36 killers before age 70.
They looked normal. They said hi. You never knew.
Comment the creepiest stranger encounter you've had."

EXAMPLE OF WHAT WE DON'T WANT:
"There are scary things in the world you don't know about.
Scientists have discovered disturbing facts. Some people 
aren't who they seem. Stay safe out there."

Generate a scary/mind-blowing fact:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Shocking opener with specific claim (max 10 words)",
    "full_script": "Complete script with SPECIFIC details (50-80 words)",
    "the_fact": "The core factual claim",
    "source_hint": "Where this info comes from (studies/data/research)",
    "call_to_action": "Engaging question that drives comments"
}}
""",

    "money_fact": """
You are a financial educator creating SHORT content that gives REAL value.

CRITICAL RULE: Provide SPECIFIC financial insight with NUMBERS. Not 
"save money" but "the 50/30/20 rule: 50% needs, 30% wants, 20% savings".

TEMPLATE:
HOOK: Surprising money truth (2 seconds)
THE PROBLEM: What most people do wrong (4 seconds)  
THE SOLUTION: Specific strategy with numbers (10 seconds)
THE RESULT: What happens if they follow this (3 seconds)
CTA: Challenge them to start (2 seconds)

EXAMPLE OF WHAT WE WANT:
"The coffee math that changed my life.
$5 a day on coffee is $1,825 a year. In 30 years with 
7% returns, that's $172,000. I didn't quit coffee.
I made it at home for 50 cents. Put the difference 
in index funds. I'm up $14,000 in just 3 years.
What's your daily money leak?"

Generate a money/financial insight:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Attention-grabbing financial truth (max 10 words)",
    "full_script": "Complete script with SPECIFIC numbers (50-80 words)",
    "specific_strategy": "The actionable financial move",
    "numbers_included": ["list of specific numbers used"],
    "call_to_action": "Question about their finances"
}}
""",

    "psychology_fact": """
You are a psychology expert explaining HOW THE MIND WORKS in simple terms.

CRITICAL RULE: Explain the psychological MECHANISM. Don't just say 
"your brain does X" - explain WHY and HOW, and what viewer can DO with 
this knowledge.

TEMPLATE:
HOOK: Surprising truth about human behavior (2 seconds)
SETUP: The common situation (3 seconds)
THE PSYCHOLOGY: What's actually happening in the brain (8 seconds)
THE HACK: How to use this knowledge (4 seconds)
CTA: Self-reflection question (2 seconds)

EXAMPLE OF WHAT WE WANT:
"Your brain sabotages you at 3pm every day.
Around 3pm, your circadian rhythm dips. Willpower crashes.
This is when most people break diets and skip workouts.
The fix: Schedule your hardest tasks for 10am when 
cortisol peaks. Leave easy work for the afternoon slump.
What time does YOUR willpower crash?"

Generate a psychology insight:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Surprising psychology truth (max 10 words)",
    "full_script": "Complete script with mechanism explained (50-80 words)",
    "the_mechanism": "The psychological/neurological explanation",
    "practical_application": "How viewer can use this",
    "call_to_action": "Self-reflection question"
}}
""",

    "mind_blow": """
You are creating content that makes people's minds EXPLODE with new 
perspective.

CRITICAL RULE: The insight must fundamentally change how they see 
something. And you must fully EXPLAIN the perspective shift, not just 
hint at it.

TEMPLATE:
HOOK: Statement that challenges assumptions (2 seconds)
THE COMMON BELIEF: What most people think (3 seconds)
THE TWIST: The reality that changes everything (8 seconds)
THE IMPLICATION: Why this matters (4 seconds)
CTA: Mind-expanding question (2 seconds)

EXAMPLE OF WHAT WE WANT:
"You're not afraid of the dark.
You're afraid of what MIGHT be in it.
Your brain evolved to fear uncertainty, not absence of light.
That's why anxiety hits hardest when you don't know 
what's coming. The unknown is scarier than any real threat.
What uncertainty is haunting you right now?"

Generate a mind-blowing insight:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Assumption-challenging opener (max 10 words)",
    "full_script": "Complete perspective shift explained (50-80 words)",
    "the_twist": "The reality that changes their view",
    "deeper_meaning": "The philosophical/practical implication",
    "call_to_action": "Deep reflection question"
}}
""",

    # v17.7.5: Additional high-performing content templates
    "productivity_hack": """
You are a productivity expert sharing SPECIFIC techniques that actually work.

CRITICAL RULE: Give an exact technique with steps, not vague advice.
Instead of "be more focused" say "the 2-minute rule: if it takes less 
than 2 minutes, do it now instead of adding it to your list."

TEMPLATE:
HOOK: Surprising productivity claim (2 seconds)
THE PROBLEM: What most people do wrong (3 seconds)
THE TECHNIQUE: Exact method with steps (10 seconds)
THE RESULT: Specific outcome (3 seconds)
CTA: Challenge to try today (2 seconds)

Generate a productivity hack:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Productivity truth that stops scrolling (max 10 words)",
    "full_script": "Complete technique with exact steps (50-80 words)",
    "technique_name": "What this method is called",
    "steps": ["step 1", "step 2", "step 3"],
    "call_to_action": "Challenge to start today"
}}
""",

    "relationship_insight": """
You are a relationship psychology expert sharing insights that help people.

CRITICAL RULE: Explain WHY the insight works psychologically. Not just 
"do this" but "do this BECAUSE the brain responds to X."

TEMPLATE:
HOOK: Surprising relationship truth (2 seconds)
CONTEXT: Common situation (3 seconds)
THE INSIGHT: Why this happens + the psychology (8 seconds)
THE FIX: What to do differently (4 seconds)
CTA: Relate to their experience (2 seconds)

Generate a relationship insight:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Relationship truth that intrigues (max 10 words)",
    "full_script": "Complete insight with psychology (50-80 words)",
    "the_psychology": "Why this happens in relationships",
    "actionable_advice": "What they can do differently",
    "call_to_action": "Personal reflection question"
}}
""",

    "health_tip": """
You are a health educator sharing EVIDENCE-BASED tips, not trends.

CRITICAL RULE: Include specific numbers or mechanisms. Not "sleep is good"
but "7 hours of sleep reduces cortisol by 30%, which is why weight loss
is 3x harder when sleep deprived."

TEMPLATE:
HOOK: Surprising health truth (2 seconds)
THE SCIENCE: What happens in your body (5 seconds)
THE NUMBERS: Specific data (5 seconds)
THE ACTION: Exact what to do (4 seconds)
CTA: Health check question (2 seconds)

Generate a health tip:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Health truth that surprises (max 10 words)",
    "full_script": "Complete health tip with science (50-80 words)",
    "the_mechanism": "What happens in the body",
    "specific_numbers": ["statistics or measurements"],
    "call_to_action": "Health-related question"
}}
""",

    "success_secret": """
You are sharing real insights from successful people that viewers can apply.

CRITICAL RULE: Be specific about WHO does this and WHAT the result is.
Not "successful people wake up early" but "Jeff Bezos makes all decisions
by 10am because willpower depletes 40% by afternoon."

TEMPLATE:
HOOK: What successful people do differently (2 seconds)
THE PERSON: Who does this (or common pattern) (3 seconds)
THE REASON: Why it works (6 seconds)
HOW TO APPLY: Viewer's version of this (5 seconds)
CTA: Challenge them (2 seconds)

Generate a success insight:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Success secret that intrigues (max 10 words)",
    "full_script": "Complete insight with example (50-80 words)",
    "who_does_this": "Example of successful person/people",
    "why_it_works": "The mechanism behind the success",
    "call_to_action": "Challenge to try this"
}}
""",

    "tech_hack": """
You are sharing hidden tech features that save time and impress people.

CRITICAL RULE: Be EXACT about where to find it and what it does.
Not "there's a cool feature" but "Press Ctrl+Shift+T to reopen your 
last closed browser tab. Works on Chrome, Firefox, and Edge."

TEMPLATE:
HOOK: Claim about what most people don't know (2 seconds)
THE FEATURE: Exact location and steps (6 seconds)
THE BENEFIT: What this saves/enables (4 seconds)
BONUS: Extra related tip (3 seconds)
CTA: Save for later prompt (2 seconds)

Generate a tech hack:
TOPIC: {topic}

Output JSON:
{{
    "hook": "Tech secret claim (max 10 words)",
    "full_script": "Complete tutorial with steps (50-80 words)",
    "exact_steps": ["step 1", "step 2"],
    "works_on": ["platforms/devices this works on"],
    "call_to_action": "Save this prompt"
}}
"""
}


# =============================================================================
# VALUE DELIVERY CHECKER
# =============================================================================

class ValueDeliveryChecker:
    """
    Checks if content actually DELIVERS value or just promises it.
    
    This is CRITICAL for preventing the "learn now but never teaches" problem.
    """
    
    # Red flag phrases that indicate missing value
    EMPTY_PROMISE_PHRASES = [
        "learn now", "find out", "discover how", "the secret is",
        "you should try", "there's a way", "studies show", "experts say",
        "research proves", "you won't believe", "here's why",
        "click to learn", "follow for more", "check the link",
        "comment below", "share this", "stay tuned"
    ]
    
    # Indicators of actual value
    VALUE_INDICATORS = [
        # Numbers and specifics
        r'\d+%', r'\d+ minutes', r'\d+ seconds', r'\$\d+',
        r'\d+ steps', r'\d+ times', r'\d+ people',
        # Action words
        r'first,', r'then,', r'finally,', r'step \d',
        r'do this:', r'try this:', r'here\'s how:',
        # Specifics
        r'called the', r'known as', r'named',
    ]
    
    def check_content(self, content: str) -> Dict:
        """
        Analyze content for value delivery.
        
        Returns a score and specific issues.
        """
        content_lower = content.lower()
        
        issues = []
        score = 100
        
        # Check for empty promises
        for phrase in self.EMPTY_PROMISE_PHRASES:
            if phrase in content_lower:
                # Check if there's follow-through after the promise
                idx = content_lower.find(phrase)
                after = content_lower[idx:idx+200]
                
                # Look for value indicators after the promise
                has_followthrough = any(
                    __import__('re').search(pattern, after) 
                    for pattern in self.VALUE_INDICATORS
                )
                
                if not has_followthrough:
                    issues.append(f"Empty promise: '{phrase}' without follow-through")
                    score -= 15
        
        # Check for specificity
        import re
        has_numbers = bool(re.search(r'\d+', content))
        has_action = any(word in content_lower for word in 
                        ['do', 'try', 'start', 'stop', 'use', 'apply'])
        
        if not has_numbers:
            issues.append("No specific numbers or data")
            score -= 20  # v17.9: Increased penalty
        
        if not has_action:
            issues.append("No actionable advice")
            score -= 20  # v17.9: Increased penalty
        
        # v17.9 FIX: Check for ACTUAL value delivery, not just promises
        # These patterns indicate content that TELLS without SHOWING
        vague_patterns = [
            r'you (can|could|should|might|will)',  # Vague future promises
            r'(this|it) (will|can|could) (help|change|improve)',  # Generic claims
            r'(many|some|most) people',  # Non-specific audience
            r'(great|amazing|incredible|powerful) (way|method|technique)',  # Hype words
        ]
        vague_count = sum(1 for p in vague_patterns if re.search(p, content_lower))
        if vague_count >= 2:
            issues.append(f"Too vague ({vague_count} hype patterns) - lacks concrete examples")
            score -= 15
        
        # v17.9 FIX: Check for CONCRETE examples/steps
        concrete_patterns = [
            r'for example',
            r'here\'s (how|what)',
            r'step \d|first.*then.*finally',
            r'specifically',
            r'called the|named|known as',
            r'\d+ (minutes|seconds|days|hours)',
            r'(example|instance):',
        ]
        concrete_count = sum(1 for p in concrete_patterns if re.search(p, content_lower))
        if concrete_count == 0:
            issues.append("No concrete examples or step-by-step instructions")
            score -= 20
        
        # Check length - too short = probably not enough value
        # v17.9 FIX: Minimum 80 words (was 40) for real content
        word_count = len(content.split())
        if word_count < 80:
            issues.append(f"Too short ({word_count} words) - needs 80+ for real value")
            score -= 25  # v17.9: Increased penalty
        elif word_count < 60:
            issues.append(f"Critically short ({word_count} words) - intro without content")
            score -= 35
        
        return {
            "score": max(0, score),
            "issues": issues,
            "verdict": "GOOD" if score >= 75 else "NEEDS_WORK" if score >= 55 else "REJECT",  # v17.9: Higher thresholds
            "word_count": word_count,
            "has_numbers": has_numbers,
            "has_action": has_action,
            "concrete_examples": concrete_count  # v17.9: Track this
        }
    
    def improve_content(self, content: str, video_type: str) -> str:
        """
        Use AI to improve content that fails value check.
        """
        check = self.check_content(content)
        
        if check["verdict"] == "GOOD":
            return content
        
        # Generate improvement prompt
        issues_text = "\n".join(f"- {issue}" for issue in check["issues"])
        
        improve_prompt = f"""The following video content has these problems:
{issues_text}

Original content:
{content}

Rewrite this to:
1. Add SPECIFIC numbers and data
2. Give ACTIONABLE steps the viewer can take
3. DELIVER on any promises made
4. Be at least 50 words

Keep the same topic but make it VALUABLE.

Return ONLY the improved script, no explanations."""
        
        # This would call AI - for now return original
        return content


# =============================================================================
# VIRAL CONTENT GENERATOR
# =============================================================================

class ViralContentGenerator:
    """Generate content that's GUARANTEED to deliver value."""
    
    def __init__(self):
        self.checker = ValueDeliveryChecker()
        self.groq_key = os.environ.get("GROQ_API_KEY")
    
    def generate(self, video_type: str, topic: str = None) -> Optional[Dict]:
        """
        Generate viral content with guaranteed value delivery.
        """
        if video_type not in CONTENT_TEMPLATES:
            video_type = "life_hack"
        
        template = CONTENT_TEMPLATES[video_type]
        
        # If no topic, let AI choose
        if not topic:
            topic = "surprise me with something genuinely useful"
        
        prompt = template.format(topic=topic)
        
        if not self.groq_key:
            return self._fallback_content(video_type)
        
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            # v16.8: DYNAMIC MODEL - No hardcoded model names
            try:
                from quota_optimizer import get_quota_optimizer
                optimizer = get_quota_optimizer()
                groq_models = optimizer.get_groq_models(self.groq_key)
                model_to_use = groq_models[0] if groq_models else "llama-3.3-70b-versatile"
            except:
                model_to_use = "llama-3.3-70b-versatile"
            
            response = client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.8
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            content = json.loads(result.strip())
            
            # Verify value delivery
            script = content.get("full_script", "")
            check = self.checker.check_content(script)
            
            if check["verdict"] == "REJECT":
                print(f"⚠️ Content failed value check: {check['issues']}")
                # Try to improve or regenerate
                return self.generate(video_type, topic + " - be MORE SPECIFIC")
            
            content["value_check"] = check
            return content
            
        except Exception as e:
            print(f"⚠️ Generation failed: {e}")
            return self._fallback_content(video_type)
    
    def _fallback_content(self, video_type: str) -> Dict:
        """
        EMERGENCY FALLBACK ONLY - Used when AI is completely unavailable.
        
        WARNING: This should rarely happen. If you see this often,
        check the AI API keys and connectivity!
        
        These fallbacks are evergreen content that still delivers value.
        """
        print("⚠️ WARNING: Using EMERGENCY FALLBACK content - AI unavailable!")
        print("   → Check GROQ_API_KEY is set and valid")
        print("   → This content is not trending/timely")
        
        from datetime import datetime
        now = datetime.now()
        
        # Make fallback slightly dynamic based on time
        time_context = "morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening"
        
        # Evergreen fallbacks that still provide value
        fallbacks = {
            "life_hack": {
                "hook": "The 2-minute rule changes everything",
                "full_script": f"If a task takes less than 2 minutes, do it immediately. "
                              f"This one rule eliminated 80 percent of my mental clutter. "
                              f"That email reply? 2 minutes. Hang up your coat? 30 seconds. "
                              f"Your brain wastes more energy remembering tasks than doing them. "
                              f"Start this {time_context} - do any small task right now. "
                              f"What has been sitting on your mental to-do list for weeks?",
                "specific_action": "Do any task under 2 minutes immediately",
                "is_fallback": True,
            },
            "scary_fact": {
                "hook": "Your phone tracks more than you think",
                "full_script": f"Your typing speed drops 12 percent about 3 days before you get sick. "
                              f"Stanford researchers found your phone motion sensors detect subtle "
                              f"changes in how you hold it when inflammation starts. "
                              f"Some health apps can now predict illness before you feel anything. "
                              f"Your daily screentime data is a health record you never knew existed. "
                              f"Has your phone ever seemed to know something was wrong?",
                "the_fact": "Phones detect illness through typing pattern changes",
                "is_fallback": True,
            },
            "psychology_fact": {
                "hook": "Your brain gets weaker as the day goes on",
                "full_script": f"Your willpower is not infinite. It drains throughout the day. "
                              f"By 3pm, decision fatigue has reduced your self-control by 40 percent. "
                              f"That is why diets fail at dinner and impulse buys happen after work. "
                              f"The fix: Make important decisions before noon. "
                              f"Schedule your workout for morning. Plan meals the night before. "
                              f"When does YOUR willpower crash?",
                "the_mechanism": "Decision fatigue depletes willpower by afternoon",
                "is_fallback": True,
            }
        }
        return fallbacks.get(video_type, fallbacks["life_hack"])


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'ViralVideoStructure',
    'CONTENT_TEMPLATES', 
    'ValueDeliveryChecker',
    'ViralContentGenerator'
]


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 VIRAL VIDEO SCIENCE - Value Delivery Test")
    print("=" * 60)
    
    checker = ValueDeliveryChecker()
    
    # Test BAD content (the problem you identified)
    bad_content = """
    Your brain has an amazing trick you need to learn.
    Studies show this works for most people.
    Experts recommend trying this method.
    Follow for more tips on improving your life.
    """
    
    print("\n❌ Testing BAD content (no value delivery):")
    result = checker.check_content(bad_content)
    print(f"   Score: {result['score']}/100")
    print(f"   Verdict: {result['verdict']}")
    for issue in result['issues']:
        print(f"   ⚠️ {issue}")
    
    # Test GOOD content (delivers actual value)
    good_content = """
    The 2-minute rule will change your life.
    If any task takes less than 2 minutes, do it immediately.
    This simple system eliminated 80% of my mental clutter.
    Yesterday I completed 47 tiny tasks that would have 
    piled up and stressed me out. Your brain wastes more 
    energy remembering tasks than actually doing them.
    What's been sitting on your mental to-do list?
    """
    
    print("\n✅ Testing GOOD content (delivers value):")
    result = checker.check_content(good_content)
    print(f"   Score: {result['score']}/100")
    print(f"   Verdict: {result['verdict']}")
    if result['issues']:
        for issue in result['issues']:
            print(f"   ⚠️ {issue}")
    else:
        print("   ✅ No issues found!")
    
    # Test generator
    print("\n" + "=" * 60)
    print("🎬 Generating VALUE-FIRST content...")
    print("=" * 60)
    
    gen = ViralContentGenerator()
    content = gen.generate("life_hack", "productivity")
    
    if content:
        print(f"\n📝 Hook: {content.get('hook', 'N/A')}")
        print(f"\n📜 Script:\n{content.get('full_script', 'N/A')}")
        print(f"\n🎯 Action: {content.get('specific_action', 'N/A')}")
        
        if "value_check" in content:
            print(f"\n✅ Value Score: {content['value_check']['score']}/100")

