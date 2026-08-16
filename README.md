# 🎙️ AI Executive Communication Coach

An offline-first, privacy-focused AI communication coach designed to help professionals master executive presence, clarity, brevity, and structured communication ("Lead with the point → support it → stop").

Powered locally by **faster-whisper** (CPU-optimized speech-to-text) and driven by **Gemini 3.5 Flash** for deep behavioral feedback, metrics scoring, and adaptive coaching.

---

## ✨ Key Features

- **Dual Practice Modes:**
  - **Non-Assisted (Free Practice) Mode:** Improvise your response to realistic executive scenarios from scratch.
  - **Assisted Mode:** Generates a teleprompter-style model executive script on the fly so you can practice reading it aloud.
- **Advanced Local Audio Processing:** Runs speech recognition locally via `faster-whisper` (`int8` CPU quantization), ensuring fast processing without needing an expensive GPU or sending raw audio logs to the cloud.
- **Deep Metrics & Scoring Engine:**
  - **BLUF (Bottom Line Up Front)** adherence scoring.
  - **WPM (Words Per Minute)** & Filler word percentage tracking.
  - **Executive Tone & Verbal Articulation** evaluations.
- **30-Day Structured Curriculum:** Progressive daily drills tracking your performance history to adaptively target your recurring bad habits.

---

## 🚀 Quickstart for End Users (No Python Required)

If you are running the pre-packaged executable release:
1. Download the latest `main.exe` from the **Releases** tab.
2. Download the `index.html` frontend file and place it in the same folder as `main.exe`.
3. Double-click **`main.exe`** to start the local backend server (leave the terminal window open).
4. Double-click **`index.html`** to open the user interface in your web browser.

---

## 🛠️ Developer Setup (Running from Source)

If you want to run or modify the source code locally:

### 1. Clone the Repository
```bash
git clone [https://github.com/aneeshprabhu6/ai-communication-coach.git](https://github.com/aneeshprabhu6/ai-communication-coach.git)
cd ai-communication-coach/backend