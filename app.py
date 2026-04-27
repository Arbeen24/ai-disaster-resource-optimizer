import streamlit as st
import pandas as pd
import random
import google.generativeai as genai
import os

# ----------------------------
# GEMINI
# ----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(layout="wide")

# ----------------------------
# UI STYLE
# ----------------------------
st.markdown("""
<style>

.main {
    background: linear-gradient(135deg, #0E1117, #1a1f2b);
    color: white;
}

/* INFO BAR */
.info-bar {
    background: #fde68a;
    color: black;
    padding: 10px;
    border-radius: 8px;
}

/* BEST MATCH */
.hero {
    background: rgba(0, 201, 167, 0.15);
    padding: 20px;
    border-radius: 12px;
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.07);
    padding:20px;
    border-radius:12px;
    transition: 0.3s;
    border:1px solid rgba(255,255,255,0.1);
}

.card:hover {
    transform: scale(1.03);
    border:1px solid #00C9A7;
}

/* AI BOX */
.ai-box {
    background: rgba(255,255,255,0.1);
    padding:15px;
    border-radius:10px;
    margin-top:10px;
}

h1, h2, h3 {
    color:#00C9A7;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATA
# ----------------------------
def get_data():
    cities = ["Bangalore","Mumbai","Delhi","Chennai","Hyderabad","Ahmedabad"]
    data = []

    for city in cities:
        for i in range(3):
            data.append({
                "name": f"{city} Shelter Hub {i+1}",
                "location": city,
                "capacity": random.randint(50,200)
            })
    return pd.DataFrame(data)

df = get_data()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", df["location"].unique())
people_needed = st.sidebar.slider("People Needed", 10,200,50)

# ----------------------------
# FILTER
# ----------------------------
filtered = df[df["location"] == location].copy()

filtered["score"] = filtered["capacity"] - people_needed
sorted_df = filtered.sort_values(by="score", ascending=False)

best = sorted_df.iloc[0]

# ----------------------------
# HEADER
# ----------------------------
st.title("🚨 AI Disaster Resource Optimizer")

# INFO BAR
st.markdown("""
<div class="info-bar">
⚠️ Every second matters in disaster response. Choose wisely.
</div>
""", unsafe_allow_html=True)

# BEST MATCH
st.markdown(f"""
<div class="hero">
<h2>🚀 Best Match: {best['name']}</h2>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# 3 CARDS LAYOUT
# ----------------------------
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(sorted_df.head(3).iterrows()):
    with cols[i]:
        st.markdown(f"""
        <div class="card">
        <h3>{row['name']}</h3>
        📍 {row['location']}<br>
        👥 Capacity: {row['capacity']}
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Explain {i}"):
            try:
                prompt = f"{row['name']} capacity {row['capacity']} for {people_needed} people. Explain."
                res = model.generate_content(prompt)

                st.markdown(f"""
                <div class="ai-box">
                🤖 {res.text}
                </div>
                """, unsafe_allow_html=True)

            except:
                st.markdown(f"""
                <div class="ai-box">
                ⚠️ AI unavailable<br><br>
                📊 Supports {row['capacity']} people<br>
                ✅ Recommended deployment
                </div>
                """, unsafe_allow_html=True)

# ----------------------------
# CHART
# ----------------------------
st.subheader(f"📊 Resource Distribution in {location}")

chart = filtered.set_index("name")["capacity"]
st.bar_chart(chart)

# ----------------------------
# TABLE
# ----------------------------
st.subheader("📋 Available Resource Providers")
st.dataframe(sorted_df)
