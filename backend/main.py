import sys
import os
import re
import json
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from google import genai
from google.genai import types

# Initialize the API
app = FastAPI(title="AI Communication Coach API - Gemini Edition")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Silence HuggingFace Symlink Warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# --- Initialize Local Whisper Model for CPU / Low-RAM Laptops ---
print("Loading Whisper model (small.en) on CPU (int8)...")
whisper_model = WhisperModel("small.en", device="cpu", compute_type="int8")

# --- Hardcoded Google GenAI Client ---
GEMINI_API_KEY = "HERE........................." 

client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-3.5-flash"

# --- 30-Day Curriculum Program Library ---
CURRICULUM_PROGRAM = {
    1: {"week": 1, "theme": "Clarity", "title": "Introduce your role", "prompt": "Introduce your current professional role and core responsibility in 60 seconds."},
    2: {"week": 1, "theme": "Clarity", "title": "Explain current project", "prompt": "Explain the primary project you are leading right now and its main goal."},
    3: {"week": 1, "theme": "Clarity", "title": "Technical to non-technical", "prompt": "Explain a complex technical challenge you faced recently to a non-technical executive."},
    4: {"week": 1, "theme": "Clarity", "title": "Explain a core problem", "prompt": "State a major operational bottleneck your team is facing without using jargon."},
    5: {"week": 1, "theme": "Clarity", "title": "Explain a recommendation", "prompt": "Give a clear recommendation for a tool or process change you want leadership to approve."},
    6: {"week": 1, "theme": "Clarity", "title": "Summarize a meeting", "prompt": "Summarize the most important cross-functional meeting you attended this week in 45 seconds."},
    7: {"week": 1, "theme": "Clarity", "title": "Weekly Clarity Assessment", "prompt": "Defend a past project decision using clear, unambiguous language."},
    8: {"week": 2, "theme": "Brevity", "title": "Project delay compression (90s)", "prompt": "Explain why your project is delayed. Target: 90 seconds."},
    9: {"week": 2, "theme": "Brevity", "title": "Project delay compression (60s)", "prompt": "Explain why your project is delayed. Compress it down to 60 seconds."},
    10: {"week": 2, "theme": "Brevity", "title": "Project delay compression (30s)", "prompt": "Explain why your project is delayed. Compress it down to a strict 30 seconds."},
    11: {"week": 2, "theme": "Brevity", "title": "Budget cut justification", "prompt": "Justify keeping your team's budget intact in under 45 seconds."},
    12: {"week": 2, "theme": "Brevity", "title": "Vendor failure summary", "prompt": "Summarize why a critical third-party vendor failed in 30 seconds."},
    13: {"week": 2, "theme": "Brevity", "title": "Product pivot pitch", "prompt": "Pitch a critical product roadmap pivot in 45 seconds."},
    14: {"week": 2, "theme": "Brevity", "title": "Weekly Brevity Assessment", "prompt": "Deliver an executive update summarizing three separate workstreams in 60 seconds."},
    15: {"week": 3, "theme": "Executive Sim", "title": "Customer escalation", "prompt": "Customer: 'You missed our launch window completely. Why should I trust your recovery timeline now?' Respond as the lead director."},
    16: {"week": 3, "theme": "Executive Sim", "title": "Executive challenge", "prompt": "VP: 'This strategy looks too risky. Why shouldn't we scrap it?' Defend your position."},
    17: {"week": 3, "theme": "Executive Sim", "title": "Resource pushback", "prompt": "CFO: 'We cannot give you 3 more engineers. Make it work with existing headcount.' Respond."},
    18: {"week": 3, "theme": "Executive Sim", "title": "Defending a decision", "prompt": "Board Member: 'Why did you select vendor A over vendor B when vendor B was cheaper?' Explain."},
    19: {"week": 3, "theme": "Executive Sim", "title": "Explaining a system failure", "prompt": "CEO: 'Bring me up to speed on why the production database went down for 2 hours.' Brief them."},
    20: {"week": 3, "theme": "Executive Sim", "title": "Disagreeing with a senior exec", "prompt": "Senior VP proposes a timeline that will cause burnout. Politely push back and offer an alternative."},
    21: {"week": 3, "theme": "Executive Sim", "title": "Weekly Simulation Assessment", "prompt": "Handle a high-pressure stakeholder meeting where three separate objections are thrown at you at once."},
    22: {"week": 4, "theme": "Real-World", "title": "Morning prep loop", "prompt": "State the single most critical conversation you have today and your core objective."},
    23: {"week": 4, "theme": "Real-World", "title": "Post-meeting reflection", "prompt": "Summarize a difficult conversation you had yesterday and state what you would say differently."},
    24: {"week": 4, "theme": "Real-World", "title": "Adaptive Remediation 1", "prompt": "Custom drill based on your weakest historical metric."},
    25: {"week": 4, "theme": "Real-World", "title": "Adaptive Remediation 2", "prompt": "Custom drill targeting your most frequent bad habit."},
    26: {"week": 4, "theme": "Real-World", "title": "High-stakes crisis brief", "prompt": "Brief the executive committee on an active security vulnerability under a 45-second constraint."},
    27: {"week": 4, "theme": "Real-World", "title": "Cross-functional alignment", "prompt": "Convince a resistant peer team to adopt your workflow framework."},
    28: {"week": 4, "theme": "Real-World", "title": "Managing upward", "prompt": "Provide bad news regarding a missed quarterly target directly to your CEO."},
    29: {"week": 4, "theme": "Real-World", "title": "Executive presence drill", "prompt": "Deliver an impromptu company-wide update focusing entirely on tone, pace, and absolute clarity."},
    30: {"week": 4, "theme": "Real-World", "title": "Final 30-Day Master Assessment", "prompt": "Synthesize a complex enterprise crisis, recovery roadmap, and financial ROI into a flawless 60-second executive brief."}
}

# --- Deterministic Metric Functions ---
def calculate_wpm(transcript: str, duration_seconds: float) -> int:
    if duration_seconds <= 0: return 0
    words = re.findall(r'\b\w+\b', transcript)
    return int((len(words) / duration_seconds) * 60)

def calculate_filler_rate(transcript: str) -> float:
    fillers = [
        r'\bum+\b', r'\buh+\b', r'\bbasically\b', r'\bactually\b', 
        r'\byou know\b', r'\bsort of\b', r'\bkind of\b', r'\bI mean\b'
    ]
    words = re.findall(r'\b\w+\b', transcript.lower())
    if not words: return 0.0
    
    filler_count = 0
    transcript_lower = transcript.lower()
    for f in fillers:
        matches = re.findall(f, transcript_lower)
        filler_count += (len(matches) * len(f.split()))
        
    return round((filler_count / len(words)) * 100, 2)

def calculate_overall_score(clarity: int, brevity: int, structure: int, bluf: int, tone: int, articulation: int, filler_rate: float) -> int:
    clarity_points = (clarity / 20) * 20
    brevity_points = (brevity / 20) * 20
    structure_points = (structure / 15) * 15
    bluf_points = (bluf / 5) * 15
    tone_points = (tone / 10) * 10
    articulation_points = (articulation / 10) * 10
    
    raw_score = clarity_points + brevity_points + structure_points + bluf_points + tone_points + articulation_points
    penalty = min(10, (filler_rate / 10) * 10)
    
    return max(0, min(100, int((raw_score / 90) * 90 - penalty + 10)))

# --- API ENDPOINTS ---

@app.post("/api/scenarios/generate")
def generate_scenario():
    try:
        prompt = """You are an expert executive communication coach. Generate a unique, realistic business communication scenario.
        The scenario should require the user to handle a customer escalation, executive briefing, project status crisis, or difficult stakeholder conversation.
        
        Output format: You must return a valid JSON object matching this exact schema:
        {
          "scenario_text": "[A clear paragraph describing the role, audience, situation, and question/task, requiring a 60-second response]"
        }"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        result = json.loads(response.text)
        return {"status": "success", "scenario_text": result.get("scenario_text", "Explain your project status to the CEO in 60 seconds.")}
    except Exception as e:
        return {"status": "success", "scenario_text": "Our primary product launch is delayed by two weeks due to a database migration bottleneck. Brief the CEO on the recovery timeline and impact in 60 seconds."}

@app.post("/api/scenarios/assisted-script")
def generate_assisted_script(scenario_text: str = Form(...)):
    try:
        prompt = f"""You are an elite executive communication coach. For the following scenario, write a model 60-second executive response script that follows the BLUF (Bottom Line Up Front) principle, is concise, and maintains an authoritative, empathetic, and professional tone.
        
        Scenario: "{scenario_text}"
        
        Output format: You must return a valid JSON object matching this exact schema:
        {{
          "assisted_script": "[The complete model response text that the user can read aloud]"
        }}"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        result = json.loads(response.text)
        return {"status": "success", "assisted_script": result.get("assisted_script", "Thank you for connecting. Here is our direct plan...")}
    except Exception as e:
        return {"status": "success", "assisted_script": f"To address this situation directly: Our core objective is resolving the core challenge immediately. We have structured a 3-step action plan with zero risk to our timeline. Let me break down the direct impact and next steps."}

@app.get("/api/curriculum/day/{day_number}")
def get_curriculum_day(day_number: int, performance_summary: Optional[str] = ""):
    day_data = CURRICULUM_PROGRAM.get(day_number, CURRICULUM_PROGRAM[1]).copy()
    
    if day_number >= 24 and performance_summary:
        prompt = f"""You are an adaptive executive communication coach. 
        Based on the user's performance history: '{performance_summary}', 
        dynamically tailor this day's practice prompt to specifically target their weakest link.
        Standard prompt was: {day_data['prompt']}
        Return a valid JSON object matching: {{"title": "...", "prompt": "..."}}"""
        
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            adapted = json.loads(response.text)
            day_data["title"] = adapted.get("title", day_data["title"])
            day_data["prompt"] = adapted.get("prompt", day_data["prompt"])
        except Exception:
            pass

    return {"status": "success", "curriculum": day_data}

@app.post("/api/attempts/evaluate")
async def evaluate_attempt(
    audio_file: UploadFile = File(...), 
    scenario_text: str = Form(...),
    history_context: Optional[str] = Form(default="")
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(await audio_file.read())
        temp_path = temp_audio.name

    try:
        segments, info = whisper_model.transcribe(
            temp_path, 
            beam_size=5,
            temperature=0.0,
            initial_prompt="Umm, let me think... uhhh, okay, basically, you know, sort of..."
        )
        transcript = " ".join([segment.text for segment in segments]).strip()
        duration = info.duration

        if len(transcript.split()) < 4:
            return {
                "status": "success",
                "transcript": "[No speech detected. Please check your microphone and try again.]",
                "metrics": {"duration_seconds": round(duration, 1), "wpm": 0, "filler_rate": 0.0},
                "overall_score": 0,
                "coach_feedback": {
                  "score_clarity": 0, "score_brevity": 0, "score_structure": 0, "score_bluf": 0,
                  "score_tone": 0, "score_articulation": 0,
                  "feedback_keep": "-",
                  "feedback_change": "We didn't catch enough audio to evaluate.",
                  "feedback_try": "Try speaking louder or check your system microphone volume.",
                  "feedback_tone": "Not enough audio.",
                  "feedback_articulation": "Not enough audio.",
                  "identified_habit": "Silence"
                }
            }

        wpm = calculate_wpm(transcript, duration)
        filler_rate = calculate_filler_rate(transcript)

        prompt = f"""You are an elite, highly critical executive communication coach. Analyze the provided transcript.
        
        The user is responding to this specific scenario:
        "{scenario_text}"
        
        USER'S PAST PRACTICE HISTORY & RECURRING HABITS:
        {history_context if history_context else "This is their first recorded attempt."}
        
        CRITICAL COACHING RULES:
        1. ACTIVE ADAPTATION: If past history shows a recurring negative habit, call out whether they improved or repeated it.
        2. STRICT BLUF SCORING: If the core recommendation or impact is delayed or at the END of the transcript, score BLUF a 1 or 2. Only score a 4 or 5 if the very first sentence contains the main point.
        3. TONE & ARTICULATION: Evaluate the professional tone (confident, empathetic, authoritative) and verbal articulation (enunciation clarity, flow, poise) based on the wording and construction.
        
        Transcript:
        {transcript}
        
        Output format: You must return a valid JSON object matching this exact schema:
        {{
          "score_clarity": [Integer 1-20],
          "score_brevity": [Integer 1-20],
          "score_structure": [Integer 1-15],
          "score_bluf": [Integer 0-5],
          "score_tone": [Integer 1-10],
          "score_articulation": [Integer 1-10],
          "feedback_keep": "[One short, specific thing they did well]",
          "feedback_change": "[The single biggest weakness to fix]",
          "feedback_try": "[Exactly what to say differently]",
          "feedback_tone": "[Specific feedback on executive tone and presence]",
          "feedback_articulation": "[Specific feedback on verbal articulation and flow]",
          "identified_habit": "[One recurring negative habit observed]"
        }}"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

        llm_feedback = json.loads(response.text)
        
        overall_score = calculate_overall_score(
            llm_feedback["score_clarity"],
            llm_feedback["score_brevity"],
            llm_feedback["score_structure"],
            llm_feedback["score_bluf"],
            llm_feedback["score_tone"],
            llm_feedback["score_articulation"],
            filler_rate
        )

        return {
            "status": "success",
            "transcript": transcript,
            "metrics": {
                "duration_seconds": round(duration, 1),
                "wpm": wpm,
                "filler_rate": filler_rate
            },
            "overall_score": overall_score,
            "coach_feedback": llm_feedback
        }
    finally:
        os.remove(temp_path)

# --- START UVICORN SERVER ON EXECUTION ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)