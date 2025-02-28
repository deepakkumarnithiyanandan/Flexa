import streamlit as st
import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import re 

# Ensure database folder exists
os.makedirs("./database", exist_ok=True)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Load user profile data
PROFILE_PATH = "./database/user_profiles.json"
WORKOUT_HISTORY_PATH = "./database/workout_history.json"
STREAK_TRACKER_PATH = "./database/streak_tracker.json"


def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}


def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def generate_plan_with_gemini(prompt):
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=data, headers=headers)

        if response.status_code != 200:
            st.error(f"Gemini API Error: {response.status_code} - {response.text}")
            return "{}"

        response_json = response.json()

        if "candidates" in response_json and response_json["candidates"]:
            text_response = response_json["candidates"][0]["content"]["parts"][0]["text"]
            
            # 🔍 Remove markdown-style triple backticks if present
            text_response = re.sub(r"```json\s*", "", text_response)  # Remove ```json
            text_response = re.sub(r"```", "", text_response)  # Remove closing ```

            # 🔍 Ensure valid JSON before returning
            try:
                parsed_json = json.loads(text_response)
                return json.dumps(parsed_json)  # Return properly formatted JSON string
            except json.JSONDecodeError:
                st.error("❌ Gemini API returned invalid JSON. Please check output.")
                st.write("🔍 Raw Response:", text_response)
                return "{}"

        else:
            st.warning("⚠️ Gemini API did not return a valid response.")
            return "{}"

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request Exception: {e}")
        return "{}"

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Decode Error: {e}")
        return "{}"


def generate_meal_plan():
    prompt = """
    Generate a **5-day healthy meal plan** in **strict JSON format only** with the following structure:

    {
        "Monday": {
            "Breakfast": "Oatmeal with berries",
            "Lunch": "Grilled chicken with salad",
            "Snack": "Apple with peanut butter",
            "Dinner": "Baked salmon with quinoa"
        },
        "Tuesday": { ... },
        "Wednesday": { ... },
        "Thursday": { ... },
        "Friday": { ... }
    }

    **Rules:**
    - **DO NOT** include any extra text, explanations, disclaimers, or headings.
    - **DO NOT** include markdown formatting.
    - The response **MUST** be **valid JSON only**.
    - Ensure all keys are days of the week, and each contains "Breakfast", "Lunch", "Snack", and "Dinner".
    """

    response = generate_plan_with_gemini(prompt)
    
    try:
        return json.loads(response)  # Ensure response is valid JSON
    except json.JSONDecodeError:
        st.error("❌ Gemini API returned invalid JSON for Meal Plan.")
        st.write("🔍 Raw Response:", response)
        return {}



def generate_workout_plan():
    prompt = """
    Generate a **5-day workout plan** in **strict JSON format only** with this structure:

    {
        "Monday": "Full-body strength training",
        "Tuesday": "Cardio and flexibility",
        "Wednesday": "Active recovery or rest",
        "Thursday": "Lower body strength training",
        "Friday": "Yoga and core workouts"
    }

    **Rules:**
    - **DO NOT** include any extra text, explanations, disclaimers, or headings.
    - **DO NOT** use markdown formatting.
    - The response **MUST** be **valid JSON only**.
    """

    response = generate_plan_with_gemini(prompt)

    try:
        return json.loads(response)  # Ensure response is valid JSON
    except json.JSONDecodeError:
        st.error("❌ Gemini API returned invalid JSON for Workout Plan.")
        st.write("🔍 Raw Response:", response)
        return {}



def get_cheapest_shopping_links():
    # Hardcoded grocery items with nutrition info and links
    return [
        {"Item": "Bananas", "Nutrition": "Rich in potassium, vitamin B6, fiber", "Link": "https://www.walmart.com/ip/Dole-Bananas/44390934"},
        {"Item": "Oats", "Nutrition": "High in fiber, good for heart health", "Link": "https://www.walmart.com/ip/Quaker-Old-Fashioned-Oats-42oz/10315307"},
        {"Item": "Greek Yogurt", "Nutrition": "High in protein, probiotics for gut health", "Link": "https://www.walmart.com/ip/Great-Value-Plain-Nonfat-Greek-Yogurt-32oz/46782241"},
        {"Item": "Chicken Breast", "Nutrition": "Lean protein, low in fat", "Link": "https://www.walmart.com/ip/Tyson-All-Natural-Boneless-Skinless-Chicken-Breast/12345678"},
        {"Item": "Brown Rice", "Nutrition": "Whole grain, high in fiber", "Link": "https://www.walmart.com/ip/Great-Value-Whole-Grain-Brown-Rice-5lbs/10452012"},
        {"Item": "Almond Butter", "Nutrition": "Healthy fats, vitamin E, protein", "Link": "https://www.walmart.com/ip/Barney-Butter-Smooth-Almond-Butter-16oz/999392098"},
        {"Item": "Eggs", "Nutrition": "High in protein, rich in choline", "Link": "https://www.walmart.com/ip/Great-Value-Large-White-Eggs-12ct/123456789"},
        {"Item": "Peanut Butter", "Nutrition": "Healthy fats, good protein source", "Link": "https://www.walmart.com/ip/Jif-Natural-Creamy-Peanut-Butter-16oz/23732861"},
        {"Item": "Spinach", "Nutrition": "Rich in iron, vitamin K, antioxidants", "Link": "https://www.walmart.com/ip/Marketside-Organic-Baby-Spinach-5oz/976673501"}
    ]



def display_calendar(meal_plan, workout_plan, streak_tracker):
    st.subheader("📅 Weekly Plan Overview")
    days = list(meal_plan.keys())

    if "streak_tracker" not in st.session_state:
        st.session_state.streak_tracker = streak_tracker
    
    streak_score = 0
    for day in days:
        checked = st.checkbox(f"✅ {day} Completed", value=st.session_state.streak_tracker.get(day, False), key=day)
        st.session_state.streak_tracker[day] = checked
    
    streak_score = sum(1 for day in days if st.session_state.streak_tracker.get(day, False))
    save_json(STREAK_TRACKER_PATH, st.session_state.streak_tracker)
    
    st.write(f"🔥 **Current Streak Score:** {streak_score} days")
    
    calendar_df = pd.DataFrame({
        "Day": days,
        "Breakfast": [meal_plan[day]["Breakfast"] for day in days],
        "Lunch": [meal_plan[day]["Lunch"] for day in days],
        "Snack": [meal_plan[day]["Snack"] for day in days],
        "Dinner": [meal_plan[day]["Dinner"] for day in days],
        "Workout": [workout_plan[day] for day in days]
    })
    st.dataframe(calendar_df)


def display_graphs(workout_history):
    df = pd.DataFrame(workout_history)
    if df.empty:
        st.warning("No workout data available.")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Calories burnt over time
    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["calories"], marker="o", linestyle="-", label="Calories Burnt")
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories Burnt")
    ax.set_title("Calories Burnt Over Time")
    ax.legend()
    st.pyplot(fig)
    
    # Exercise score trend
    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["score"], marker="s", linestyle="--", color="green", label="Exercise Score")
    ax.set_xlabel("Date")
    ax.set_ylabel("Form Score (%)")
    ax.set_title("Exercise Score Progress")
    ax.legend()
    st.pyplot(fig)

def main():
    with st.spinner('⏳ Flexa is curating a customized plan for you...'):
        user_profiles = load_json(PROFILE_PATH)
        workout_history = load_json(WORKOUT_HISTORY_PATH)
        streak_tracker = load_json(STREAK_TRACKER_PATH)

        if not user_profiles:
            st.error("No user profiles found. Please create your profile in 'Me, Myself & Flex'.")
        else:
            st.title("🥑 Munch & Crunch - Personalized Lifestyle Plan")
            meal_plan = generate_meal_plan()
            workout_plan = generate_workout_plan()

            display_calendar(meal_plan, workout_plan, streak_tracker)

            st.subheader("📊 Your Progress")
            display_graphs(workout_history)

            st.success("Your customized 5-day meal & workout plan is ready! 🥗💪")

            # ✅ Display the Grocery List as a Table
            st.subheader("🛒 Cheapest Grocery Links")
            grocery_list = get_cheapest_shopping_links()
            
            # Convert list to DataFrame
            grocery_df = pd.DataFrame(grocery_list)
            
            # ✅ Keep the raw clickable link (no alt text)
            grocery_df["Link"] = grocery_df["Link"].apply(lambda x: f"<a href='{x}' target='_blank'>{x}</a>")

            st.markdown("### Grocery List", unsafe_allow_html=True)
            st.write(grocery_df.to_html(escape=False, index=False), unsafe_allow_html=True)


