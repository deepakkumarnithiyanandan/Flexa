import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from streamlit_lottie import st_lottie
import requests
from dotenv import load_dotenv
from bill import process_bill
from stripe_payment import process_payment, get_payment_history
from trainer import track_exercise
from analytics import main


# --- Page Config ---
st.set_page_config(page_title="Flexa", page_icon="🍑", layout="wide")

# Ensure database folder exists
os.makedirs("./database", exist_ok=True)

# Load API keys from .env
load_dotenv()

# Function to load existing user data
def load_user_data():
    file_path = "./database/user_profiles.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

# Function to save user data
def save_user_data(user_data):
    file_path = "./database/user_profiles.json"
    
    existing_data = load_user_data()
    
    # Auto-increment user ID
    new_user_id = len(existing_data) + 1
    existing_data[new_user_id] = user_data
    
    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)
    
    return new_user_id
# --- Function to Fetch Lottie Animations ---
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- Lottie Animations ---
splitwise_animation = load_lottie_url("https://lottie.host/9e72d50f-9219-4e27-970c-95d7d604d1ba/3BNR1SE38T.json")
girl_1T = load_lottie_url("https://lottie.host/e4d68804-020b-493d-ac54-cb23ae9164c2/45Oof5ee2s.json")
posture = load_lottie_url("https://lottie.host/76c6d628-9e39-4099-b55d-27b5489ee557/q1GGTjMa0O.json")
death_dancing = load_lottie_url("https://lottie.host/5f97f66c-b96a-493c-9d98-e61c49fce1b3/AEZhJ3cU05.json")
monkey_meme = load_lottie_url("https://lottie.host/16250878-84bd-4217-87ef-fdd7e07f29fd/aZqhphCqwO.json")
shopping = load_lottie_url("https://lottie.host/cc901e2f-dcdf-4d82-bbb8-6779edf048ab/oP1M0GjOLV.json")
cat_meme = load_lottie_url("https://lottie.host/897fe626-fb4d-45a0-9168-896307e53c83/IdPpNgiPtJ.json")
auth = load_lottie_url("https://lottie.host/347edf77-cab1-4bcd-bd40-1d41ac914957/o8OfUiv8cc.json")


# --- Sidebar ---
st.sidebar.title("🔥 **Flexa Navigation**")
section = st.sidebar.radio("Select a Section:", [
    "📝 Me, Myself & Flex",
    "💪 Flexa-Tron 3000",
    "🥑 Munch & Crunch",
    "💸 Flexa"
])

# Add a space before pet animation for better positioning
st.sidebar.markdown("<br>", unsafe_allow_html=True)
with st.sidebar:
    st_lottie(monkey_meme, height=200, key="keto_pet")

# --- Main Page ---
# st.title("**Welcome to Flexa!** 🚀")
# st.write("### If Life was easy, You wouldn’t need Us!!")

if section == "📝 Me, Myself & Flex":
    st.title("**Welcome to Flexa!** 🚀")
    st.write("### If Life was easy, You wouldn’t need Us!!")
    st.header("📝 Me, Myself & Flex")
    # st.write("*Because your profile deserves some gains too!* 😎")

    with st.form("user_profile_form"):
        st.subheader("👤 Personal Details")
        # st.write("*Because your profile deserves some gains too!* 😎")
        name = st.text_input("Full Name", placeholder="Enter your name")
        email = st.text_input("Email", placeholder="Enter your email")

        st.subheader("🥗 Health & Fitness")
        dietary_restrictions = st.text_area("Dietary Restrictions", placeholder="Any allergies or diet plans?")
        
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", min_value=50, max_value=250, step=1)
        with col2:
            weight = st.number_input("Weight (kg)", min_value=20, max_value=300, step=1)

        st.subheader("🎯 Goals & Activity")
        goal_options = ["Bulking 🏋️", "Cutting 🔥", "Lean Bulk 💪", "Maintain ⚖️", "Flexibility & Mobility 🤸"]
        goal = st.selectbox("Fitness Goal", goal_options)

        activity_options = ["Sedentary (little to no exercise)", "Lightly active (1-3 days/week)", 
                            "Moderately active (3-5 days/week)", "Very active (6-7 days/week)", 
                            "Super active (Athlete level)"]
        activity_level = st.selectbox("Activity Level", activity_options)

        submit_button = st.form_submit_button("Save Profile", type="primary")

    if submit_button:
        user_data = {
            "name": name,
            "email": email,
            "dietary_restrictions": dietary_restrictions,
            "height": height,
            "weight": weight,
            "goal": goal,
            "activity_level": activity_level
        }

        user_id = save_user_data(user_data)
        st.success(f"Profile Saved! 🚀 (User ID: {user_id})")
    
elif section == "💪 Flexa-Tron 3000":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💪 Flexa-Tron 3000 - AI Trainer")
        st.write("🏋️ **AI-powered workout tracker. Track reps, form, and calories!**")

        # Select exercise and number of reps
        exercise_options = ["Bicep Curls", "Yoga", "pilates", "Squats", "Push-ups", "Lunges", "Deadlifts", "Planks", "Bench Press"]
        selected_exercise = st.selectbox("🏋️ Choose an Exercise:", exercise_options)
        
        rep_count = st.number_input("🔢 Number of Reps:", min_value=1, step=1, value=10)

        # Start Workout Button
        if st.button("🎥 Start Workout"):
            with st.spinner("Tracking your workout..."):
                result = track_exercise(selected_exercise, rep_count)

            if result["success"]:
                st.success(f"✅ Workout Completed: {result['reps']} reps | Calories Burned: {result['calories']} kcal")
                st.image(result["chart_path"], caption="📈 Form Score Chart", use_column_width=True)
            else:
                st.error(result["message"])

        # 📜 Display Workout History
        st.subheader("📜 Workout History")

        # Load workout history from JSON
        workout_history_path = "./database/workout_history.json"
        
        if os.path.exists(workout_history_path):
            with open(workout_history_path, "r") as file:
                workout_history = json.load(file)

            if workout_history:
                df = pd.DataFrame(workout_history)
                df = df[["timestamp", "exercise_name", "reps", "score", "calories"]]  
                st.dataframe(df)
            else:
                st.info("📂 No past workouts found.")

    with col2:
        st_lottie(girl_1T, height=300, key="posture")# Display posture animation

elif section == "🥑 Munch & Crunch":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🥑 Munch & Crunch")
        st.write("*Diet so good, even Gordon Ramsay won’t yell at you!* 🍔🥗")
        st.sidebar.info("Macros or McNuggets? Why not both? 🍔🥗.")

        if st.button("Build my lifestyle with FlexAI", type="primary"):
            main()  # Calls the function from analytics.py

    with col2:
        st_lottie(shopping, height=300, key="shopping")

elif section == "💸 Flexa":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💸 Flexa - Bill Splitting System")

        # File uploader outside of button click
        uploaded_file = st.file_uploader("📄 Upload your bill image", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            process_button = st.button("🧾 Process Bill with FlexAI", type="primary")

            if process_button:
                with st.spinner("Processing bill..."):
                    structured_data = process_bill(uploaded_file)

                    if structured_data:
                        st.success("Bill processed successfully! 🎉")
                        with open("./database/bill_data.json", "w") as json_file:
                            json.dump(structured_data, json_file, indent=4)

    # Load bill data if available
    bill_data_path = "./database/bill_data.json"
    if os.path.exists(bill_data_path):
        with open(bill_data_path, "r") as file:
            bill_data = json.load(file)

        if bill_data:
            st.subheader(f"💰 Split Bill: {bill_data['bill_id']} - {bill_data['bill_name']}")

            # Step 1: Choose Split Type
            split_type = st.radio("📊 How do you want to split?", ["Split Equally", "Customize"])

            if split_type == "Split Equally":
                # Step 2: Split Bill Equally
                users = ["Kayla", "Nandan", "Deepak", "Lily"]
                
                # ✅ Calculate total bill including taxes
                total_amount = sum(item["price"] * item["quantity"] for item in bill_data["items"]) 
                total_amount += sum(tax["amount"] for tax in bill_data["taxes"])  # ✅ Fixed tax sum

                equal_split = round(total_amount / len(users), 2)

                split_result = {user: equal_split for user in users}

                st.subheader("💰 Equal Split Breakdown")
                st.write(f"Each person owes: **${equal_split}**")
                st.json(split_result)

                # ✅ Display Graph for Equal Split
                fig, ax = plt.subplots()
                ax.bar(split_result.keys(), split_result.values(), color=['blue', 'green', 'red', 'purple'])
                ax.set_ylabel("Amount ($)")
                ax.set_title("Equal Bill Split Per Person")
                st.pyplot(fig)

                # ✅ Show in table format
                df = pd.DataFrame.from_dict(split_result, orient="index", columns=["Amount Owed"])
                st.table(df)

            else:
                # Ensure payment history file exists
                os.makedirs("./database", exist_ok=True)
                payment_history_path = "./database/payment_history.json"

                if not os.path.exists(payment_history_path):
                    with open(payment_history_path, "w") as file:
                        json.dump([], file, indent=4)

                # Step 2: Select users who participated
                users = ["Kayla", "Nandan", "Deepak", "Lily"]
                selected_users = st.multiselect("👥 Who ate this bill?", users)

                if selected_users:
                    st.subheader("🍽 Assign Items & Share")
                    item_options = {item["item_name"]: (item["price"], item["quantity"]) for item in bill_data["items"]}

                    # ✅ Calculate total bill before assignments
                    total_amount = sum(item["price"] * item["quantity"] for item in bill_data["items"]) 
                    remaining_amount = total_amount  # Track unassigned amount

                    user_shares = {}

                    for user in selected_users:
                        st.write(f"👤 **{user}**")
                        selected_item = st.selectbox(f"Item for {user}", list(item_options.keys()), key=f"{user}_item")
                        max_percentage = item_options[selected_item][1] * 100  # Max % based on item quantity

                        share = st.number_input(
                            f"{user}'s % share", min_value=0, max_value=max_percentage, step=1, key=f"{user}_share"
                        )

                        user_shares[user] = {"item": selected_item, "share": share}
                        item_price = item_options[selected_item][0] * (share / 100)  # Calculate user’s portion

                        remaining_amount -= item_price  # ✅ Deduct assigned amount

                    # Display remaining amount dynamically
                    st.subheader(f"💰 Remaining Amount: **${round(remaining_amount, 2)}**")

                    # Ensure all items are accounted for
                    if remaining_amount > 0:
                        st.warning("⚠ Some items are unassigned! Ensure all are accounted for.")

                    # Step 3: Tax Splitting Option
                    tax_split_method = st.radio("🧾 Split Taxes & Tips:", ["Equally", "Proportionally"])

                    # Calculate Split
                    if st.button("💸 Calculate Split"):
                        total_taxes = sum(tax["amount"] for tax in bill_data["taxes"])  # ✅ Fixed tax sum issue
                        split_result = {}

                        for user, data in user_shares.items():
                            item_cost = item_options[data["item"]][0] * (data["share"] / 100)

                            if tax_split_method == "Equally":
                                user_taxes = total_taxes / len(selected_users)
                            else:
                                user_taxes = (item_cost / total_amount) * total_taxes

                            split_result[user] = round(item_cost + user_taxes, 2)

                        st.subheader("💰 Final Split Breakdown")
                        st.json(split_result)

                        # ✅ Display Graph for Custom Split
                        fig, ax = plt.subplots()
                        ax.bar(split_result.keys(), split_result.values(), color=['blue', 'green', 'red', 'purple'])
                        ax.set_ylabel("Amount ($)")
                        ax.set_title("Custom Bill Split Per Person")
                        st.pyplot(fig)

                        # ✅ Show in table format
                        df = pd.DataFrame.from_dict(split_result, orient="index", columns=["Amount Owed"])
                        st.table(df)

                        # Define test users (replace with dynamic user creation)
                        users = {
                            "Kayla": "acct_test1",
                            "Nandan": "acct_test2",
                            "Deepak": "acct_test3",
                            "Lily": "acct_test4"
                        }

                        st.subheader("💳 Send Payment via Stripe")

                        # Select sender & receiver
                        sender = st.selectbox("🧑‍💼 Who is paying?", list(users.keys()))
                        receiver = st.selectbox("🎯 Who is receiving the payment?", [u for u in users.keys() if u != sender])

                        # Select amount to pay
                        amount = st.number_input("💰 Enter Amount to Pay ($)", min_value=1.0, step=0.01)

                        if st.button("💸 Pay Now with Stripe"):
                            result = process_payment(sender, receiver, amount)

                            if result["success"]:
                                st.success(result["message"])
                                st.write(f"🔗 [View Payment](https://dashboard.stripe.com/test/payments/{result['payment_id']})")
                            else:
                                st.error(result["message"])

                        # 📜 Display Payment History
                        st.subheader("📜 Payment History")

                        payment_history = get_payment_history()

                        if payment_history:
                            df = pd.DataFrame(payment_history)
                            df = df[["timestamp", "sender", "receiver", "amount", "status"]]  # Order columns
                            st.dataframe(df)
                        else:
                            st.info("📂 No past payments found.")

    with col2:
        st_lottie(splitwise_animation, height=300, key="splitwise")

# Footer for all pages - Centered
st.markdown("""
    <style>
        .footer {
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 0px;
            font-size: 16px;
        }
    </style>
    <div class='footer'>
        Made by Flexa with ❣️
    </div>
""", unsafe_allow_html=True) 

# Hide Streamlit's default top bar, menu, and footer
st.markdown("""
    <style>
        /* Hide top bar */
        header {visibility: hidden;}

        /* Hide menu & footer */
        #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)



        

