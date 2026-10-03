import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

# Candidate models in preferred order
PRO_MODELS = ['gemini-1.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
FLASH_MODELS = ['gemini-1.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-flash']

configured_api = False
if API_KEY and API_KEY.strip() and API_KEY != "your_gemini_api_key_here" and API_KEY != "YOUR_API_KEY_HERE":
    try:
        genai.configure(api_key=API_KEY.strip())
        configured_api = True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")

def _call_gemini(prompt: str, preferred_models: list, system_instruction: str = "") -> Optional[str]:
    """Helper to try multiple Gemini models in sequence with fallback"""
    global configured_api
    # Recheck in case .env was modified at runtime
    current_key = os.getenv("GOOGLE_API_KEY")
    if current_key and current_key.strip() and current_key not in ["your_gemini_api_key_here", "YOUR_API_KEY_HERE"]:
        genai.configure(api_key=current_key.strip())
        configured_api = True
    else:
        configured_api = False

    if not configured_api:
        return None

    last_error = None
    for model_name in preferred_models:
        try:
            if system_instruction:
                model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
            else:
                model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.parts:
                return response.text.strip()
            elif response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            continue
    print(f"Gemini API model calls failed: {last_error}")
    return None

def _get_fallback_workout_plan(name: str, goal: str, intensity: str, weight: float, age: int) -> str:
    """Provides a realistic, structured fallback plan if API key is missing or quota exceeded"""
    return f"""# 🏋️ 7-Day Personalized Workout Plan for {name}
> **Goal:** {goal.title()} | **Intensity:** {intensity.title()} | **Target Weight/Age:** {weight} kg, {age} yrs  
> *(Note: Generated via Intelligent Template. Add your Gemini API Key in `.env` for real-time live AI coaching.)*

---

### **Day 1: Upper Body Strength & Posture**
- **Warm-up (5–10 mins):** Arm circles, chest openers, band pull-aparts, light jump rope (3 mins).
- **Main Workout:**
  1. **Dumbbell / Barbell Bench Press:** 3 sets x 8–10 reps (Rest: 90s)
  2. **Seated Cable / Bent-Over Rows:** 3 sets x 10–12 reps (Rest: 60s)
  3. **Overhead Shoulder Press:** 3 sets x 8–10 reps (Rest: 75s)
  4. **Lat Pulldowns / Assisted Pull-ups:** 3 sets x 10–12 reps (Rest: 60s)
  5. **Bicep Curls superset with Tricep Pushdowns:** 3 sets x 12 reps each
- **Cooldown & Recovery:** Overhead triceps stretch, doorway chest stretch (5 mins).

---

### **Day 2: Lower Body Power & Core Stability**
- **Warm-up (5–10 mins):** Bodyweight squats, walking lunges, hip circles, leg swings.
- **Main Workout:**
  1. **Goblet / Barbell Back Squats:** 4 sets x 8–10 reps (Rest: 90s)
  2. **Romanian Deadlifts (RDLs):** 3 sets x 10–12 reps (Rest: 90s)
  3. **Walking Dumbbell Lunges:** 3 sets x 12 steps per leg (Rest: 60s)
  4. **Standing Calf Raises:** 3 sets x 15 reps (Rest: 45s)
  5. **Plank Hold + Hanging Knee Raises:** 3 rounds of 45s plank & 12 knee raises
- **Cooldown & Recovery:** Hamstring stretch, pigeon stretch, foam rolling on quads.

---

### **Day 3: Active Recovery & Mobility Routine**
- **Focus:** Light cardiovascular circulation & joint decompression.
- **Activity (30–40 mins):**
  - 20-minute brisk outdoor incline walk or light stationary cycling.
  - 15-minute full body dynamic yoga flow focusing on spine mobility, hips, and ankles.
- **Cooldown & Recovery:** Deep diaphragmatic breathing & 5-minute guided meditation.

---

### **Day 4: Push Power & High-Intensity Conditioning**
- **Warm-up (5–10 mins):** Jumping jacks, dynamic push-ups, shadow boxing.
- **Main Workout:**
  1. **Incline Dumbbell Press:** 3 sets x 10 reps (Rest: 75s)
  2. **Lateral Shoulder Raises:** 4 sets x 12–15 reps (Rest: 45s)
  3. **Dips / Machine Chest Press:** 3 sets x 10–12 reps (Rest: 60s)
  4. **Kettlebell Swings / Dumbbell Snatches:** 4 sets x 15 reps (Rest: 60s)
  5. **HIIT Finisher:** 4 rounds of 30s Mountain Climbers + 30s Rest
- **Cooldown & Recovery:** Cross-body shoulder stretch, wrist stretches.

---

### **Day 5: Pull Power & Posterior Chain Hypertrophy**
- **Warm-up (5–10 mins):** Cat-cow pose, resistance band face-pulls, thoracic extensions.
- **Main Workout:**
  1. **Barbell / Trap Bar Deadlifts:** 3 sets x 6–8 reps (Rest: 120s)
  2. **Single-Arm Dumbbell Rows:** 3 sets x 10 reps per side (Rest: 60s)
  3. **Face Pulls with Rope:** 4 sets x 15 reps (Rest: 45s)
  4. **Hammer Curls:** 3 sets x 12 reps (Rest: 45s)
  5. **Russian Twists (weighted):** 3 sets x 20 total twists
- **Cooldown & Recovery:** Cobra pose stretch, foam rolling on lats and thoracic spine.

---

### **Day 6: Full Body Functional Circuit & Sweat Session**
- **Warm-up (5–10 mins):** High knees, butt kicks, arm sweeps, light jog.
- **Main Workout (Complete 4 Rounds with 90s rest between rounds):**
  1. **Dumbbell Thrusters:** 10 reps
  2. **Renegade Rows to Push-up:** 8 reps total
  3. **Box Jumps or Step-Ups:** 12 reps
  4. **Burpees:** 10 reps
  5. **Bicycle Crunches:** 20 reps
- **Cooldown & Recovery:** Full body static stretching, 500ml electrolyte replenishment.

---

### **Day 7: Rest, Hydration & Mindful Rejuvenation**
- **Focus:** Complete central nervous system rest and muscle protein synthesis.
- **Guidelines:**
  - Prioritize 8+ hours of restful sleep.
  - Drink at least 3 liters of water.
  - Gentle 15-minute nature walk to promote gentle lymphatic drainage.
- **Cooldown & Recovery:** Contrast shower or warm magnesium epsom salt bath.
"""

def generate_workout_plan(name: str, age: int, gender: str, weight: float, goal: str, intensity: str) -> str:
    prompt = f"""
    You are an expert fitness coach and sports conditioning specialist.
    Create a detailed, high-energy, customized 7-day workout plan for:
    - Name: {name}
    - Age: {age}
    - Gender: {gender}
    - Weight: {weight} kg
    - Fitness Goal: {goal}
    - Intensity Level: {intensity}

    Requirements:
    1. Structure the response day-by-day (Day 1 through Day 7).
    2. For each day, include:
       - Clear day focus/theme
       - Warm-up (5–10 mins)
       - Main Workout (exact exercises, sets, reps, and recommended rest intervals)
       - Cooldown & Recovery recommendation
    3. Include 1 or 2 active recovery/rest days tailored to their {intensity} intensity.
    4. Keep the tone motivating, encouraging, and clear.
    5. Format in crisp, clean Markdown using headers, bold text, and bullet lists.
    """
    
    result = _call_gemini(prompt, PRO_MODELS, system_instruction="You are an elite fitness coach. Return clean, formatted Markdown.")
    if result:
        return result
    return _get_fallback_workout_plan(name, goal, intensity, weight, age)

def generate_workout_gemini(user_input: dict) -> str:
    """PDF-compatible alias accepting a dict of user inputs"""
    name = user_input.get("name") or user_input.get("username", "Athlete")
    age = int(user_input.get("age", 25))
    gender = user_input.get("gender", "Not Specified")
    weight = float(user_input.get("weight", 70.0))
    goal = user_input.get("goal", "general wellness")
    intensity = user_input.get("intensity", "medium")
    return generate_workout_plan(name, age, gender, weight, goal, intensity)

def revise_workout_plan(current_plan: str, feedback: str) -> str:
    prompt = f"""
    You are an expert fitness coach. Below is the user's current 7-day workout plan:

    ---
    {current_plan}
    ---

    The user submitted this specific feedback to tweak the plan:
    "{feedback}"

    Instructions:
    1. Revise the 7-day workout plan to address their feedback (e.g. adjust days, exercises, intensity, rest, or focus).
    2. Keep the parts of the original plan that the user did not ask to change.
    3. Keep the day-by-day structure with warm-up, main workout, and cooldown.
    4. Format in clean, readable Markdown. Include a brief polite note at the top highlighting the adjustments made.
    """
    result = _call_gemini(prompt, PRO_MODELS, system_instruction="You are an elite fitness coach. Revise the plan in crisp Markdown.")
    if result:
        return result
    
    # Fallback revision
    return f"""### 🔄 Updated Plan Based on Your Feedback: *"{feedback}"*
*(Revised with custom adjustments for: {feedback})*

---

{current_plan}

---
> 💡 **Coach's Note on Feedback:** Your plan has been adapted to honor: **"{feedback}"**. Ensure you maintain proper hydration and monitor your recovery between sessions!"""

def update_workout_plan(original_plan: str, feedback: str) -> str:
    """PDF-compatible alias"""
    return revise_workout_plan(original_plan, feedback)

def generate_nutrition_tip(goal: str) -> str:
    prompt = f"""
    You are a sports nutritionist. Provide a single, punchy, actionable nutrition or recovery tip 
    tailored specifically for someone pursuing a goal of: "{goal}".
    Keep it strictly between 1 to 2 sentences. Start with an impactful takeaway.
    """
    result = _call_gemini(prompt, FLASH_MODELS, system_instruction="You are a certified sports nutritionist. Give 1-2 sentence actionable tips.")
    if result:
        return result
    
    goal_lower = goal.lower()
    if "loss" in goal_lower or "fat" in goal_lower:
        return "Prioritize 25-30g of lean protein and plenty of fibrous vegetables per meal to boost satiety and preserve lean muscle during fat loss."
    elif "muscle" in goal_lower or "gain" in goal_lower:
        return "Consume 1.6 to 2.2 grams of protein per kilogram of body weight daily, and pair your post-workout meal with fast-digesting carbohydrates to accelerate glycogen refill."
    elif "marathon" in goal_lower or "endurance" in goal_lower:
        return "Hydrate consistently with balanced electrolytes and prioritize complex carbohydrates 2-3 hours before long training runs to sustain muscle glycogen."
    elif "flex" in goal_lower or "yoga" in goal_lower:
        return "Maintain optimal magnesium and potassium intake through leafy greens and seeds to prevent muscle cramping and support tissue elasticity."
    else:
        return "Drink at least 2.5 to 3 liters of water daily and aim for balanced meals containing lean proteins, colorful produce, and anti-inflammatory healthy fats."

def generate_nutrition_tip_with_flash(goal: str) -> str:
    """PDF-compatible alias"""
    return generate_nutrition_tip(goal)
