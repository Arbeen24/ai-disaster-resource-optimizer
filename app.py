import streamlit as st
import pandas as pd
import random
import google.generativeai as genai
import os

# ----------------------------
# 🔑 GEMINI CONFIG
# ----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# ----------------------------
# 🎨 GLASS UI
# ----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0E1117, #1a1f2b);
    color: white;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(10px);
    padding:20px;
    border-radius:15px;
    border:1px solid rgba(255,255,255,0.15);
    margin-bottom:15px;
}

/* Header card */
.hero {
    background: rgba(0, 201, 167, 0.15);
    backdrop-filter: blur(10px);
    padding:25px;
    border-radius:15px;
    border:1px solid rgba(0,201,167,0.4);
}

/* Priority subtle text */
.priority {
    font-size: 16px;
    opacity: 0.9;
    margin-top:10px;
}

h1, h2, h3 {
    color: #00C9A7;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATA
# ----------------------------
def get_data():
    cities = ["Bangalore","Mumbai","Delhi","Chennai","Hyderabad","Ahmedabad"]
    types = ["Shelter","Food","Medical","Volunteers"]

    data = []
    for city in cities:
        for t in types:
            for i in range(2):
                data.append({
                    "name": f"{city} {t} Hub {i+1}",
                    "type": t,
                    "location": city,
                    "capacity": random.randint(50,200)
                })
    return pd.DataFrame(data)

df = get_data()

# ----------------------------
# 🤖 AI
# ----------------------------
def get_ai_text(donor, people_needed):
    try:
        prompt = f"{donor['name']} with capacity {donor['capacity']} for {people_needed} people."
        res = model.generate_content(prompt)
        return res.text, True
    except:
        return None, False

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", df["location"].unique())
resource_type = st.sidebar.selectbox("Resource Type", df["type"].unique())
people_needed = st.sidebar.slider("People Needed", 10,200,50)

# ----------------------------
# FILTER
# ----------------------------
filtered = df[df["type"] == resource_type].copy()

def score(row):
    s = 0
    if row["location"] == location:
        s += 50
    s += min(row["capacity"], people_needed)
    return s

filtered["score"] = filtered.apply(score, axis=1)
sorted_df = filtered.sort_values(by="score", ascending=False)

best = sorted_df.iloc[0]

# ----------------------------
# 🧠 AUTO PRIORITY
# ----------------------------
if people_needed > best["capacity"]:
    priority = "🚨 HIGH PRIORITY – Demand exceeds capacity"
elif people_needed > best["capacity"] * 0.7:
    priority = "⚠️ MEDIUM PRIORITY – Limited resources"
else:
    priority = "✅ LOW PRIORITY – Situation under control"

# ----------------------------
# HEADER
# ----------------------------
st.title("🚨 AI Disaster Resource Optimizer")

st.markdown(f"""
<div class="hero">
<h2>🚀 Best Match: {best['name']}</h2>
<div class="priority">{priority}</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# OPTIONS (GLASS CARDS ONLY)
# ----------------------------
st.subheader("🏆 Deployment Options")

for _, row in sorted_df.head(3).iterrows():
    st.markdown(f"""
    <div class="card">
    <h3>{row['name']}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.progress(row["score"]/100)

    if st.button(f"Explain - {row['name']}"):
        ai_text, success = get_ai_text(row, people_needed)

        if success:
            st.markdown(f"""
            <div class="card">
            🤖 <b>AI Insight:</b><br><br>
            {ai_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card">
            📊 <b>Smart Suggestion:</b> {row['name']} can support {row['capacity']} people.<br><br>
            ✅ <b>Recommendation:</b> Deploy based on capacity and location.
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# 📊 CHART
# ----------------------------
st.subheader(f"📊 Resource Distribution in {location}")

city_data = df[df["location"] == location]
chart = city_data.groupby("type")["capacity"].sum()

st.bar_chart(chart)

# ----------------------------
# TABLE
# ----------------------------
st.subheader("📋 Available Resource Providers")
st.dataframe(sorted_df)
