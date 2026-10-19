# 🎬 ViralShorts Factory

**100% Autonomous AI-Powered YouTube Shorts Generator**

Generate viral, high-quality YouTube Shorts automatically using a **100% free tech stack**. 6 videos daily, zero cost.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Cost](https://img.shields.io/badge/Cost-$0-brightgreen?style=flat-square)
![Videos](https://img.shields.io/badge/Daily%20Videos-6-orange?style=flat-square)

## 🚀 Features

- **100% Autonomous**: GitHub Actions generates & uploads videos daily
- **Zero-Cost**: Free-tier AI (Groq, Gemini, OpenRouter) + Free assets
- **AI-Powered Quality**: 419 enhancements for viral-ready content
- **Self-Learning**: Learns from analytics to improve over time
- **Multi-Platform**: YouTube, Dailymotion, Rumble support
- **Smart Quotas**: Intelligent rate-limit management across providers

## 📁 Project Structure

```
ViralShorts-Factory/
├── src/                          # Main source code
│   ├── core/                     # Video generation core
│   │   ├── pro_video_generator.py  # Main generator (v16.11)
│   │   ├── dynamic_video_generator.py
│   │   ├── video_enhancements.py
│   │   └── script.py, script_v2.py
│   │
│   ├── ai/                       # AI modules
│   │   ├── multi_ai.py           # Multi-provider AI caller
│   │   ├── god_tier_prompts.py   # Optimized prompts
│   │   ├── ai_evaluator.py       # Content quality AI
│   │   ├── ai_generator.py       # Content generation
│   │   └── trending_*.py         # Trend detection
│   │
│   ├── enhancements/             # Quality enhancement systems
│   │   ├── enhancements_v9.py    # 89 enhancements
│   │   ├── enhancements_v12.py   # 330 enhancements
│   │   └── critical_fixes.py     # Font/SFX/Quality fixes
│   │
│   ├── analytics/                # Analytics & learning
│   │   ├── analytics_feedback.py # Performance tracking
│   │   ├── self_learning_engine.py
│   │   └── viral_*.py            # Viral analysis
│   │
│   ├── quota/                    # API quota management
│   │   ├── quota_optimizer.py    # Dynamic model selection
│   │   ├── quota_monitor.py      # Usage tracking
│   │   └── token_budget_manager.py
│   │
│   ├── platforms/                # Platform uploaders
│   │   ├── youtube_uploader.py
│   │   ├── dailymotion_uploader.py
│   │   └── rumble_uploader.py
│   │
│   └── utils/                    # Utilities
│       ├── fetch_broll.py        # B-roll fetching
│       ├── background_music.py   # Music selection
│       └── sound_effects.py
│
├── tests/                        # Test suite
├── scripts/                      # Helper scripts
├── .github/workflows/            # GitHub Actions
├── assets/                       # Static assets
├── data/                         # Persistent data
├── config/                       # Configuration
└── output/                       # Generated videos
```

## 🛠️ Installation

### Prerequisites

1. **Python 3.10+**
2. **FFmpeg**: `winget install ffmpeg` (Windows) / `brew install ffmpeg` (Mac)
3. **ImageMagick**: Download from [imagemagick.org](https://imagemagick.org)

### Setup

```bash
# Clone the repository
git clone <URL-REPOSITORY-ANDA>
cd <NAMA-FOLDER-REPOSITORY>

# Install dependencies
pip install -r requirements.txt

# Set up API keys (all free tier)
export GROQ_API_KEY="your-groq-key"
export GEMINI_API_KEY="your-gemini-key"
export OPENROUTER_API_KEY="your-openrouter-key"
```

## 🎯 Usage

### Generate Videos Locally

```bash
# Generate 1 video (no upload)
python pro_video_generator.py --count 1 --no-upload

# Generate and upload to Dailymotion
python pro_video_generator.py --count 3 --upload
```

### Automated Generation (GitHub Actions)

The project includes automated workflows:

- **generate.yml**: Runs 6x daily, generates & uploads videos
- **analytics-feedback.yml**: Weekly analytics analysis
- **pre-work.yml**: Pre-fetches trending topics
- **monthly-analysis.yml**: Monthly performance review

## 🔑 Required Secrets

Set these in GitHub Repository Settings → Secrets:

| Secret | Description | Where to Get |
|--------|-------------|--------------|
| `GROQ_API_KEY` | Groq AI API | [console.groq.com](https://console.groq.com) |
| `GEMINI_API_KEY` | Google Gemini | [aistudio.google.com](https://aistudio.google.com) |
| `OPENROUTER_API_KEY` | OpenRouter | [openrouter.ai](https://openrouter.ai) |
| `YOUTUBE_*` | YouTube API | Google Cloud Console |
| `DAILYMOTION_*` | Dailymotion API | Dailymotion Developer |
| `PEXELS_API_KEY` | B-roll videos | [pexels.com/api](https://www.pexels.com/api/) |

## 📊 Enhancement Systems

- **v9 Enhancements**: 89 quality checks (hooks, SEO, engagement)
- **v12 Enhancements**: 330 advanced optimizations
- **Critical Fixes**: Font rendering, SFX, promise enforcement
- **Self-Learning**: Adapts prompts based on video performance

## 📈 Performance

- **Quality Score Target**: 10/10 (AI-evaluated)
- **First-Attempt Success**: >80%
- **Daily Output**: 6 videos
- **Cost**: $0 (all free-tier APIs)

## 📜 License

MIT License - See [LICENSE](LICENSE)

---

**Made with ❤️ for content creators who want to automate viral shorts.**
