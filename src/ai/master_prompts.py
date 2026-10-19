#!/usr/bin/env python3
"""
ViralShorts Factory - MASTER PROMPT ENGINEERING
Ultra-optimized prompts for maximum viral potential.

Each prompt is crafted using advanced prompt engineering techniques:
1. Role priming (expert persona)
2. Chain of thought reasoning
3. Few-shot examples
4. Constraint specification
5. Output format enforcement
6. Anti-hallucination guards
7. Emotional/psychological triggers
"""

import os
import json
import re
import warnings
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Suppress google.generativeai deprecation warning (will migrate to google.genai later)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# Dynamic model selection
try:
    from src.quota.quota_optimizer import get_best_gemini_model, get_best_groq_model
except ImportError:
    def get_best_gemini_model(api_key=None):
        return "gemini-2.5-flash"
    def get_best_groq_model(api_key=None):
        return "llama-3.3-70b-versatile"

# Gemini as fallback for when Groq fails
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


def strip_emojis(text: str) -> str:
    """Remove ALL emojis and special characters that don't render."""
    # Comprehensive emoji and symbol removal
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"  # dingbats
        u"\U000024C2-\U0001F251"  # enclosed
        u"\U0001f926-\U0001f937"  # people
        u"\U00010000-\U0010ffff"  # supplementary
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()


# =============================================================================
# MASTER PROMPT: Viral Topic Generation
# =============================================================================

VIRAL_TOPIC_PROMPT = """You are MrBeast's head content strategist combined with Robert Cialdini (psychology), 
James Clear (actionable advice), and Alex Hormozi (bold claims that deliver).
You've created content with 50 BILLION views. You understand MAXIMUM VIRALITY.

Your task: Generate video ideas that are IMPOSSIBLE TO SCROLL PAST and DELIVER REAL VALUE.

CURRENT CONTEXT:
- Date: {date}
- Day: {day_of_week}  
- Season: {season}
- Trending themes: {trending_themes}

===== MAXIMUM VIRALITY MINDSET (v17.9.9) =====
Your content must trigger these PSYCHOLOGICAL RESPONSES:
1. PATTERN INTERRUPT: "Wait, what?!" - Stop their thumb mid-scroll
2. IDENTITY THREAT: "Am I doing this wrong?" - Challenge their self-image
3. STATUS BOOST: "I'll look smart sharing this" - Shareable insight
4. URGENT FOMO: "I need to know this NOW" - Immediate action required
5. TRIBAL DEBATE: "I disagree/agree strongly" - Polarizing (but truthful) stance

===== AGGRESSIVE BUT TRUTHFUL HOOKS =====
Take BOLD STANCES backed by REAL logic. Don't be vanilla - be memorable!

WEAK (forgettable): "Here's a tip to save money"
STRONG (viral): "Banks pray you never learn this. It's costing you $500/year."

WEAK: "Ways to be more productive"
STRONG: "If you check email before 10am, you've already failed today."

WEAK: "How to sleep better"
STRONG: "Your phone is destroying your sleep. Put it 10 feet away tonight."

The difference: STRONG takes a STANCE, creates TENSION, makes them PROVE you wrong.

===== THE PROMISE-PAYOFF CONTRACT (CRITICAL!) =====
Every viral video makes a PROMISE in the hook and DELIVERS in the content.
AGGRESSIVE hooks are only viral if you DELIVER. Empty aggression = death.

❌ NEVER DO THIS:
- "Here's an amazing strategy..." (without explaining the strategy)
- "Learn this powerful technique..." (without teaching the technique)
- "Scientists discovered..." (without saying what they discovered)
- "You won't believe..." (and then not delivering the surprise)

✅ ALWAYS DO THIS:
- "The 2-minute rule: Any task under 2 minutes, do it NOW. I did 47 yesterday."
- "Your willpower crashes at 3pm. Schedule hard tasks before noon."
- "You've walked past 36 murderers. Based on crime rates, it's mathematically certain."

===== NUMBERED PROMISE RULE (CRITICAL - DO NOT VIOLATE!) =====
If your hook/title mentions a NUMBER of items, the content MUST contain EXACTLY that many items!

❌ BROKEN PROMISE (will get flagged!):
- Hook: "7 Weird Christmas Traditions" → Content only mentions 2 traditions
- Hook: "5 Money Secrets" → Content only explains 1 secret
- Hook: "3 Signs You're..." → Content only gives 1 sign

✅ DELIVERED PROMISE:
- Hook: "3 Signs You're Smarter" → Content: "First: [sign 1]. Second: [sign 2]. Third: [sign 3]."
- Hook: "5 Money Hacks" → Content lists all 5 hacks with clear transitions

VALIDATION: If you use a number N in the hook, COUNT the distinct items in your content. 
If count < N, either: (a) add more items, or (b) change the hook to match the count.
SAFER APPROACH: Use "THIS one trick" or "The secret" instead of numbered lists if unsure.

===== VALUE-FIRST CONTENT STRUCTURE =====
HOOK (2 sec): Shocking specific claim with a NUMBER or FACT
BUILD (5 sec): Context that increases tension
DELIVER (10 sec): THE ACTUAL VALUE - specific steps, numbers, proof
REINFORCE (3 sec): Why this matters to THEM personally
CTA (2 sec): Question that makes them reflect/comment

===== CONTENT REQUIREMENTS (MAXIMUM IMPACT) =====
1. Include AT LEAST 2 specific numbers (percentages, times, counts)
2. Give ONE clear actionable step they can take in the NEXT 5 MINUTES
3. Explain the MECHANISM (why/how it works) - this builds trust
4. Make them feel SMARTER and SUPERIOR after watching
5. NO empty promises - if you say "here's how," you MUST explain how
6. CREATE URGENCY: "Before your next paycheck" / "Starting tonight" / "Before Monday"
7. CHALLENGE BELIEFS: "Everyone does X, but here's why that's backwards"
8. NAME THE ENEMY: "Banks" / "Your boss" / "Social media" / "Traditional advice"
9. BE SPECIFIC: Not "a lot of money" but "$500" / Not "often" but "3x per week"
10. END WITH DEBATE: Your CTA should be a question people WANT to answer

===== BELIEVABILITY & QUALITY (CRITICAL!) =====
You are creating content for SKEPTICAL viewers. Everything must feel REAL and TRUSTWORTHY.

NUMBERS MUST BE:
- REALISTIC: Use believable, commonly-cited numbers (not random like $3333 or 47.3%)
- ROUND & MEMORABLE: $500, 80%, 1000+, 30 days (NOT $487, 83.7%, 947, 29 days)
- VERIFIABLE: Could someone Google this? If not, soften the claim.
- STICKY: Easy to remember and share

❌ AWKWARD NUMBERS (feel fake/AI-generated):
- "You're losing $3333 every year" (why that random number?)
- "47.3% of people experience this" (too precise to be believable)
- "In 1847, scientists discovered..." (random year)

✅ BELIEVABLE NUMBERS (feel researched/real):
- "You're losing $500+ every year" (round, memorable)
- "Nearly half of people experience this" (natural phrasing)
- "In the 1990s, scientists discovered..." (believable range)

THE SKEPTICAL VIEWER TEST:
Before using ANY claim, ask: "Would a skeptical viewer think 'this sounds made up'?"
If yes → use softer language, round numbers, or cite a source type ("Harvard study")

===== SHORT-FORM VIDEO READABILITY (CRITICAL!) =====
This content will be displayed as TEXT on mobile screens. Optimize for VISUAL READABILITY:

1. NUMBERS AS DIGITS: Always use "500" not "five hundred", "3pm" not "three pm", "$50" not "fifty dollars"
2. SHORT SENTENCES: Maximum 12 words per sentence. Viewers read while watching.
3. NO COMPLEX WORDS: Use "use" not "utilize", "get" not "obtain", "show" not "demonstrate"
4. CONVERSATIONAL: Write like texting a friend, not writing an essay
5. PUNCHY PHRASES: Each sentence should hit hard. No filler words.
6. SCANNABLE: Viewer should understand the point in 2 seconds of reading
7. NATURAL HUMAN SPEECH: Would a real person say this? If it sounds robotic, rewrite it.

BAD: "Studies have demonstrated that approximately five hundred individuals..."
GOOD: "500 people tested this. 73% saw results in 2 weeks."

BAD: "You are losing exactly $3,847.52 per year on hidden fees..."
GOOD: "You're losing $500+ a year on hidden fees. Here's how to stop it."

===== B-ROLL KEYWORDS =====
- Highly specific ("person staring at phone in dark room" not "technology")
- Emotionally matched to content
- Available on stock sites

Generate {count} video ideas. For EACH video:

CRITICAL: The "hook" and "content" are SEPARATE! Do NOT repeat the hook inside the content!
- hook = The opening attention-grabber (spoken first)
- content = The rest of the video (spoken after the hook)

{{
    "topic": "2-4 word topic name",
    "video_type": "scary_fact|money_fact|psychology_fact|life_hack|mind_blow|science_fact|history_mystery|space_fact|animal_fact|weird_law|unsolved_mystery|would_you_rather|this_or_that|crazy_experiment|world_record|optical_illusion",
    "hook": "7-10 word attention grabber - this is spoken FIRST - NO EMOJIS",
    "content": "The REST of the video AFTER the hook. Do NOT repeat the hook here! Include: mechanism/evidence, actionable takeaway. 50-80 words. NO EMOJIS.",
    "the_payoff": "The ONE specific thing they learn/can do after watching",
    "call_to_action": "Reflective question that drives comments",
    "broll_keywords": ["specific visual 1", "specific visual 2", "specific visual 3", "specific visual 4"],
    "music_mood": "suspense|dramatic|inspirational|energetic|emotional",
    "virality_score": 1-10,
    "psychological_triggers": ["trigger1", "trigger2"],
    "why_viral": "One sentence on the psychology of why this spreads"
}}

Return a JSON array of {count} objects. No markdown, no emojis, no explanations outside JSON."""


# =============================================================================
# MASTER PROMPT: Content Quality Evaluation
# =============================================================================

CONTENT_EVALUATION_PROMPT = """You are a YouTube Shorts algorithm expert who has analyzed 10 million viral videos. You understand exactly what makes content spread.

Evaluate this video content for viral potential:

HOOK: "{hook}"
CONTENT: "{content}"
TYPE: {video_type}

Score each dimension (1-10) and explain:

1. SCROLL-STOPPING POWER (Does the hook make you stop scrolling?)
   - First 0.5 seconds must be UNMISSABLE
   - Pattern interrupt or curiosity gap required
   
2. INFORMATION VALUE (Does viewer learn something valuable?)
   - Not just "interesting" but USEFUL or SURPRISING
   - Must feel like insider knowledge
   
3. EMOTIONAL INTENSITY (Does it trigger strong emotion?)
   - Fear, anger, joy, surprise, or awe
   - Weak emotions = no shares
   
4. SHAREABILITY (Would someone send this to a friend?)
   - "You HAVE to see this"
   - Must create social currency
   
5. COMMENT BAIT (Does it provoke discussion?)
   - Controversial without being offensive
   - Easy to have an opinion

Return JSON:
{{
    "scroll_stop": {{"score": 1-10, "reason": "why"}},
    "info_value": {{"score": 1-10, "reason": "why"}},
    "emotion": {{"score": 1-10, "reason": "why"}},
    "shareability": {{"score": 1-10, "reason": "why"}},
    "comment_bait": {{"score": 1-10, "reason": "why"}},
    "overall": 1-10,
    "verdict": "VIRAL|GOOD|WEAK|TRASH",
    "improvements": ["specific improvement 1", "specific improvement 2"]
}}"""


# =============================================================================
# MASTER PROMPT: B-roll Keyword Extraction
# =============================================================================

BROLL_KEYWORDS_PROMPT = """You are a professional video editor who has worked on Netflix documentaries. You understand visual storytelling.

For this video content, suggest B-roll footage that will:
1. ENHANCE the emotional impact
2. ILLUSTRATE concepts visually
3. MAINTAIN viewer attention
4. CREATE professional production value

CONTENT: "{content}"
MOOD: {mood}

Think about:
- What visuals would a BBC documentary use?
- What creates MOVEMENT and ENERGY on screen?
- What colors and lighting support the mood?
- What's AVAILABLE on stock sites (Pexels, Pixabay)?

BAD B-ROLL: "abstract", "motion", "colorful" (too generic)
GOOD B-ROLL: "dramatic storm clouds time lapse", "person looking worried close up", "money falling slow motion"

Return EXACTLY 5 specific, searchable B-roll descriptions:
{{
    "primary": "Most important visual - shown most of video",
    "secondary": "Supporting visual for variety",
    "detail": "Close-up or detail shot",
    "atmosphere": "Mood-setting background",
    "transition": "Visual for transitions",
    "search_terms": ["exact search term 1", "exact search term 2", "exact search term 3", "exact search term 4", "exact search term 5"]
}}"""


# =============================================================================
# MASTER PROMPT: Voiceover Script
# =============================================================================

VOICEOVER_PROMPT = """You are Morgan Freeman's dialogue coach + a TikTok creator with 50M followers.

Write a voiceover that DELIVERS VALUE, not just promises it.

CONTENT TO ADAPT: "{content}"
TARGET: 15-30 seconds (50-80 words)

===== THE VALUE TEST =====
Before writing, ask: "What does the viewer LEARN or GAIN from this?"
If the answer is vague ("motivation" / "awareness"), rewrite until it's SPECIFIC.

GOOD: "Viewer learns the 2-minute rule and can use it today"
BAD: "Viewer feels inspired to be productive"

===== STRUCTURE =====
1. HOOK (1 sec): Surprising claim that STOPS the scroll
2. BUILD (3 sec): Create anticipation for the payoff
3. DELIVER (10 sec): THE ACTUAL VALUE - specific, actionable, memorable
4. REINFORCE (3 sec): Why this matters to THEM
5. CTA (2 sec): Question that drives comments

===== STYLE RULES =====
- Short sentences (5-10 words max)
- Pauses as "..." for emphasis
- CAPS for key words
- NO filler words
- Conversational but confident
- Numbers and specifics always

===== BELIEVABILITY CHECK (CRITICAL!) =====
Before writing, pass EVERY claim through the SKEPTICAL VIEWER test:
- Would someone watching think "this sounds made up"?
- Are the numbers REALISTIC and MEMORABLE? (round numbers: $500, 80%, 30 days)
- Does anything sound robotic or awkward when read aloud?
- Would a human naturally say this in conversation?

❌ FAILS THE TEST:
- "You're losing $3,847 every year" (random number = fake)
- "Studies from 1847 proved..." (random year = suspicious)  
- "This affects exactly 47.3% of people" (too precise = AI garbage)

✅ PASSES THE TEST:
- "You're losing over $500 a year" (round, believable)
- "For decades, scientists have known..." (natural phrasing)
- "Nearly half of people experience this" (conversational)

===== MOBILE READABILITY (CRITICAL!) =====
The script will be displayed as TEXT OVERLAY on mobile screens:
- ALWAYS use digits: "500" not "five hundred", "$20" not "twenty dollars"
- ALWAYS use symbols: "$", "%", "&" - they're shorter and scannable
- Keep each phrase under 10 words - this becomes one text screen
- Use everyday words: "use" not "utilize", "buy" not "purchase"
- Be specific: "3pm" not "afternoon", "47 people" not "many people"

BAD: "There's a technique you should learn about..."
GOOD: "The 2-minute rule. If it takes less than 2 minutes... do it NOW."

BAD: "Studies show this really works for most people."
GOOD: "MIT tested 1,200 students. 73% improved in 2 weeks."

BAD: "You could save approximately five hundred dollars annually."
GOOD: "Save $500/year with this 1 trick."

BAD: "You are losing exactly $3,333 on crypto fees every year."
GOOD: "Crypto fees are eating $500+ of your money. Here's the fix."

Return JSON:
{{
    "script": "Complete script with pauses as ...",
    "word_count": number,
    "estimated_duration_seconds": number,
    "the_value_delivered": "ONE sentence describing what viewer gains",
    "hook_line": "First line only",
    "closing_line": "Last line only"
}}"""


# =============================================================================
# MASTER PROMPT: Platform-Specific Optimization (#6)
# =============================================================================

PLATFORM_OPTIMIZATION_PROMPT = """You are a MULTI-PLATFORM STRATEGIST who knows the differences between platforms.

=== ORIGINAL CONTENT ===
Title: {title}
Hook: {hook}
CTA: {cta}
Platform: {platform}

=== PLATFORM DIFFERENCES ===
YOUTUBE SHORTS:
- Formal-ish, educational tone works well
- Subscribe CTAs are effective
- Hashtags: #shorts required, 3-5 relevant tags
- Longer hooks OK (2-3 seconds)

DAILYMOTION:
- More casual, entertainment-focused audience
- Lower competition = can be more niche
- Less emphasis on subscribe CTAs
- Similar format to YouTube

TIKTOK (future):
- Very casual, trend-driven
- "Duet this" / "Stitch this" CTAs
- Trending sounds matter
- Hook must be < 1 second

=== OUTPUT JSON ===
{{
    "optimized_title": "platform-specific title",
    "optimized_hook": "adjusted hook for platform",
    "optimized_cta": "platform-appropriate CTA",
    "hashtags": ["#shorts", "#relevant", "#tags"],
    "platform_tips": ["tip for this platform"]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Contextual Event Awareness (#15)
# =============================================================================

CONTEXTUAL_AWARENESS_PROMPT = """You are a CULTURAL SENSITIVITY and TIMING expert.

=== CONTENT ===
Topic: {topic}
Hook: {hook}
Date: {current_date}

=== CHECK FOR ===
1. SENSITIVE DATES: Is today a day we should avoid certain topics?
   - Memorial days, tragedies anniversaries, religious holidays
   
2. OPPORTUNITY DATES: Is there an event we can leverage?
   - Sports events, award shows, product launches, holidays
   
3. REGIONAL SENSITIVITY: Global audience considerations
   - Avoid US-centric assumptions
   - Be aware of international events

4. TRENDING OPPORTUNITIES: Any current events to reference?

=== OUTPUT JSON ===
{{
    "is_sensitive": true/false,
    "sensitivity_reason": "why sensitive" or null,
    "is_opportunity": true/false,
    "opportunity_reason": "event to leverage" or null,
    "modifications_needed": ["change 1"] or [],
    "proceed": true/false,
    "timing_score": 1-10
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Cross-Promotion Network (#19)
# =============================================================================

CROSS_PROMOTION_PROMPT = """You are a CONTENT NETWORK STRATEGIST.

=== CURRENT VIDEO ===
Topic: {current_topic}
Category: {category}

=== RECENT VIDEOS (for cross-promotion) ===
{recent_videos}

=== TASK ===
Suggest how to connect this video to our other content:
1. Related video to mention in description
2. Series/theme to establish
3. "Watch next" suggestion for end screen

=== OUTPUT JSON ===
{{
    "related_video": "title of related video from list" or null,
    "description_mention": "Check out our video on [X] for more!" or null,
    "series_opportunity": "This could be part of [X] series" or null,
    "end_screen_suggestion": "Pair with [video] for end screen"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Failed Content Recycling (#23)
# =============================================================================

CONTENT_RECYCLING_PROMPT = """You are a CONTENT RESURRECTION SPECIALIST.
This video underperformed. Diagnose WHY and prescribe a FIX.

=== FAILED VIDEO ===
Title: {title}
Hook: {hook}
Topic: {topic}
Views: {views} (our average: {avg_views})
Engagement: {engagement}

=== AUTOPSY - Find the cause of death ===
1. Was the hook weak?
2. Was the topic stale?
3. Was the title unclickable?
4. Was the content thin?
5. Was timing bad?

=== RESURRECTION PLAN ===
{{
    "diagnosis": "why it failed",
    "salvageable": true/false,
    "resurrection_plan": {{
        "new_angle": "fresh approach to same topic",
        "new_hook": "stronger hook",
        "new_title": "more clickable title",
        "timing_suggestion": "when to republish"
    }},
    "effort_score": 1-10 (10 = too much work)
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Seasonal Content Calendar (#27 - v9.5)
# =============================================================================

SEASONAL_CALENDAR_PROMPT = """You are a CONTENT CALENDAR strategist for viral short-form video.

=== TODAY'S DATE ===
{current_date}

=== YOUR TASK ===
Identify the TOP 5 content opportunities for the NEXT 7 DAYS based on:

1. UPCOMING HOLIDAYS & EVENTS
   - Major holidays (Christmas, New Year, Valentine's, Halloween, etc.)
   - Awareness days/months (Mental Health Month, Earth Day, etc.)
   - Sports events (Super Bowl, Olympics, World Cup, etc.)
   - Pop culture (award shows, movie releases, etc.)

2. SEASONAL RELEVANCE
   - Weather changes, seasonal activities
   - Back-to-school, summer vacation, etc.
   - Year-end content (lists, resolutions, reviews)

3. PREDICTABLE VIRAL PATTERNS
   - End of week: "Weekend plans" content
   - Mondays: Motivation/productivity content
   - Pay days: Money/finance content
   - Full moon: Astrology/weird content

=== OUTPUT REQUIREMENTS ===
For each opportunity, provide:
- Specific content angle (not just "Christmas content")
- Why it will work NOW (timing is everything)
- Hook idea

{{
    "content_opportunities": [
        {{
            "event": "specific event/date",
            "days_until": number,
            "content_angle": "specific viral angle",
            "hook_idea": "hook line",
            "urgency": "high/medium/low",
            "category": "psychology/money/life_hack/etc"
        }}
    ],
    "seasonal_mood": "festive/reflective/energetic/cozy",
    "avoid_topics": ["topics to avoid right now"],
    "overall_strategy": "one sentence on content approach this week"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Series Detection & Continuation (#33 - v9.5)
# =============================================================================

SERIES_CONTINUATION_PROMPT = """You are a CONTENT STRATEGIST specializing in SERIES and FRANCHISES.

=== HIGH-PERFORMING VIDEO ===
Title: {title}
Topic: {topic}
Category: {category}
Views: {views} (average: {avg_views})
Performance: {performance_multiplier}x average

=== THE SERIES OPPORTUNITY ===
When content performs well, there's hidden demand for MORE. Your job is to identify:
1. What specifically resonated (the "magic ingredient")
2. How to capture that magic again WITHOUT being repetitive
3. Whether this should be a "Part 2" or a new angle

=== SERIES TYPES ===
1. NUMBERED SERIES: "Part 1", "Part 2" (for cliffhangers, deep topics)
2. THEMED SERIES: Same category, different examples ("More Money Hacks")
3. DEPTH SERIES: Go deeper on one aspect ("Deep Dive: [Subtopic]")
4. FLIP SERIES: Opposite angle ("Why This DOESN'T Work")
5. AUDIENCE SERIES: "What You Asked For: [Viewer Questions]"

=== OUTPUT JSON ===
{{
    "magic_ingredient": "what specifically worked",
    "series_type": "numbered/themed/depth/flip/audience",
    "should_continue": true/false,
    "continuation_plan": {{
        "part2_topic": "specific topic for sequel",
        "part2_hook": "hook that references success",
        "part2_angle": "how it's different but related",
        "timing": "when to release (days from now)",
        "reference_original": true/false
    }},
    "series_name": "if this becomes a series, what to call it",
    "potential_parts": 3-5 (how many videos in this series),
    "confidence": "high/medium/low"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Engagement Reply Templates (#34 - v9.5)
# =============================================================================

ENGAGEMENT_REPLY_PROMPT = """You are a COMMUNITY MANAGER for a viral YouTube Shorts channel.

=== SAMPLE COMMENTS FROM OUR VIDEOS ===
{sample_comments}

=== YOUR TASK ===
Create reply templates that:
1. Sound HUMAN (not robotic/corporate)
2. Encourage FURTHER engagement (more replies, follows)
3. Build COMMUNITY (make people feel seen)
4. Are EFFICIENT (we can copy-paste and slightly customize)

=== COMMENT CATEGORIES ===
Identify which of these categories appear in the comments:

1. PRAISE: "Great video!", "Love this!", "So helpful!"
   - Acknowledge, ask follow-up question

2. QUESTIONS: "How do I...?", "What about...?"
   - Answer briefly, point to more content

3. DISAGREEMENT: "Actually...", "This is wrong..."
   - Stay curious, not defensive

4. REQUESTS: "Can you make a video about...?"
   - Validate, ask for more details

5. PERSONAL STORIES: "This happened to me..."
   - Empathize, ask how it turned out

6. TROLLS: "Fake", "AI slop", negative spam
   - Usually ignore, but sometimes humor works

=== OUTPUT JSON ===
{{
    "comment_categories_found": ["praise", "questions", "etc"],
    "templates": [
        {{
            "category": "praise",
            "trigger_phrases": ["great video", "love this"],
            "reply_templates": [
                "Thanks! 🙏 What topic should I cover next?",
                "Glad you liked it! Drop a follow for more"
            ]
        }}
    ],
    "high_priority_comments": [
        {{
            "comment": "exact comment to prioritize",
            "why_priority": "high engagement potential",
            "suggested_reply": "specific reply"
        }}
    ],
    "engagement_tips": ["tip 1", "tip 2"]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: B-Roll Relevance Scoring (#31 - v9.5)
# =============================================================================

BROLL_RELEVANCE_PROMPT = """You are a VIDEO EDITOR selecting B-roll for a short video.

=== PHRASE TO ILLUSTRATE ===
"{phrase}"

=== CONTENT CONTEXT ===
Topic: {topic}
Mood: {mood}
Video Type: {video_type}

=== B-ROLL OPTIONS FROM PEXELS ===
{broll_options}

=== SCORING CRITERIA ===
Rate each option 1-10:

10 = PERFECT: Directly shows what the phrase describes
8-9 = GREAT: Strongly related, enhances understanding
6-7 = GOOD: Related, adds visual interest
4-5 = OK: Loosely related, generic but acceptable
1-3 = BAD: Unrelated or distracting

=== WHAT MAKES GOOD B-ROLL ===
✅ SHOWS the concept (not just illustrates it)
✅ Has MOVEMENT and energy
✅ Matches MOOD (dark for scary, bright for inspirational)
✅ HIGH QUALITY (not blurry or low-res)

❌ AVOID:
- Too literal (if talking about money, don't just show coins)
- Too abstract (random shapes, stock graphics)
- Wrong mood (happy people for a serious topic)
- Cliché (handshake for "partnership")

=== OUTPUT JSON ===
{{
    "scores": [
        {{"index": 1, "score": 8, "reason": "short reason"}}
    ],
    "best_option": index number,
    "avoid_options": [indices to skip],
    "alternative_search": "better search term if all options are poor"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Hook Word Analysis (#28 - v9.5)
# =============================================================================

HOOK_WORD_ANALYSIS_PROMPT = """You are a LINGUISTIC ANALYST studying viral video hooks.

=== HOOK PERFORMANCE DATA ===
{hook_data}

=== YOUR TASK ===
Analyze these hooks to find patterns:

1. POWER WORDS: Which words correlate with high views?
   - Emotional triggers (shocking, secret, hidden)
   - Urgency words (now, today, immediately)
   - Curiosity words (why, how, what if)

2. WEAK WORDS: Which words correlate with low views?
   - Vague words (thing, stuff, really)
   - Overused words (amazing, incredible)
   - Passive words (might, could, maybe)

3. STRUCTURAL PATTERNS: What hook structures work?
   - Question hooks: "Why do...?"
   - Statement hooks: "This is the..."
   - Challenge hooks: "You can't..."
   - Secret hooks: "The secret to..."

=== OUTPUT JSON ===
{{
    "power_words": ["word1", "word2"],
    "weak_words": ["avoid1", "avoid2"],
    "best_structures": [
        {{
            "pattern": "Why [X] is [unexpected thing]",
            "example": "Why your alarm is making you tired",
            "avg_performance": 1.5
        }}
    ],
    "recommendations": [
        "Always start with why/how/what",
        "Include a number in first 3 words"
    ]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Category Decay Analysis (#35 - v9.5)
# =============================================================================

CATEGORY_DECAY_PROMPT = """You are a TREND ANALYST tracking content category performance over time.

=== CATEGORY PERFORMANCE HISTORY ===
{category_history}

=== YOUR TASK ===
Analyze which categories are:
1. TRENDING UP: Growing in performance
2. STABLE: Consistent performance
3. DECLINING: Dropping in performance
4. SATURATED: Too much similar content

=== FACTORS TO CONSIDER ===
- Recent (last 7 days) performance vs. older
- Seasonal effects (holiday topics spike, then crash)
- Market saturation (everyone making same content)
- Algorithm changes (platform pushing certain types)

=== OUTPUT JSON ===
{{
    "category_status": {{
        "psychology": {{
            "trend": "up/stable/down",
            "recent_performance": 1.2,
            "recommendation": "increase/maintain/decrease output"
        }}
    }},
    "hot_categories": ["trending up categories"],
    "cool_categories": ["declining categories"],
    "rotation_suggestion": "which category to focus on next"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Emotional Arc Design (#37 - v10.0)
# =============================================================================

EMOTIONAL_ARC_PROMPT = """You are an EMOTIONAL STORYTELLING expert for viral short-form video.

=== VIDEO CONTENT ===
{content}

=== VIDEO TYPE ===
{video_type}

=== DESIGN THE EMOTIONAL JOURNEY ===
Map the viewer's emotional state across the video:

PHASE 1: HOOK (0-2 seconds)
- What emotion STOPS the scroll? (shock, curiosity, fear, confusion)
- How intense should it be? (1-10)

PHASE 2: BUILD (2-8 seconds)
- How does tension ESCALATE?
- What keeps them watching? (mystery, stakes, anticipation)

PHASE 3: PEAK (8-15 seconds)
- The emotional CLIMAX
- The "wow" or "aha" moment
- Maximum intensity point

PHASE 4: RESOLUTION (15-20 seconds)
- How do they FEEL after?
- Satisfied? Motivated? Curious for more?
- What action do they take?

=== OUTPUT JSON ===
{{
    "emotional_journey": [
        {{"phase": "hook", "emotion": "curiosity", "intensity": 7, "technique": "open loop"}},
        {{"phase": "build", "emotion": "anticipation", "intensity": 8, "technique": "raising stakes"}},
        {{"phase": "peak", "emotion": "surprise", "intensity": 10, "technique": "unexpected reveal"}},
        {{"phase": "resolution", "emotion": "satisfaction", "intensity": 6, "technique": "clear takeaway"}}
    ],
    "peak_moment_second": 12,
    "energy_curve": [6, 7, 8, 9, 10, 8, 7],
    "music_mood": "building_tension",
    "voice_direction": "start intrigued, build excitement, end confident",
    "pacing_notes": "quick cuts during build, slower at peak for impact"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Competitor Gap Analysis (#38 - v10.0)
# =============================================================================

COMPETITOR_GAP_PROMPT = """You are a COMPETITIVE INTELLIGENCE analyst for viral short-form content.

=== OUR RECENT TOPICS ===
{our_topics}

=== COMPETITOR TOPICS (from top viral channels) ===
{competitor_topics}

=== FIND THE GAPS ===
Identify content opportunities competitors are MISSING:

1. UNTAPPED NICHES
   - Subcategories no one is covering
   - Angles that are overlooked
   - Audiences being ignored

2. FRESH PERSPECTIVES
   - New takes on popular topics
   - Contrarian viewpoints
   - Unique combinations

3. TIMING OPPORTUNITIES
   - Topics that SHOULD be trending
   - Upcoming events no one is preparing for
   - Seasonal gaps

4. FORMAT INNOVATIONS
   - Styles competitors aren't using
   - Hook types that are underutilized

=== OUTPUT JSON ===
{{
    "untapped_niches": [
        {{"niche": "specific niche", "why_valuable": "reason", "hook_idea": "example hook"}}
    ],
    "fresh_angles": [
        {{"existing_topic": "what competitors do", "our_angle": "how we differentiate"}}
    ],
    "timing_opportunities": [
        {{"topic": "time-sensitive topic", "deadline": "when to post", "reason": "why now"}}
    ],
    "content_recommendations": [
        {{"topic": "specific topic", "priority": "high/medium/low", "confidence": 0.8}}
    ],
    "saturated_topics_to_avoid": ["topic1", "topic2"]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Description SEO (#39 - v10.0)
# =============================================================================

DESCRIPTION_SEO_PROMPT = """You are a YOUTUBE SEO expert specializing in Shorts optimization.

=== VIDEO INFO ===
Title: {title}
Category: {category}
Content Summary: {content_summary}

=== OPTIMIZE FOR YOUTUBE SEARCH ===
Create a description that:
1. Includes PRIMARY KEYWORD in first 25 characters
2. Contains 3-5 RELATED KEYWORDS naturally
3. Has a clear CALL-TO-ACTION
4. Is UNDER 200 characters (Shorts sweet spot)
5. Includes RELEVANT HASHTAGS

=== SEO PRINCIPLES ===
- YouTube reads the first 125 characters most heavily
- Keywords should flow naturally, not stuffed
- Hashtags at end, max 3-5
- Include channel CTA if space permits

=== OUTPUT JSON ===
{{
    "optimized_description": "The full SEO-optimized description",
    "primary_keyword": "main search term",
    "secondary_keywords": ["keyword2", "keyword3", "keyword4"],
    "cta": "the call-to-action used",
    "hashtags": ["#tag1", "#tag2", "#tag3"],
    "character_count": 150,
    "seo_score": 8,
    "reasoning": "why this description ranks well"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Viral Velocity Prediction (#45 - v10.0)
# =============================================================================

VIRAL_VELOCITY_PROMPT = """You are a VIRAL PREDICTION expert who has analyzed 10 million YouTube Shorts.

=== VIDEO TO ANALYZE ===
Title: {title}
Hook: {hook}
Category: {category}
Content Preview: {content_preview}
Channel Average Views: {avg_views}

=== PREDICT VIRAL VELOCITY ===
Analyze these viral factors:

1. SCROLL-STOP POWER (1-10)
   - Does the title/hook DEMAND attention?
   - Pattern interrupt? Curiosity gap? Shock value?

2. SHAREABILITY (1-10)
   - Would someone SEND this to a friend?
   - "You have to see this" factor?

3. COMMENT BAIT (1-10)
   - Does it PROVOKE discussion?
   - Easy to have an opinion?

4. TREND ALIGNMENT (1-10)
   - Is this topic CURRENTLY trending?
   - Riding a wave or creating one?

5. ALGORITHM FRIENDLINESS (1-10)
   - Will YouTube PUSH this?
   - High completion rate likely?

=== OUTPUT JSON ===
{{
    "viral_score": 7.5,
    "velocity_tier": "slow_burn" or "moderate" or "fast" or "explosive",
    "scores": {{
        "scroll_stop": 8,
        "shareability": 7,
        "comment_bait": 6,
        "trend_alignment": 8,
        "algorithm_friendly": 7
    }},
    "predicted_first_hour": 500,
    "predicted_first_day": 5000,
    "predicted_week_1": 25000,
    "confidence": 0.7,
    "strength_factors": ["strong hook", "trending topic"],
    "risk_factors": ["saturated category", "weak CTA"],
    "recommendation": "upload" or "improve_first",
    "improvements_if_needed": ["specific improvement"]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Thumbnail Text Optimization (#36 - v10.0)
# =============================================================================

THUMBNAIL_TEXT_PROMPT = """You are a THUMBNAIL OPTIMIZATION expert who has tested thousands of click-through variations.

=== VIDEO INFO ===
Title: {title}
Hook: {hook}
Category: {category}

=== LEARNED PATTERNS ===
Best performing style: {best_style}
Optimal word count: {optimal_words}
Top power words: {power_words}

=== DESIGN THUMBNAIL TEXT ===
Create text overlay that:
1. Is NOT the same as the title (adds new information)
2. Creates CURIOSITY or URGENCY
3. Uses proven power words
4. Is READABLE on mobile (short, bold)
5. Complements the visual

=== OUTPUT JSON ===
{{
    "primary_text": "THE MAIN TEXT",
    "secondary_text": "optional smaller text",
    "style": "ALL_CAPS" or "Title_Case",
    "word_count": 3,
    "power_words_used": ["SECRET"],
    "color_suggestion": "yellow on dark" or "white with shadow",
    "placement": "top" or "center" or "bottom",
    "reasoning": "why this text drives clicks"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Comment Sentiment Analysis (#40 - v10.0)
# =============================================================================

COMMENT_SENTIMENT_PROMPT = """You are a SENTIMENT ANALYSIS expert for YouTube comment sections.

=== COMMENTS TO ANALYZE ===
{comments}

=== ANALYZE SENTIMENT ===
Categorize each comment:
- POSITIVE: praise, thanks, love, support
- NEGATIVE: criticism, hate, accusations, complaints
- NEUTRAL: questions, observations, neither

=== EXTRACT INSIGHTS ===
1. What do viewers LOVE? (do more)
2. What do viewers CRITICIZE? (fix or avoid)
3. Any "AI detection" accusations? (quality red flag)
4. What are viewers REQUESTING?

=== OUTPUT JSON ===
{{
    "counts": {{
        "positive": 15,
        "negative": 3,
        "neutral": 7
    }},
    "sentiment_ratio": 5.0,
    "overall_sentiment": "positive" or "negative" or "mixed",
    "notable_positive": [
        {{"comment": "exact comment", "why_valuable": "insight"}}
    ],
    "notable_negative": [
        {{"comment": "exact comment", "issue": "what to fix"}}
    ],
    "audience_requests": ["topic they want", "feature they want"],
    "quality_concerns": ["any AI accusations or fake claims"],
    "actionable_insights": ["do more X", "avoid Y"]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Click Bait Optimization (#46-51 - v11.0)
# =============================================================================

CLICKBAIT_OPTIMIZATION_PROMPT = """You are a CLICK PSYCHOLOGY expert who understands what makes humans click.

=== CURRENT TITLE/HOOK ===
Title: {title}
Hook: {hook}
Category: {category}

=== OPTIMIZE FOR CLICKS ===
Apply these proven click triggers:

1. CURIOSITY GAP: Create a gap between what they know and what they want to know
   - Bad: "How to Save Money"
   - Good: "The $27 Bill Trick Banks Don't Want You to Know"

2. SPECIFICITY: Specific beats vague
   - Bad: "Lose Weight Fast"
   - Good: "The 4:30 AM Habit That Burns 300 Extra Calories"

3. NUMBER MAGIC: Use odd numbers and be specific
   - Bad: "Tips to Be Happier"
   - Good: "7 Weird Things Happy People Do at 6 AM"

4. POWER WORDS: shock, secret, truth, hidden, never, always, proven
5. PERSONAL ATTACK: "You're doing X wrong" triggers defensiveness
6. FOMO: "Before it's too late", "Everyone knows except you"

=== OUTPUT JSON ===
{{
    "optimized_title": "click-optimized version",
    "optimized_hook": "scroll-stopping hook",
    "click_triggers_used": ["curiosity_gap", "specificity"],
    "power_words_added": ["secret", "hidden"],
    "predicted_ctr_improvement": "+35%",
    "why_it_works": "specific reason this version clicks"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: First 3 Seconds Retention (#52-57 - v11.0)
# =============================================================================

FIRST_SECONDS_PROMPT = """You are a RETENTION EXPERT who specializes in the first 3 seconds of short-form video.

=== CURRENT HOOK ===
{hook}

=== TOPIC ===
{topic}

=== THE CRITICAL FIRST 3 SECONDS ===
You have 2-3 seconds to:
1. STOP THE SCROLL - Pattern interrupt
2. CREATE NEED - They MUST know what happens
3. DELIVER VALUE - Give them something immediately

=== TECHNIQUES ===
1. SHOCKING STAT: Start with a mind-blowing number
   "93% of people do this wrong..."

2. DIRECT CHALLENGE: Attack their assumption
   "You're breathing wrong. Here's proof."

3. OPEN LOOP: Start a sentence they NEED completed
   "The one thing billionaires never..."

4. INSTANT VALUE: Give them something useful immediately
   "Your phone battery lasts 40% longer if..."

5. VISUAL SHOCK: Describe what they should see
   "Show something unexpected in frame 1"

=== OUTPUT JSON ===
{{
    "optimized_hook": "3-second hook text",
    "technique": "which technique used",
    "instant_value": "what value is delivered immediately",
    "open_loop": "what question is left unanswered",
    "visual_suggestion": "what should be on screen",
    "audio_suggestion": "what sound to use",
    "scroll_stop_score": 8
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Algorithm Optimization (#58-63 - v11.0)
# =============================================================================

ALGORITHM_OPTIMIZATION_PROMPT = """You are a YOUTUBE ALGORITHM EXPERT who understands exactly how Shorts get promoted.

=== CONTENT ===
{content}

=== CATEGORY ===
{category}

=== ALGORITHM SIGNALS TO MAXIMIZE ===

1. WATCH TIME: How to keep them watching
   - Tease what's coming
   - Progressive reveals
   - Save the best for 70% through

2. COMPLETION RATE: Get them to the end
   - Perfect pacing (not too fast, not slow)
   - Clear structure
   - Satisfying ending

3. RE-WATCH: Make them watch again
   - Hidden details to catch
   - Seamless loop
   - "Wait, did I miss something?"

4. ENGAGEMENT: Trigger comments/likes
   - Ask questions
   - Controversial (safe) takes
   - Relatable moments

5. SESSION TIME: Keep them on platform
   - End with related topic tease
   - Series connection

=== OUTPUT JSON ===
{{
    "watch_time_hooks": ["specific hook 1", "specific hook 2"],
    "completion_strategy": "how to ensure completion",
    "rewatch_trigger": "what makes them watch again",
    "comment_bait": "CTA to drive comments",
    "share_trigger": "why they'd share",
    "loop_friendly_ending": "how to make seamless loop",
    "algorithm_score": 8
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Visual Optimization (#64-68 - v11.0)
# =============================================================================

VISUAL_OPTIMIZATION_PROMPT = """You are a VISUAL DESIGN expert for short-form video.

=== VIDEO INFO ===
Category: {category}
Mood: {mood}
Topic: {topic}

=== OPTIMIZE VISUALS ===

1. COLOR PSYCHOLOGY
   - Red: urgency, excitement
   - Blue: trust, calm
   - Yellow: attention, optimism
   - Green: money, growth
   - Purple: luxury, mystery

2. TEXT READABILITY (Mobile-first)
   - Large fonts (60px+)
   - Max 5 words per line
   - High contrast
   - Shadow or outline

3. MOTION MATCHING
   - Calm content = gentle pans
   - Exciting content = quick cuts
   - Suspense = slow zooms

4. VISUAL VARIETY
   - Change every 3-4 seconds
   - Mix close-ups and wide shots
   - Use B-roll strategically

=== OUTPUT JSON ===
{{
    "primary_color": "#hex",
    "color_reasoning": "why this color",
    "text_style": "large_bold_shadow",
    "motion_level": "subtle/moderate/dynamic/intense",
    "cuts_per_video": 5,
    "b_roll_suggestions": ["type 1", "type 2"],
    "thumbnail_focus": "what to highlight",
    "mobile_optimized": true
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Content Quality Check (#69-74 - v11.0)
# =============================================================================

CONTENT_QUALITY_PROMPT = """You are a CONTENT QUALITY expert who ensures videos are valuable, believable, and memorable.

=== CONTENT TO REVIEW ===
{content}

=== QUALITY CHECKS ===

1. CREDIBILITY CHECK
   - Are claims believable?
   - Are numbers realistic?
   - Would a skeptic accept this?

2. ACTIONABLE VALUE
   - Is there a clear takeaway?
   - Can they DO something after watching?
   - Is the benefit clear?

3. STORY STRUCTURE
   - Is there a beginning, middle, end?
   - Is there tension/resolution?
   - Is the pacing right?

4. MEMORABILITY
   - Is there a sticky phrase?
   - Will they remember this tomorrow?
   - Is it quotable?

5. RELATABILITY
   - Can they see themselves in this?
   - Is the language natural?
   - Are examples relatable?

6. AUTHENTICITY (Anti-AI Slop)
   - Does it sound human?
   - Is it specific, not generic?
   - Would a real person say this?

=== OUTPUT JSON ===
{{
    "overall_quality_score": 7.5,
    "credibility": {{"score": 8, "issues": [], "fixes": []}},
    "actionability": {{"score": 7, "current_takeaway": "...", "better_takeaway": "..."}},
    "story_structure": {{"score": 8, "structure_type": "problem_solution"}},
    "memorability": {{"score": 6, "memory_hook": "suggested sticky phrase"}},
    "relatability": {{"score": 7, "add_phrase": "to make more relatable"}},
    "authenticity": {{"score": 8, "ai_slop_detected": [], "humanize": []}},
    "publish_ready": true,
    "priority_fix": "most important improvement"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Viral/Trend Optimization (#75-79 - v11.0)
# =============================================================================

VIRAL_TREND_PROMPT = """You are a VIRAL TREND expert who knows how to ride waves and create them.

=== TOPIC ===
{topic}

=== CATEGORY ===
{category}

=== TREND ANALYSIS ===

1. TREND LIFECYCLE
   - Emerging: Get in early for maximum growth
   - Growing: Good time, but move fast
   - Peak: Risky, might be too late
   - Declining: Avoid unless unique angle

2. EVERGREEN VS TRENDING
   - Balance: 60% evergreen, 40% trending
   - Evergreen = consistent views forever
   - Trending = spike then decline

3. VIRAL PATTERNS
   - Listicle: "5 Things..."
   - Myth bust: "This is actually wrong"
   - Comparison: "X vs Y"
   - Tutorial: "How to X in Y seconds"
   - Secret reveal: "The secret to..."

4. CULTURAL MOMENTS
   - Holidays, events, news
   - Memes and internet culture
   - Seasonal relevance

=== OUTPUT JSON ===
{{
    "topic_assessment": {{
        "is_trending": true or false,
        "lifecycle_phase": "emerging/growing/peak/declining",
        "is_evergreen": true or false,
        "trend_score": 7
    }},
    "viral_pattern": "which pattern to use",
    "cultural_tie_in": "relevant moment to reference" or null,
    "timing": "post now or wait",
    "angle_recommendation": "specific angle to take",
    "competition_level": "low/medium/high/saturated"
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Analytics Deep Dive (#80-84 - v11.0)
# =============================================================================

ANALYTICS_DEEP_DIVE_PROMPT = """You are an ANALYTICS EXPERT who finds hidden insights in video performance data.

=== PERFORMANCE DATA ===
{performance_data}

=== DEEP ANALYSIS ===

1. RETENTION ANALYSIS
   - Where do viewers drop off?
   - What causes spikes?
   - Pattern across videos?

2. CORRELATION DISCOVERY
   - Category vs Views
   - Title length vs CTR
   - Posting time vs Performance
   - Voice vs Retention

3. CHANNEL HEALTH
   - Trend: growing, stable, declining?
   - Shadow ban indicators?
   - Engagement ratio healthy?

4. GROWTH PREDICTION
   - Based on current trajectory
   - What would accelerate growth?
   - What's holding back growth?

=== OUTPUT JSON ===
{{
    "key_insights": [
        {{"insight": "description", "impact": "high/medium/low", "action": "what to do"}}
    ],
    "correlations": [
        {{"factor1": "...", "factor2": "...", "relationship": "positive/negative", "strength": 0.8}}
    ],
    "channel_health_score": 75,
    "health_indicators": {{"trend": "growing", "shadow_ban_risk": "low", "engagement": "healthy"}},
    "growth_prediction": {{"next_week": "+15%", "next_month": "+40%"}},
    "priority_actions": ["top action 1", "top action 2", "top action 3"]
}}

JSON ONLY."""


# =============================================================================
# MASTER PROMPT: Channel Growth Strategy (#85-89 - v11.0)
# =============================================================================

CHANNEL_GROWTH_PROMPT = """You are a CHANNEL GROWTH strategist who builds sustainable, long-term success.

=== CHANNEL DATA ===
{channel_data}

=== GROWTH STRATEGY ===

1. COMPETITOR RESPONSE
   - What are competitors doing well?
   - How can we differentiate?
   - What gaps can we fill?

2. NICHE AUTHORITY
   - What niche should we own?
   - How to become THE channel for X?
   - Expertise signaling

3. QUALITY CONSISTENCY
   - Every video must meet standards
   - No "throwaway" content
   - Build trust through reliability

4. UPLOAD CADENCE
   - Optimal frequency?
   - Consistency vs quantity?
   - Audience expectations

5. AUDIENCE LOYALTY
   - How to build returning viewers?
   - Community building
   - Recognizable brand elements

=== OUTPUT JSON ===
{{
    "niche_recommendation": "the niche we should own",
    "differentiation": "how we stand out from competitors",
    "authority_signals": ["ways to signal expertise"],
    "quality_threshold": 7,
    "optimal_cadence": "X videos per day/week",
    "brand_elements": ["consistent elements to use"],
    "loyalty_builders": ["ways to build returning viewers"],
    "growth_priority": "single most important action"
}}

JSON ONLY."""


# =============================================================================
# Main Class
# =============================================================================

class MasterContentGenerator:
    """Generate viral content using master prompts with multi-AI support."""
    
    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        
        # Initialize Groq (primary - faster)
        if HAS_GROQ and os.environ.get("GROQ_API_KEY"):
            self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # Initialize Gemini (backup - uses DYNAMIC model selection)
        if HAS_GEMINI and os.environ.get("GEMINI_API_KEY"):
            try:
                api_key = os.environ.get("GEMINI_API_KEY")
                genai.configure(api_key=api_key)
                # DYNAMIC MODEL SELECTION - no hardcoded model names
                model_name = get_best_gemini_model(api_key)
                self.gemini_client = genai.GenerativeModel(model_name)
                print(f"[OK] Gemini initialized ({model_name})")
            except Exception as e:
                print(f"[!] Gemini init failed: {e}")
    
    def _call_ai(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Make AI call with automatic fallback (Groq -> Gemini)."""
        
        # Try Groq first (faster) - DYNAMIC MODEL SELECTION
        if self.groq_client:
            try:
                groq_model = get_best_groq_model()
                response = self.groq_client.chat.completions.create(
                    model=groq_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.85  # High creativity
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ Groq failed: {e}, trying Gemini...")
        
        # Fallback to Gemini (higher quality)
        if self.gemini_client:
            try:
                response = self.gemini_client.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"⚠️ Gemini also failed: {e}")
        
        print("❌ All AI providers failed")
        return None
    
    def _parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response."""
        if not text:
            return None
        
        # Clean markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        try:
            return json.loads(text.strip())
        except:
            return None
    
    def generate_viral_topics(self, count: int = 3) -> List[Dict]:
        """
        Generate viral topic ideas using master prompt.
        
        IMPORTANT: Uses MULTIPLE SOURCES for trending data - NO HARDCODED TOPICS!
        Sources: Google Trends RSS, Reddit, AI predictions
        """
        # Try Multi-Source Trend Fetcher first (Google RSS + Reddit + AI)
        try:
            from multi_trend_fetcher import MultiTrendFetcher
            fetcher = MultiTrendFetcher()
            raw_trends = fetcher.fetch_all(count=count * 2)  # Get extra for filtering
            
            if raw_trends:
                print(f"[OK] Got {len(raw_trends)} trends from multi-source fetcher")
                
                # Convert to our topic format using AI
                topics = []
                for trend in raw_trends[:count]:
                    topic = self._trend_to_topic(trend)
                    if topic:
                        # Track source for analytics
                        topic["_source"] = trend.source  # "google", "reddit", "ai"
                        topics.append(topic)
                
                if topics:
                    return topics
        except Exception as e:
            print(f"[!] Multi-source trend fetcher unavailable: {e}")
        
        # Fallback: Use the AI Trend Fetcher (AI only)
        try:
            from ai_trend_fetcher import AITrendFetcher
            fetcher = AITrendFetcher()
            topics = fetcher.fetch_trending_topics(count)
            
            if topics:
                print(f"[OK] Got {len(topics)} trending topics from AI Trend Fetcher")
                return topics
        except Exception as e:
            print(f"[!] AI Trend Fetcher unavailable: {e}")
        
        # Fallback: Use the prompt system but let AI determine trends
        now = datetime.now()
        
        # DYNAMIC season context (no hardcoded topics!)
        month = now.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        # Let AI figure out what's trending - NO HARDCODED LIST
        trending = "USE YOUR KNOWLEDGE to determine what topics are currently trending and relevant"
        
        prompt = VIRAL_TOPIC_PROMPT.format(
            date=now.strftime("%B %d, %Y"),
            day_of_week=now.strftime("%A"),
            season=season,
            trending_themes=trending,
            count=count
        )
        
        result = self._call_ai(prompt)
        topics = self._parse_json(result)
        
        if isinstance(topics, list):
            # Strip emojis from all text fields
            for topic in topics:
                for key in ["hook", "content", "topic", "call_to_action"]:
                    if key in topic and topic[key]:
                        topic[key] = strip_emojis(str(topic[key]))
            return topics
        
        return []
    
    def _trend_to_topic(self, trend) -> Optional[Dict]:
        """Convert a trending topic to our video topic format using AI."""
        prompt = f"""Convert this trending topic into a viral short video script.

TRENDING TOPIC: {trend.topic}
SOURCE: {trend.source}
CATEGORY: {trend.category}
KEYWORDS: {', '.join(trend.keywords) if trend.keywords else 'N/A'}

Create a video that:
1. Uses this trend to deliver REAL VALUE
2. Includes specific numbers/facts
3. Has an actionable takeaway

Return JSON:
{{
    "topic": "{trend.topic[:50]}",
    "video_type": "{trend.category}_fact",
    "hook": "7-10 word attention grabber - NO EMOJIS",
    "content": "50-80 words of VALUE - NO EMOJIS",
    "the_payoff": "What viewer learns",
    "call_to_action": "Question for comments",
    "broll_keywords": ["visual1", "visual2", "visual3", "visual4"],
    "music_mood": "dramatic|suspense|inspirational",
    "virality_score": 8,
    "psychological_triggers": ["trigger1", "trigger2"],
    "why_viral": "Why this spreads"
}}

Only return valid JSON."""

        result = self._call_ai(prompt, max_tokens=800)
        topic = self._parse_json(result)
        
        if topic:
            # Strip emojis
            for key in ["hook", "content", "topic", "call_to_action"]:
                if key in topic and topic[key]:
                    topic[key] = strip_emojis(str(topic[key]))
            return topic
        
        return None
    
    def generate_broll_keywords(self, content: str, mood: str) -> Dict:
        """Generate specific B-roll keywords."""
        prompt = BROLL_KEYWORDS_PROMPT.format(content=content, mood=mood)
        result = self._call_ai(prompt, max_tokens=500)
        return self._parse_json(result) or {}
    
    def evaluate_content(self, hook: str, content: str, video_type: str) -> Dict:
        """Evaluate content quality."""
        prompt = CONTENT_EVALUATION_PROMPT.format(
            hook=hook, content=content, video_type=video_type
        )
        result = self._call_ai(prompt, max_tokens=800)
        return self._parse_json(result) or {}
    
    def generate_voiceover(self, content: str) -> Dict:
        """Generate optimized voiceover script."""
        prompt = VOICEOVER_PROMPT.format(content=content)
        result = self._call_ai(prompt, max_tokens=500)
        data = self._parse_json(result) or {}
        
        # Strip emojis from script
        if "script" in data:
            data["script"] = strip_emojis(data["script"])
        
        return data


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 MASTER PROMPT ENGINEERING TEST")
    print("=" * 60)
    
    # Direct API test
    api_key = os.environ.get("GROQ_API_KEY")
    print(f"API Key present: {bool(api_key)}")
    
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            print("✅ Groq client created")
            
            # Quick test
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say 'test successful' in 3 words"}],
                max_tokens=20
            )
            print(f"✅ API Test: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Error: {e}")
            client = None
    else:
        client = None
    
    gen = MasterContentGenerator()
    gen.client = client
    
    if not gen.client:
        print("⚠️ No AI client - set GROQ_API_KEY")
    else:
        print("\n📊 Generating viral topics...")
        topics = gen.generate_viral_topics(2)
        
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*50}")
            print(f"📹 Topic {i}: {topic.get('topic', 'N/A')}")
            print(f"   Hook: {topic.get('hook', 'N/A')}")
            print(f"   Type: {topic.get('video_type', 'N/A')}")
            print(f"   Virality: {topic.get('virality_score', 'N/A')}/10")
            print(f"   Triggers: {topic.get('psychological_triggers', [])}")
            print(f"   B-roll: {topic.get('broll_keywords', [])}")
            print(f"   Why viral: {topic.get('why_viral', 'N/A')}")

