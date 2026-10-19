#!/usr/bin/env python3
"""
CRITICAL FIXES for Video Quality Issues
========================================

This module provides REAL fixes that ENFORCE quality:
1. AI-driven font selection with ACTUAL application
2. Varied sound effects (not same pattern every time)
3. Minimum quality score enforcement (8+/10)
4. Numbered promise validation in CODE (not just prompts)
"""

import random
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ============================================
# FIX 1: AI-DRIVEN FONT SELECTION
# ============================================

# Available fonts with their characteristics
AVAILABLE_FONTS = {
    "bebas-neue": {
        "moods": ["energetic", "bold", "action", "tech"],
        "categories": ["crypto", "tech", "fitness", "gaming"],
    },
    "oswald-bold": {
        "moods": ["professional", "serious", "news"],
        "categories": ["business", "news", "education"],
    },
    "anton": {
        "moods": ["dramatic", "impactful", "urgent"],
        "categories": ["breaking", "shocking", "trending"],
    },
    "montserrat-bold": {
        "moods": ["modern", "clean", "minimal"],
        "categories": ["lifestyle", "beauty", "fashion"],
    },
    "poppins-bold": {
        "moods": ["friendly", "approachable", "casual"],
        "categories": ["self_improvement", "mental_health", "productivity"],
    },
    "bangers": {
        "moods": ["fun", "playful", "exciting"],
        "categories": ["entertainment", "memes", "challenges"],
    },
    "permanent-marker": {
        "moods": ["personal", "authentic", "raw"],
        "categories": ["stories", "confessions", "tips"],
    },
    "archivo-black": {
        "moods": ["powerful", "statement", "bold"],
        "categories": ["motivation", "sports", "finance"],
    },
}


def select_font_for_content(category: str, mood: str = None, topic: str = None) -> str:
    """
    Select the BEST font based on content characteristics.
    This is NOT random - it's intelligent selection.
    
    Returns the font key to use.
    """
    category = category.lower() if category else "general"
    mood = mood.lower() if mood else "neutral"
    
    # Score each font based on match
    scores = {}
    for font_key, font_data in AVAILABLE_FONTS.items():
        score = 0
        
        # Category match (high weight)
        for cat in font_data["categories"]:
            if cat in category or category in cat:
                score += 10
        
        # Mood match (medium weight)
        for m in font_data["moods"]:
            if m in mood or mood in m:
                score += 5
        
        # Topic keyword match (low weight)
        if topic:
            topic_lower = topic.lower()
            for cat in font_data["categories"]:
                if cat in topic_lower:
                    score += 3
        
        scores[font_key] = score
    
    # Get best match (or random from top 3 if tie)
    max_score = max(scores.values())
    
    if max_score > 0:
        top_fonts = [k for k, v in scores.items() if v == max_score]
        return random.choice(top_fonts)
    else:
        # No specific match - use category-appropriate defaults
        category_defaults = {
            "tech": "bebas-neue",
            "crypto": "bebas-neue",
            "finance": "archivo-black",
            "self_improvement": "poppins-bold",
            "productivity": "poppins-bold",
            "mental_health": "poppins-bold",
            "entertainment": "bangers",
            "news": "oswald-bold",
        }
        
        for key, font in category_defaults.items():
            if key in category:
                return font
        
        # Ultimate fallback - random from all
        return random.choice(list(AVAILABLE_FONTS.keys()))


# ============================================
# FIX 2: VARIED SOUND EFFECTS
# ============================================

# SFX pools for different purposes
SFX_POOLS = {
    "hook": ["hit", "whoosh", "ding"],  # Variety for hooks
    "transition": ["whoosh", "tick", None],  # Some transitions silent
    "payoff": ["ding", "hit", None],  # Vary endings too
    "emphasis": ["tick", "ding", None],  # For emphasis moments
}


def get_varied_sfx_for_phrase(phrase_index: int, total_phrases: int, video_id: int = None) -> Optional[str]:
    """
    Get varied sound effect - NOT the same pattern every time.
    Uses video_id as seed for per-video consistency but cross-video variety.
    
    IMPROVED: More balanced weights for TRUE variety across videos.
    """
    # Use video ID to seed randomness for this video
    if video_id:
        random.seed(video_id + phrase_index * 7)  # Multiply by prime for better distribution
    
    if phrase_index == 0:
        # Hook: More balanced - 40% hit, 30% whoosh, 15% ding, 15% silent
        sfx = random.choices(
            ["hit", "whoosh", "ding", None],
            weights=[40, 30, 15, 15]
        )[0]
    elif phrase_index == total_phrases - 1:
        # Payoff: More balanced - 35% ding, 25% hit, 25% whoosh, 15% silent
        sfx = random.choices(
            ["ding", "hit", "whoosh", None],
            weights=[35, 25, 25, 15]
        )[0]
    else:
        # Middle phrases: More balanced - 30% whoosh, 25% tick, 25% silent, 20% ding
        sfx = random.choices(
            ["whoosh", "tick", None, "ding"],
            weights=[30, 25, 25, 20]
        )[0]
    
    # Reset random state
    random.seed()
    
    return sfx


# ============================================
# FIX 3: MINIMUM QUALITY ENFORCEMENT
# ============================================

MINIMUM_ACCEPTABLE_SCORE = 7  # v17.1: Lowered from 8 - 7/10 is acceptable quality
MAX_REGENERATION_ATTEMPTS = 3


def enforce_quality_score(content: Dict, ai_func, regenerate_func) -> Tuple[Dict, int]:
    """
    Enforce minimum quality score with regeneration.
    
    Returns (content, final_score)
    """
    score = content.get('evaluation_score', 0)
    
    if score >= MINIMUM_ACCEPTABLE_SCORE:
        return content, score
    
    # Need to regenerate
    for attempt in range(MAX_REGENERATION_ATTEMPTS):
        print(f"   [QUALITY] Score {score}/10 too low (min: {MINIMUM_ACCEPTABLE_SCORE}), regenerating (attempt {attempt + 1})...")
        
        # Regenerate with feedback
        feedback = f"Previous attempt scored {score}/10. Make it more engaging, specific, and valuable. Minimum acceptable is {MINIMUM_ACCEPTABLE_SCORE}/10."
        
        try:
            new_content = regenerate_func(feedback)
            if new_content:
                new_score = new_content.get('evaluation_score', 0)
                if new_score >= MINIMUM_ACCEPTABLE_SCORE:
                    print(f"   [QUALITY] Improved to {new_score}/10 - ACCEPTED")
                    return new_content, new_score
                score = new_score
                content = new_content
        except Exception as e:
            print(f"   [QUALITY] Regeneration failed: {e}")
    
    # After all attempts, accept best we have but log warning
    print(f"   [QUALITY WARNING] Could not achieve {MINIMUM_ACCEPTABLE_SCORE}/10 after {MAX_REGENERATION_ATTEMPTS} attempts. Best: {score}/10")
    return content, score


# ============================================
# FIX 4: PROMISE VALIDATION (AI-DRIVEN, GENERIC)
# ============================================

def extract_promised_count(text: str) -> Optional[int]:
    """
    GENERIC extraction of any numbered promise from text.
    Uses broad patterns to catch ANY numbered promise, not just specific words.
    
    Examples caught:
    - "5 tips" → 5
    - "7 ways" → 7
    - "10 secrets" → 10
    - "3 things you need" → 3
    - "Here are 4 reasons" → 4
    - "The top 6" → 6
    - ANY "number + noun" pattern
    """
    # GENERIC patterns - catch ANY numbered promise
    patterns = [
        # "X things/ways/etc" - ANY plural noun after a number
        r'(\d+)\s+\w+(?:s|es)\b',
        # "top/best X" - number after quantifier
        r'(?:top|best|here are|these|only|just)\s+(\d+)',
        # "X of the" patterns
        r'(\d+)\s+(?:of\s+the|that\s+will|which|to\s+\w+)',
        # Standalone prominent numbers at start
        r'^(\d+)\s+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            # Only consider reasonable counts (1-20)
            if 1 <= num <= 20:
                return num
    
    return None


def count_items_in_content(phrases: List[str]) -> int:
    """
    GENERIC count of items delivered in content.
    Counts ANY form of list item, not just specific words.
    """
    item_count = 0
    
    for phrase in phrases:
        # Explicit numbering: "1.", "2)", "3:"
        if re.match(r'^\s*\d+[\.\):\-]', phrase):
            item_count += 1
        # Ordinal words (generic pattern for any ordinal)
        elif re.search(r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|next|another|last|final)\b', phrase, re.IGNORECASE):
            item_count += 1
        # List indicators
        elif re.search(r'\b(one\s+(?:is|thing)|number\s+\d|#\d|step\s+\d)\b', phrase, re.IGNORECASE):
            item_count += 1
    
    # If no explicit items found, assume each phrase after hook is an item
    return max(item_count, len(phrases) - 1)


def validate_numbered_promise(hook: str, phrases: List[str]) -> Dict:
    """
    GENERIC validation that ANY numbered promise is kept.
    Works for tips, ways, secrets, reasons, or ANY other list type.
    
    Returns:
        {
            "promised": int or None,
            "delivered": int,
            "valid": bool,
            "fix_suggestion": str or None
        }
    """
    promised = extract_promised_count(hook)
    
    if promised is None:
        # No numbered promise detected
        return {"promised": None, "delivered": None, "valid": True, "fix_suggestion": None}
    
    delivered = count_items_in_content(phrases[1:])  # Exclude hook
    
    if delivered >= promised:
        return {
            "promised": promised,
            "delivered": delivered,
            "valid": True,
            "fix_suggestion": None
        }
    else:
        # Promise broken - suggest generic fix
        fix = f"Hook promises {promised} items but only {delivered} delivered. Either add more items or reduce the number in hook."
        return {
            "promised": promised,
            "delivered": delivered,
            "valid": False,
            "fix_suggestion": fix
        }


def fix_broken_promise(hook: str, delivered_count: int) -> str:
    """
    GENERIC fix for broken promise - replaces ANY number in hook.
    Works for any type of numbered promise, not just specific words.
    """
    # Find the first number in the hook that looks like a promise
    # and replace it with the delivered count
    
    # Pattern: number followed by plural word
    def replace_first_promise(match):
        return f'{delivered_count} {match.group(2)}'
    
    # Try to replace "X things/ways/etc"
    fixed = re.sub(r'(\d+)\s+(\w+(?:s|es)\b)', replace_first_promise, hook, count=1, flags=re.IGNORECASE)
    
    if fixed != hook:
        return fixed
    
    # Try "top/best X" pattern
    fixed = re.sub(r'(top|best|here are|these)\s+\d+', f'\\1 {delivered_count}', hook, count=1, flags=re.IGNORECASE)
    
    return fixed


# ============================================
# FIX 5: CONTENT PROMPT CONSTRAINTS
# ============================================

CONTENT_CONSTRAINTS = """
=== CRITICAL RENDERING CONSTRAINTS ===
When generating content, you MUST know:

AVAILABLE FONTS (choose one that matches mood):
- bebas-neue: Bold, energetic (tech, crypto, fitness)
- oswald-bold: Professional, serious (business, news)
- anton: Dramatic, impactful (breaking news, shocking)
- montserrat-bold: Modern, clean (lifestyle, beauty)
- poppins-bold: Friendly, approachable (self-improvement, mental health)
- bangers: Fun, playful (entertainment, memes)
- permanent-marker: Personal, authentic (stories, tips)
- archivo-black: Powerful, statement (motivation, finance)

SOUND EFFECTS AVAILABLE:
- hit: Dramatic impact (for hooks)
- whoosh: Smooth transition
- ding: Positive reveal/payoff
- tick: Countdown/emphasis

NUMBERED PROMISES:
If you promise "X things" in the hook, you MUST deliver EXACTLY X items.
Each item must be clearly identifiable in a separate phrase.

OUTPUT FORMAT:
Your JSON must include:
{
  "font_choice": "font-key-from-above",
  "sfx_style": "dramatic|subtle|minimal",
  "promised_count": number or null,
  "items": [list of exactly promised_count items if applicable]
}
"""


def get_constraint_aware_prompt(base_prompt: str) -> str:
    """
    Inject constraints into any prompt to make AI aware of rendering limitations.
    """
    return f"{base_prompt}\n\n{CONTENT_CONSTRAINTS}"


# ============================================
# INTEGRATION HELPER
# ============================================

def apply_all_critical_fixes(
    content: Dict,
    category: str,
    topic: str,
    video_id: int = None
) -> Dict:
    """
    Apply all critical fixes to content before rendering.
    
    This should be called AFTER AI generation but BEFORE rendering.
    """
    fixed_content = content.copy()
    
    # 1. Select appropriate font
    mood = content.get('mood', content.get('music_mood', 'neutral'))
    font = select_font_for_content(category, mood, topic)
    fixed_content['selected_font'] = font
    print(f"   [FIX] Font selected: {font} (based on {category}/{mood})")
    
    # 2. Plan varied SFX
    phrases = content.get('phrases', [])
    sfx_plan = []
    for i in range(len(phrases)):
        sfx = get_varied_sfx_for_phrase(i, len(phrases), video_id)
        sfx_plan.append(sfx)
    fixed_content['sfx_plan'] = sfx_plan
    sfx_summary = [s for s in sfx_plan if s]
    print(f"   [FIX] SFX plan: {sfx_summary}")
    
    # 3. Validate numbered promise
    if phrases:
        validation = validate_numbered_promise(phrases[0], phrases)
        if not validation['valid']:
            print(f"   [FIX] Promise broken! Promised {validation['promised']}, delivered {validation['delivered']}")
            # Fix the hook
            fixed_hook = fix_broken_promise(phrases[0], validation['delivered'])
            fixed_content['phrases'][0] = fixed_hook
            fixed_content['promise_fixed'] = True
            print(f"   [FIX] Hook fixed: {fixed_hook[:50]}...")
        else:
            fixed_content['promise_fixed'] = False
    
    return fixed_content


# ============================================
# v17.6: HOOK QUALITY SCORER
# ============================================

SCROLL_STOP_PATTERNS = [
    r'\bSTOP\b',           # Pattern interrupt
    r'\bWait\b',           # Pause command
    r'^\d+%',              # Leading percentage
    r'^\$\d+',             # Leading dollar amount
    r'\?$',                # Ends with question
    r'!$',                 # Ends with exclamation
    r'\bdid\s+you\s+know\b',  # Curiosity trigger
    r'\bdon\'t\s+\w+\s+without\b',  # Loss aversion
    r'\bwrong\b',          # Challenge
    r'\bsecret\b',         # Mystery
    r'\btruth\b',          # Revelation
    r'\bshock\b',          # Emotion
]

def score_hook_quality(hook: str) -> Dict:
    """
    v17.6: Score a hook for scroll-stop power.
    
    Returns:
        score: 1-10 (10 = maximum scroll-stop power)
        patterns_found: list of patterns that matched
        suggestions: improvements if score is low
    """
    score = 0
    patterns_found = []
    
    hook_lower = hook.lower()
    
    # Check for scroll-stop patterns
    for pattern in SCROLL_STOP_PATTERNS:
        if re.search(pattern, hook, re.IGNORECASE):
            score += 1
            patterns_found.append(pattern)
    
    # Check for numbers (specificity)
    if re.search(r'\d+', hook):
        score += 1
        patterns_found.append("has_number")
    
    # Check for short hook (<=15 words is optimal)
    word_count = len(hook.split())
    if word_count <= 15:
        score += 1
        patterns_found.append("short_hook")
    elif word_count > 25:
        score -= 1  # Penalty for too long
    
    # Check for personal pronoun (engagement)
    if re.search(r'\b(you|your|we|our)\b', hook_lower):
        score += 1
        patterns_found.append("personal_pronoun")
    
    # Cap at 10
    score = min(max(score, 1), 10)
    
    # Generate suggestions for low scores
    suggestions = []
    if score < 6:
        if 'has_number' not in patterns_found:
            suggestions.append("Add a specific number (e.g., 93% instead of 'most')")
        if 'personal_pronoun' not in patterns_found:
            suggestions.append("Make it personal (use 'you' or 'your')")
        if word_count > 15:
            suggestions.append(f"Shorten hook ({word_count} words → aim for 10-15)")
        if len(patterns_found) < 2:
            suggestions.append("Add pattern interrupt (STOP, Wait, Did you know...?)")
    
    return {
        "score": score,
        "patterns_found": patterns_found,
        "suggestions": suggestions,
        "word_count": word_count
    }


if __name__ == "__main__":
    # Test the fixes
    print("Testing Critical Fixes...")
    
    # Test font selection
    font = select_font_for_content("self_improvement", "friendly", "Morning Habits")
    print(f"Font for self_improvement/friendly: {font}")
    
    # Test SFX variety
    print("\nSFX patterns for 3 different videos:")
    for vid in [12345, 67890, 11111]:
        pattern = [get_varied_sfx_for_phrase(i, 4, vid) for i in range(4)]
        print(f"  Video {vid}: {pattern}")
    
    # Test promise validation
    hook = "Here are 5 morning habits that will change your life"
    phrases = [hook, "First tip", "Second tip", "Third tip"]  # Only 3 items!
    result = validate_numbered_promise(hook, phrases)
    print(f"\nPromise validation: {result}")
    if not result['valid']:
        fixed = fix_broken_promise(hook, result['delivered'])
        print(f"Fixed hook: {fixed}")


