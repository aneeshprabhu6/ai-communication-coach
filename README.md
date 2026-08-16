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

## 🛠️ Developer Setup & Generating the Standalone `.exe`

If you want to run the project from source or compile it into a standalone executable (`main.exe`) so it can run on machines without Python installed, follow these steps:

### 1. Clone or Download the Repository
Navigate to your project directory containing the `backend/` and `frontend/` folders.

### 2. Install Dependencies
Open your terminal inside the `backend/` folder and install the required Python packages:
```bash
pip install -r requirements.txt

---

Open main.py in notepad and enter your GEMINI API KEY where it says "HERE........................." 

---

Generate the Standalone .exe (PyInstaller)
To bundle the FastAPI backend, Uvicorn, Whisper models, and all dependencies into a single portable executable file, run PyInstaller:

Bash
pip install pyinstaller
pyinstaller --onefile main.py

Once the build completes, PyInstaller will create a dist/ folder inside your backend/ directory.

Inside dist/, you will find your compiled main.exe

---

Running the Application
Move your newly generated main.exe and your index.html file into the same folder.

Double-click main.exe to start the local backend server (keep the terminal window open).

Double-click index.html to open the user interface in your web browser

---

## 🛠️ Developer Setup (Running from Source)

If you want to run or modify the source code locally:

### 1. Clone the Repository
```bash
git clone [https://github.com/aneeshprabhu6/ai-communication-coach.git](https://github.com/aneeshprabhu6/ai-communication-coach.git)
cd ai-communication-coach/backend
