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
# 🎨 UI STYLE
# ----------------------------
st.markdown("""
<style>
.hero {
    background: #d1fae5;
    padding: 20px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 📊 DATA
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
# 🤖 AI FUNCTION
# ----------------------------
def get_ai_explanation(donor, people_needed):
    try:
        prompt = f"""
        Resource: {donor['name']}
        Type: {donor['type']}
        City: {donor['location']}
        Capacity: {donor['capacity']}
        Demand: {people_needed}

        Explain suitability briefly.
        """

        res = model.generate_content(prompt)

        # ✅ AI WORKING
        return f"""
        <div style="
            background:#e0f2fe;
            padding:15px;
            border-radius:10px;
            border-left:5px solid #0284c7;
        ">
        🤖 <b>AI Insight:</b><br><br>
        {res.text}
        </div>
        """

    except:
        # ⚠️ FALLBACK
        return f"""
        <div style="
            background:#fef3c7;
            padding:15px;
            border-radius:10px;
            border-left:5px solid #f59e0b;
        ">
        ⚠️ <b>AI temporarily unavailable (quota limit)</b><br><br>

        <div style="
            background:#f3f4f6;
            padding:10px;
            border-radius:8px;
            color:black;
        ">
        📊 <b>Smart Suggestion:</b> {donor['name']} can support {donor['capacity']} people.<br><br>
        ✅ <b>Recommendation:</b> Deploy based on capacity and location.
        </div>
        </div>
        """

# ----------------------------
# 🎯 SIDEBAR
# ----------------------------
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", df["location"].unique())
resource_type = st.sidebar.selectbox("Resource Type", df["type"].unique())
urgency = st.sidebar.selectbox("Urgency", ["Low","Medium","High"])
people_needed = st.sidebar.slider("People Needed", 10,200,50)

# ----------------------------
# 🧠 FILTER + SCORE
# ----------------------------
filtered = df[df["type"] == resource_type].copy()

def score(row):
    s = 0
    if row["location"] == location:
        s += 50
    s += min(row["capacity"], people_needed)
    if urgency == "High":
        s += 20
    return s

filtered["score"] = filtered.apply(score, axis=1)
sorted_df = filtered.sort_values(by="score", ascending=False)

# ----------------------------
# 🚨 HEADER
# ----------------------------
st.title("🚨 AI Disaster Resource Optimizer")

best = sorted_df.iloc[0]

st.markdown(f"""
<div class="hero">
<h2>🚀 Best Match: {best['name']}</h2>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# 🏆 OPTIONS
# ----------------------------
st.subheader("🏆 Deployment Options")

for _, row in sorted_df.head(3).iterrows():
    st.write(f"### {row['name']}")
    st.progress(row["score"]/100)

    if st.button(f"Explain - {row['name']}"):
        # ✅ THIS IS THE FIX
        st.markdown(get_ai_explanation(row, people_needed), unsafe_allow_html=True)

# ----------------------------
# 📊 CHART
# ----------------------------
st.subheader(f"📊 Resource Distribution in {location}")

city_data = df[df["location"] == location]

chart_data = (
    city_data.groupby("type")["capacity"]
    .sum()
    .reset_index()
    .set_index("type")
)

st.bar_chart(chart_data)

# ----------------------------
# 📋 TABLE
# ----------------------------
st.subheader("📋 Available Providers")
st.dataframe(sorted_df)
