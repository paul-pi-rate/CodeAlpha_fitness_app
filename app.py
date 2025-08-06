import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

# ---------------------------
# Database setup
# ---------------------------
conn = sqlite3.connect('fitness.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS fitness_data (
        id INTEGER PRIMARY KEY,
        log_date TEXT,
        steps INTEGER,
        workout_time INTEGER,
        exercise_type TEXT,
        calories INTEGER
    )
''')
conn.commit()

# ---------------------------
# Page settings
# ---------------------------
st.set_page_config(page_title="🏋️ Fitness Tracker", layout="centered")
st.title("🏋️‍♂️ Fitness Tracker App")

# ---------------------------
# User Input Form
# ---------------------------
st.subheader("📥 Log Your Fitness Activity")

with st.form("fitness_form"):
    log_date = st.date_input("Date", date.today())
    steps = st.number_input("Steps Walked", min_value=0, step=100)
    workout_time = st.number_input("Workout Duration (mins)", min_value=0, step=5)
    exercise_type = st.selectbox("Exercise Type", ["Running", "Cycling", "Yoga", "Gym", "Walking", "Other"])
    calories = st.number_input("Calories Burned", min_value=0, step=10)

    submitted = st.form_submit_button("Log Activity")

    if submitted:
        cursor.execute('''
            INSERT INTO fitness_data (log_date, steps, workout_time, exercise_type, calories)
            VALUES (?, ?, ?, ?, ?)
        ''', (log_date.isoformat(), steps, workout_time, exercise_type, calories))
        conn.commit()
        st.success("✅ Activity Logged!")

# ---------------------------
# Dashboard / Summary
# ---------------------------
st.subheader("📊 Your Activity Summary")

# Fetch last 7 days data
today = date.today()
seven_days_ago = today - timedelta(days=6)
cursor.execute('''
    SELECT * FROM fitness_data WHERE log_date BETWEEN ? AND ?
''', (seven_days_ago.isoformat(), today.isoformat()))
rows = cursor.fetchall()

# Display data
if rows:
    df = pd.DataFrame(rows, columns=["ID", "Date", "Steps", "Workout (min)", "Exercise", "Calories"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Show table
    st.dataframe(df[["Date", "Steps", "Workout (min)", "Exercise", "Calories"]], use_container_width=True)

    # Plotting
    st.write("### 📈 Weekly Steps Progress")
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Steps"], marker='o', color='green')
    ax.set_ylabel("Steps")
    ax.set_xlabel("Date")
    ax.grid(True)
    st.pyplot(fig)

    st.write("### 🔥 Calories Burned")
    st.bar_chart(df.set_index("Date")["Calories"])

else:
    st.info("No data available for the last 7 days. Log your activity above.")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption("💪 Built with Streamlit and SQLite for local tracking")
