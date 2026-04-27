import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# -------------------------
# CUSTOM CSS (GLASS UI 🔥)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.glass {
    backdrop-filter: blur(14px);
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    transition: 0.3s;
}
.glass:hover {
    transform: translateY(-5px);
    border: 1px solid rgba(255,255,255,0.3);
}
.ai-box {
    background: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# GEMINI SETUP
# -------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# -------------------------
# DATASET
# -------------------------
cities = ["Bangalore", "Mumbai", "Chennai", "Hyderabad"]
types = ["Shelter", "Medical", "Food", "Rescue"]

data = []
for city in cities:
    for t in types:
        for i in range(1, 5):
            data.append({
                "name": f"{city} {t} Hub {i}",
                "type": t,
                "location": city,
                "capacity": random.randint(50, 200)
            })

df = pd.DataFrame(data)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", df["location"].unique())
resource_type = st.sidebar.selectbox("Resource Type", types)
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# -------------------------
# LOGIC
# -------------------------
filtered = df[
    (df["location"] == location) &
    (df["type"] == resource_type)
].copy()

urgency_weight = {"Low": 1, "Medium": 2, "High": 3}

filtered["score"] = (
    filtered["capacity"]
    - people_needed
    + urgency_weight[urgency] * 25
)

sorted_df = filtered.sort_values(by="score", ascending=False)
best = sorted_df.iloc[0]

# -------------------------
# HEADER
# -------------------------
st.title("🚨 AI Disaster Resource Optimizer")
st.warning("Every second matters in disaster response. Choose wisely.")

# -------------------------
# BEST MATCH
# -------------------------
st.markdown(f"""
<div class="glass" style="background: linear-gradient(135deg,#00c6ff,#0072ff); color:white;">
🚀 <b>Best Match:</b> {best['name']}
</div>
""", unsafe_allow_html=True)

# -------------------------
# CARDS + AI
# -------------------------
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(sorted_df.head(3).iterrows()):
    with cols[i]:

        # Capacity status
        if people_needed > row["capacity"]:
            status = "🔴 Cannot handle required people"
            color = "#ff4d4d"
        elif row["capacity"] - people_needed < 25:
            status = "🟡 Limited capacity"
            color = "#ffc107"
        else:
            status = "🟢 Sufficient capacity"
            color = "#28a745"

        key = f"ai_{i}"

        # CARD
        st.markdown(f"""
        <div class="glass">
        <h3>{row['name']}</h3>
        <p>📍 {row['location']}</p>
        <p>👥 Capacity: {row['capacity']}</p>
        <p style="color:{color}; font-weight:bold;">{status}</p>
        </div>
        """, unsafe_allow_html=True)

        # BUTTON
        if st.button("✨ Explain", key=f"btn_{i}"):

            if AI_AVAILABLE:
                try:
                    prompt = f"""
                    You are an AI disaster response assistant.

                    Resource:
                    {row['name']}

                    Capacity: {row['capacity']}
                    People Needed: {people_needed}
                    Urgency: {urgency}

                    Answer clearly:
                    1. Can it handle?
                    2. Should deploy?
                    3. Any risks?

                    Keep it short and practical.
                    """

                    response = model.generate_content(prompt)
                    st.session_state[key] = response.text

                except:
                    st.session_state[key] = "⚠️ AI quota exceeded or error."

            else:
                st.session_state[key] = "⚠️ AI not configured."

        # SHOW AI RESULT
        if key in st.session_state:
            st.markdown(f"""
            <div class="ai-box">
            🤖 {st.session_state[key]}
            </div>
            """, unsafe_allow_html=True)

# -------------------------
# CHART
# -------------------------
st.subheader(f"📊 Resource Distribution in {location}")
st.bar_chart(sorted_df.head(5).set_index("name")["capacity"])

# -------------------------
# TABLE
# -------------------------
st.subheader("📋 Available Resource Providers")
st.dataframe(sorted_df)
