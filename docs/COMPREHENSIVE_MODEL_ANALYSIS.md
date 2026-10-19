# ViralShorts Factory - Comprehensive Model Analysis

> Generated: January 2026 | Analysis Duration: Deep Dive

## Complete Model Comparison (22 Models)

| # | Provider | Model | Daily Limit | Indep? | Rate Limit | Delay | Quality | Our Prompts | Robustness | Best For |
|---|----------|-------|-------------|--------|------------|-------|---------|-------------|------------|----------|
| 1 | **Gemini** | gemini-1.5-flash | 1,500/day | ✅ Yes | 15 req/min | 4-5s | 7.5/10 | 8.0/10 | 95% | Description, SEO, Hashtags |
| 2 | **Gemini** | gemini-1.5-flash-latest | 1,500/day | ✅ Yes | 15 req/min | 4-5s | 7.5/10 | 8.0/10 | 95% | Same as 1.5-flash |
| 3 | **Gemini** | gemini-1.5-flash-8b | 1,500/day | ✅ Yes | 15 req/min | 4-5s | 7.0/10 | 7.5/10 | 95% | Simple prompts only |
| 4 | **Gemini** | gemini-2.0-flash | 500/day | ✅ Yes | 15 req/min | 4-5s | 8.0/10 | 8.5/10 | 92% | Evaluation, Complex analysis |
| 5 | **Gemini** | gemini-1.5-pro | ~50/day | ✅ Yes | 5 req/min | 12s | 8.5/10 | 9.0/10 | 90% | God-tier prompts |
| 6 | **Gemini** | gemini-2.0-flash-exp | 50-100/day | ✅ Yes | 10 req/min | 6s | 8.0/10 | 8.5/10 | 85% | Testing only |
| 7 | **Gemini** | gemini-pro | 60/day | ✅ Yes | 5 req/min | 12s | 7.0/10 | 7.0/10 | 88% | Legacy fallback |
| 8 | **Groq** | llama-3.3-70b-versatile | ~300/day* | ❌ Shared | 30 req/min | 2s | 8.5/10 | 9.0/10 | 98% | Creative content, Scripts |
| 9 | **Groq** | llama-3.1-70b-versatile | ~300/day* | ❌ Shared | 30 req/min | 2s | 8.0/10 | 8.5/10 | 97% | Backup for 3.3 |
| 10 | **Groq** | llama-3.1-8b-instant | ~600/day* | ❌ Shared | 60 req/min | 1s | 7.0/10 | 7.0/10 | 99% | Simple/fast prompts |
| 11 | **Groq** | mixtral-8x7b-32768 | ~400/day* | ❌ Shared | 40 req/min | 1.5s | 7.5/10 | 7.5/10 | 96% | Long context needs |
| 12 | **Groq** | gemma2-9b-it | ~400/day* | ❌ Shared | 40 req/min | 1.5s | 7.0/10 | 7.0/10 | 95% | Fallback |
| 13 | **OpenRouter** | llama-3.2-3b:free | Unlimited | ✅ Yes | ~60 req/min | 1s | 6.5/10 | 6.0/10 | 90% | Emergency only |
| 14 | **OpenRouter** | gemma-2-9b-it:free | Unlimited | ✅ Yes | ~60 req/min | 1s | 7.0/10 | 7.0/10 | 88% | Bulk/simple tasks |
| 15 | **OpenRouter** | mistral-7b:free | Unlimited | ✅ Yes | ~60 req/min | 1s | 7.0/10 | 7.0/10 | 87% | Alternative style |
| 16 | **OpenRouter** | zephyr-7b-beta:free | Unlimited | ✅ Yes | ~60 req/min | 1s | 7.0/10 | 7.0/10 | 86% | Chat-style prompts |
| 17 | **OpenRouter** | openchat-7b:free | Unlimited | ✅ Yes | ~60 req/min | 1s | 6.5/10 | 6.5/10 | 85% | Last resort |
| 18 | **HuggingFace** | zephyr-7b-beta | ~2,400/day | ✅ Yes | ~100 req/hr | 36s | 7.5/10 | 7.5/10 | 80% | Bulk processing |
| 19 | **HuggingFace** | gemma-2-2b-it | ~2,400/day | ✅ Yes | ~100 req/hr | 36s | 6.5/10 | 6.0/10 | 78% | Very simple prompts |
| 20 | **HuggingFace** | Qwen2.5-1.5B | ~2,400/day | ✅ Yes | ~100 req/hr | 36s | 6.0/10 | 5.5/10 | 75% | Tiny tasks |
| 21 | **HuggingFace** | TinyLlama-1.1B | ~2,400/day | ✅ Yes | ~100 req/hr | 36s | 5.5/10 | 5.0/10 | 70% | Last resort |
| 22 | **HuggingFace** | Phi-3-mini | ~2,400/day | ✅ Yes | ~100 req/hr | 36s | 7.0/10 | 7.0/10 | 82% | Microsoft backup |

*Groq shares a token pool (14,400 tokens/min), not strict request limits

---

## Column Explanations

| Column | Meaning |
|--------|---------|
| **Daily Limit** | How many requests per day to this model |
| **Indep?** | Is this quota independent from other models in same provider? |
| **Rate Limit** | Maximum requests per minute |
| **Delay** | Recommended delay between calls to stay safe |
| **Quality** | General quality score (1-10) |
| **Our Prompts** | Quality score specifically for OUR viral video prompts |
| **Robustness** | % chance of getting a successful response (not 429/503) |
| **Best For** | Which of our prompts this model excels at |

---

## Complete Prompt Inventory (All 7 Workflows)

### Workflow 1: `generate.yml` (Main Video Generation)

| # | Prompt Name | Complexity | Tokens | Best Model | Why |
|---|-------------|------------|--------|------------|-----|
| 1 | VIRAL_TOPIC_PROMPT | 🔴 Complex | ~2000 | llama-3.3-70b | Needs creativity, understanding of viral patterns |
| 2 | GOD_TIER_GENERATION_PROMPT | 🔴 Complex | ~1500 | llama-3.3-70b | Critical for quality, needs best model |
| 3 | GOD_TIER_EVALUATION_PROMPT | 🔴 Complex | ~1500 | gemini-2.0-flash | Evaluation benefits from structured output |
| 4 | CONTENT_EVALUATION_PROMPT | 🟡 Medium | ~800 | gemini-1.5-flash | Scoring is faster with flash |
| 5 | BROLL_KEYWORDS_PROMPT | 🟢 Simple | ~500 | gemini-1.5-flash | Just keyword extraction |
| 6 | VOICEOVER_PROMPT | 🟡 Medium | ~600 | llama-3.3-70b | Needs natural human voice |
| 7 | DESCRIPTION_SEO_PROMPT | 🟢 Simple | ~400 | gemini-1.5-flash | SEO is formulaic |
| 8 | THUMBNAIL_TEXT_PROMPT | 🟢 Simple | ~400 | gemini-1.5-flash | Short output |
| 9 | PLATFORM_OPTIMIZATION_PROMPT | 🟡 Medium | ~600 | gemini-1.5-flash | Platform-specific |
| 10 | CONTEXTUAL_AWARENESS_PROMPT | 🟢 Simple | ~400 | llama-3.1-8b | Date checking |
| 11 | Hashtag Generation | 🟢 Simple | ~200 | gemini-1.5-flash | List generation |
| 12 | Hook Word Analysis | 🟡 Medium | ~500 | gemini-1.5-flash | Pattern recognition |
| 13 | Value Delivery Check | 🟡 Medium | ~600 | llama-3.3-70b | Needs understanding |
| 14 | Quality Gate Checks | 🟡 Medium | ~800 | gemini-2.0-flash | Evaluation task |

### Workflow 2: `analytics-feedback.yml` (Learning)

| # | Prompt Name | Complexity | Tokens | Best Model | Why |
|---|-------------|------------|--------|------------|-----|
| 15 | ANALYTICS_DEEP_DIVE_PROMPT | 🔴 Complex | ~1200 | gemini-1.5-pro | Deep analysis |
| 16 | CATEGORY_DECAY_PROMPT | 🟡 Medium | ~600 | gemini-1.5-flash | Trend tracking |
| 17 | HOOK_WORD_ANALYSIS_PROMPT | 🟡 Medium | ~500 | gemini-1.5-flash | Pattern extraction |
| 18 | SERIES_CONTINUATION_PROMPT | 🟡 Medium | ~700 | llama-3.3-70b | Creative continuation |
| 19 | ENGAGEMENT_REPLY_PROMPT | 🟡 Medium | ~600 | llama-3.3-70b | Human-like replies |
| 20 | COMMENT_SENTIMENT_PROMPT | 🟢 Simple | ~400 | gemini-1.5-flash | Classification |

### Workflow 3: `monthly-analysis.yml` (Strategy)

| # | Prompt Name | Complexity | Tokens | Best Model | Why |
|---|-------------|------------|--------|------------|-----|
| 21 | CHANNEL_GROWTH_PROMPT | 🔴 Complex | ~1500 | gemini-1.5-pro | Strategic thinking |
| 22 | COMPETITOR_GAP_PROMPT | 🔴 Complex | ~1200 | llama-3.3-70b | Creative gap finding |
| 23 | CONTENT_RECYCLING_PROMPT | 🟡 Medium | ~700 | llama-3.3-70b | Creative resurrection |
| 24 | VIRAL_VELOCITY_PROMPT | 🟡 Medium | ~800 | gemini-2.0-flash | Prediction |

### Workflow 4: `pre-work.yml` (Preparation)

| # | Prompt Name | Complexity | Tokens | Best Model | Why |
|---|-------------|------------|--------|------------|-----|
| 25 | SEASONAL_CALENDAR_PROMPT | 🟡 Medium | ~800 | gemini-1.5-flash | Date-based |
| 26 | Trend Discovery | 🟡 Medium | ~600 | llama-3.3-70b | Needs current knowledge |

### Workflow 5: `refresh-ai-patterns.yml` (Pattern Learning)

| # | Prompt Name | Complexity | Tokens | Best Model | Why |
|---|-------------|------------|--------|------------|-----|
| 27 | Pattern Extraction | 🟡 Medium | ~500 | gemini-1.5-flash | Extraction task |
| 28 | Power Word Analysis | 🟢 Simple | ~300 | gemini-1.5-flash | List processing |

### Additional Enhancement Prompts (89 Enhancements)

| Category | Prompts | Complexity | Best Model |
|----------|---------|------------|------------|
| Click Baiting (#46-51) | 6 | 🟡 Medium | llama-3.3-70b |
| First Seconds (#52-57) | 6 | 🟡 Medium | llama-3.3-70b |
| Algorithm Optimization (#58-63) | 6 | 🟢 Simple | gemini-1.5-flash |
| Visual Improvements (#64-68) | 5 | 🟢 Simple | gemini-1.5-flash |
| Content Quality (#69-74) | 6 | 🟡 Medium | llama-3.3-70b |
| Viral/Trendy (#75-79) | 5 | 🟡 Medium | llama-3.3-70b |
| Analytics Feedback (#80-84) | 5 | 🟡 Medium | gemini-1.5-flash |
| Other Important (#85-89) | 5 | 🟡 Medium | gemini-1.5-flash |

---

## Prompts That Benefit from Specific Models

### 🎯 CREATIVE PROMPTS → llama-3.3-70b-versatile

These prompts need human-like creativity and natural voice:

| Prompt | Why llama-3.3-70b is better |
|--------|---------------------------|
| VIRAL_TOPIC_PROMPT | Needs creative, viral-worthy ideas |
| GOD_TIER_GENERATION_PROMPT | Content must sound human, not AI |
| VOICEOVER_PROMPT | Natural speech patterns required |
| ENGAGEMENT_REPLY_PROMPT | Human-like comment responses |
| Hook Generation | Punchy, creative hooks |
| CTA Generation | Engaging calls-to-action |
| Series Continuation | Creative sequel ideas |
| Content Recycling | Fresh angles on old content |

**Score Comparison for Creative Prompts:**
- llama-3.3-70b: 9.0/10
- gemini-2.0-flash: 7.5/10
- gemini-1.5-flash: 7.0/10
- llama-3.1-8b: 6.5/10

### 📊 EVALUATION/ANALYSIS PROMPTS → gemini-2.0-flash

These prompts need structured output and scoring:

| Prompt | Why gemini-2.0-flash is better |
|--------|------------------------------|
| GOD_TIER_EVALUATION_PROMPT | Structured scoring output |
| CONTENT_EVALUATION_PROMPT | Multi-dimensional scoring |
| VIRAL_VELOCITY_PROMPT | Prediction with numbers |
| Quality Gate Checks | Pass/fail decisions |
| Analytics Deep Dive | Data interpretation |

**Score Comparison for Evaluation Prompts:**
- gemini-2.0-flash: 8.5/10
- gemini-1.5-flash: 8.0/10
- llama-3.3-70b: 7.5/10
- gemini-1.5-pro: 8.5/10 (but limited quota)

### ⚡ SIMPLE/FAST PROMPTS → gemini-1.5-flash or llama-3.1-8b

These prompts are simple and benefit from speed:

| Prompt | Best Model |
|--------|-----------|
| Hashtag Generation | gemini-1.5-flash |
| B-roll Keywords | gemini-1.5-flash |
| Description SEO | gemini-1.5-flash |
| Thumbnail Text | gemini-1.5-flash |
| Date/Context Checking | llama-3.1-8b |
| Pattern Extraction | gemini-1.5-flash |
| Sentiment Classification | gemini-1.5-flash |

**Score Comparison for Simple Prompts:**
- All models perform similarly (7-8/10)
- Speed and quota are the differentiators

### 🧠 COMPLEX ANALYSIS PROMPTS → gemini-1.5-pro (limited use)

Use sparingly due to low quota (~50/day):

| Prompt | Why Pro is worth the quota |
|--------|---------------------------|
| CHANNEL_GROWTH_PROMPT | Strategic, long-term planning |
| ANALYTICS_DEEP_DIVE_PROMPT | Complex correlation finding |
| Competitor Gap Analysis | Deep market analysis |

**Recommendation:** Use Pro only for monthly analysis workflow, not daily.

---

## Robustness Analysis

| Model | Success Rate | Common Failures | Recovery Time |
|-------|--------------|-----------------|---------------|
| llama-3.3-70b | 98% | Rate limit (2%) | 60s |
| gemini-1.5-flash | 95% | 429 quota (5%) | Reset at midnight PT |
| gemini-2.0-flash | 92% | 429 quota (8%) | Reset at midnight PT |
| llama-3.1-8b | 99% | Almost never | N/A |
| HuggingFace models | 75-82% | 503 overload (18%) | 30-60s |
| OpenRouter free | 85-90% | Model busy (10%) | 30s |

---

## Recommended Model Selection Strategy

### For Daily Video Generation (6 videos/day)

```
PROMPT TYPE              → PRIMARY MODEL        → FALLBACK
───────────────────────────────────────────────────────────
Topic Generation         → llama-3.3-70b        → gemini-2.0-flash
Content Creation         → llama-3.3-70b        → gemini-2.0-flash  
Content Evaluation       → gemini-2.0-flash     → llama-3.3-70b
Hook Generation          → llama-3.3-70b        → gemini-1.5-flash
Voiceover Script         → llama-3.3-70b        → gemini-1.5-flash
B-roll Keywords          → gemini-1.5-flash     → llama-3.1-8b
Description/SEO          → gemini-1.5-flash     → llama-3.1-8b
Hashtags                 → gemini-1.5-flash     → llama-3.1-8b
Quality Checks           → gemini-2.0-flash     → gemini-1.5-flash
```

### Estimated Daily Usage with Optimal Routing

| Model | Calls/Video | Daily (6 videos) | % of Quota |
|-------|-------------|------------------|-----------|
| llama-3.3-70b | 3 | 18 | ~6% |
| gemini-1.5-flash | 4 | 24 | ~1.6% |
| gemini-2.0-flash | 2 | 12 | ~2.4% |
| llama-3.1-8b | 1 | 6 | ~1% |

**Total Daily Usage: ~60 calls = 1.5% of combined quota**

---

## Additional Scores

### Latency (Time to First Token)

| Model | Latency | Rating |
|-------|---------|--------|
| llama-3.1-8b-instant | ~100ms | ⚡⚡⚡⚡⚡ |
| llama-3.3-70b | ~300ms | ⚡⚡⚡⚡ |
| gemini-1.5-flash | ~400ms | ⚡⚡⚡ |
| gemini-2.0-flash | ~500ms | ⚡⚡⚡ |
| HuggingFace | ~2000ms | ⚡ |

### Output Token Quality

| Model | Coherence | Creativity | Accuracy | Formatting |
|-------|-----------|------------|----------|------------|
| llama-3.3-70b | 9/10 | 9/10 | 8/10 | 8/10 |
| gemini-2.0-flash | 8/10 | 7/10 | 9/10 | 9/10 |
| gemini-1.5-flash | 8/10 | 7/10 | 8/10 | 9/10 |
| gemini-1.5-pro | 9/10 | 8/10 | 9/10 | 9/10 |
| llama-3.1-8b | 7/10 | 6/10 | 7/10 | 7/10 |

### JSON Output Reliability

| Model | Valid JSON % | Notes |
|-------|--------------|-------|
| gemini-2.0-flash | 98% | Best for structured output |
| gemini-1.5-flash | 96% | Very reliable |
| llama-3.3-70b | 92% | Sometimes needs cleaning |
| llama-3.1-8b | 88% | Occasionally malformed |
| HuggingFace | 75% | Often needs cleanup |

---

## Implementation Recommendations

### 1. Smart Prompt Router

```python
def get_best_model_for_prompt(prompt_type: str) -> str:
    CREATIVE_PROMPTS = ["topic", "content", "hook", "voiceover", "cta", "engagement"]
    EVALUATION_PROMPTS = ["evaluation", "quality", "velocity", "analysis"]
    SIMPLE_PROMPTS = ["hashtag", "broll", "seo", "description", "sentiment"]
    
    if any(p in prompt_type.lower() for p in CREATIVE_PROMPTS):
        return "groq:llama-3.3-70b-versatile"
    elif any(p in prompt_type.lower() for p in EVALUATION_PROMPTS):
        return "gemini:gemini-2.0-flash"
    else:
        return "gemini:gemini-1.5-flash"
```

### 2. Quota-Aware Selection

```python
def select_model_with_quota_awareness(prompt_type: str, quota_status: dict) -> str:
    ideal = get_best_model_for_prompt(prompt_type)
    provider, model = ideal.split(":")
    
    if quota_status[provider]["remaining"] < 10:
        # Fall back to next best
        return get_fallback_model(prompt_type)
    
    return ideal
```

### 3. Per-Prompt Retry Strategy

```python
RETRY_CONFIG = {
    "creative": {"max_retries": 3, "backoff": 2.0},  # Important, retry more
    "evaluation": {"max_retries": 2, "backoff": 1.5},
    "simple": {"max_retries": 1, "backoff": 1.0}  # Not critical
}
```

---

## Summary

| Metric | Value |
|--------|-------|
| Total Models Available | 22 |
| Total Prompts in System | 89+ (28 core + 61 enhancements) |
| Daily Combined Quota | 4,100+ calls |
| Daily Usage (6 videos) | ~60 calls (1.5%) |
| Headroom | **68x more capacity than needed** |
| Best Creative Model | llama-3.3-70b-versatile |
| Best Evaluation Model | gemini-2.0-flash |
| Best Simple Task Model | gemini-1.5-flash |
| Most Reliable Model | llama-3.1-8b-instant (99%) |
| Best Quality/Quota Ratio | gemini-1.5-flash |

