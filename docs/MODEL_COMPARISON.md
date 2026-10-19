# ViralShorts Factory - Model Comparison Chart

> Generated: January 2026 | Version: v17.9.8

## Complete Model Inventory

### GEMINI (Google)

| Model | Daily Limit | Quality | Speed | Priority | Notes |
|-------|-------------|---------|-------|----------|-------|
| gemini-1.5-flash | 1,500/day | 7.5/10 | Fast | **1st** | PRIMARY - Highest quota |
| gemini-1.5-flash-latest | 1,500/day | 7.5/10 | Fast | 2nd | Same as 1.5-flash |
| gemini-1.5-flash-8b | 1,500/day | 7/10 | Very Fast | 3rd | Smaller variant |
| gemini-2.0-flash | 500/day | 8/10 | Fast | 4th | Stable, good quality |
| gemini-1.5-pro | ~50/day | 8.5/10 | Slower | 5th | Complex tasks only |
| gemini-2.0-flash-exp | 50-100/day | 8/10 | Fast | 6th | EXPERIMENTAL - Low quota |
| gemini-pro | 60/day | 7/10 | Slow | Last | Legacy fallback |

### GROQ

| Model | Rate Limit | Quality | Speed | Priority | Notes |
|-------|------------|---------|-------|----------|-------|
| llama-3.3-70b-versatile | 14.4K tok/min | 8.5/10 | Ultra Fast | **1st** | PRIMARY - Best quality |
| llama-3.1-70b-versatile | 14.4K tok/min | 8/10 | Ultra Fast | 2nd | Backup for 3.3 |
| llama-3.1-8b-instant | 14.4K tok/min | 7/10 | Fastest | 3rd | Small but super fast |
| mixtral-8x7b-32768 | 14.4K tok/min | 7.5/10 | Fast | 4th | Alternative architecture |
| gemma2-9b-it | 14.4K tok/min | 7/10 | Fast | 5th | Google model on Groq |

> **Note**: Groq uses shared token pool (14,400 tokens/minute), no daily limit!

### OPENROUTER (Free Tier)

| Model | Limit | Quality | Speed | Notes |
|-------|-------|---------|-------|-------|
| meta-llama/llama-3.2-3b-instruct:free | Unlimited | 6.5/10 | Fast | Small but free |
| google/gemma-2-9b-it:free | Unlimited | 7/10 | Fast | Google model |
| mistralai/mistral-7b-instruct:free | Unlimited | 7/10 | Fast | General tasks |
| huggingfaceh4/zephyr-7b-beta:free | Unlimited | 7/10 | Fast | Chat-tuned |
| openchat/openchat-7b:free | Unlimited | 6.5/10 | Fast | Community model |

### HUGGINGFACE

| Model | Rate Limit | Quality | Speed | Notes |
|-------|------------|---------|-------|-------|
| HuggingFaceH4/zephyr-7b-beta | ~100 req/h | 7.5/10 | Medium | NON-GATED, reliable |
| google/gemma-2-2b-it | ~100 req/h | 6.5/10 | Fast | Small Google model |
| Qwen/Qwen2.5-1.5B-Instruct | ~100 req/h | 6/10 | Very Fast | Tiny but capable |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | ~100 req/h | 5.5/10 | Fastest | Ultra lightweight |
| microsoft/Phi-3-mini-4k-instruct | ~100 req/h | 7/10 | Medium | Microsoft quality |

---

## Fallback Chain

```
PRIORITY 1: GROQ (Primary)
    └─> llama-3.3-70b-versatile
    └─> llama-3.1-70b-versatile
    └─> llama-3.1-8b-instant
    └─> mixtral-8x7b-32768
         │
         ▼ (if all fail)
PRIORITY 2: GEMINI (Secondary)
    └─> gemini-1.5-flash (1,500/day)
    └─> gemini-2.0-flash (500/day)
    └─> gemini-1.5-pro (50/day)
         │
         ▼ (if all fail)
PRIORITY 3: HUGGINGFACE (Tertiary)
    └─> HuggingFaceH4/zephyr-7b-beta
    └─> google/gemma-2-2b-it
    └─> Qwen/Qwen2.5-1.5B-Instruct
         │
         ▼ (if all fail)
PRIORITY 4: OPENROUTER (Last Resort)
    └─> meta-llama/llama-3.2-3b-instruct:free
    └─> google/gemma-2-9b-it:free
    └─> mistralai/mistral-7b-instruct:free
```

---

## Quota Summary

| Provider | Available Quota | Our Daily Need | Headroom |
|----------|-----------------|----------------|----------|
| Groq | ~200-300 calls/day | 48-100 | **3x** |
| Gemini (1.5-flash) | 1,500 calls/day | 48-100 | **30x** |
| HuggingFace | ~2,400 calls/day | 48-100 | **24x** |
| OpenRouter | Unlimited | 48-100 | **∞** |
| **TOTAL** | **4,100+/day** | **100** | **40x** |

---

## Quality Tiers

### Tier 1 (8+ Quality) - Critical Content
- llama-3.3-70b-versatile (Groq) - 8.5/10
- gemini-1.5-pro (Gemini) - 8.5/10
- gemini-2.0-flash (Gemini) - 8/10
- llama-3.1-70b-versatile (Groq) - 8/10

### Tier 2 (7-7.9 Quality) - Standard Tasks
- gemini-1.5-flash (Gemini) - 7.5/10
- mixtral-8x7b-32768 (Groq) - 7.5/10
- HuggingFaceH4/zephyr-7b-beta - 7.5/10
- microsoft/Phi-3-mini-4k-instruct - 7/10

### Tier 3 (6-6.9 Quality) - Fallback Only
- google/gemma-2-2b-it - 6.5/10
- meta-llama/llama-3.2-3b-instruct:free - 6.5/10
- Qwen/Qwen2.5-1.5B-Instruct - 6/10

---

## Best Model by Task

| Task | Recommended Model | Reason |
|------|------------------|--------|
| Viral Script Writing | llama-3.3-70b (Groq) | Creative, human-like output |
| Hook Generation | gemini-2.0-flash | Good at punchy, short phrases |
| Content Evaluation | gemini-1.5-flash | Fast, accurate scoring |
| Hashtag Generation | llama-3.1-8b (Groq) | Fast for simple tasks |
| Description Writing | gemini-1.5-flash | Structured output |
| Complex Analysis | gemini-1.5-pro | Deeper reasoning capability |
| Bulk Processing | zephyr-7b (HuggingFace) | Free, reliable |
| Emergency Fallback | llama-3.2-3b (OpenRouter) | Always available |

---

## Key Insights

1. **Groq is PRIMARY** - No daily limit, only per-minute token limit
2. **Gemini 1.5-flash has 30x more quota than we need** - Safe for heavy use
3. **4 providers = 13+ model fallbacks** - Extremely resilient
4. **Quality vs Quota tradeoff**: Higher quota models (1.5-flash) have slightly lower quality than pro models
5. **Experimental models have LOW quota** - Avoid as primary

