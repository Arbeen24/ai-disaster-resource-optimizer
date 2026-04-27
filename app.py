import streamlit as st
import pandas as pd
import random

# Gemini
import google.generativeai as genai

# ================== CONFIG ==================
st.set_page_config(page_title="AI Disaster Resource Optimizer", layout="wide")

# ================== GEMINI SETUP ==================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# ================== UI STYLES ==================
st.markdown("""
<style>
body {
    background-color: #0b0f19;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #020617);
    color: white;
}

/* Glass Cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    transition: 0.3s;
}
.glass-card:hover {
    transform: scale(1.03);
    border: 1px solid #00ffe0;
}

/* AI Box */
.ai-box {
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 10px;
    margin-top: 10px;
    border-left: 4px solid #00ffcc;
}

/* Warning */
.warning-box {
    background: #facc15;
    color: black;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 15px;
}

/* Best match */
.best-match {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    padding: 20px;
    border-radius: 12px;
    font-size: 20px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
cities = ["Bangalore", "Mumbai", "Chennai", "Hyderabad", "Delhi"]

data = []
for city in cities:
    for i in range(1, 6):
        for t in ["Shelter", "Medical", "Food"]:
            data.append({
                "name": f"{city} {t} Hub {i}",
                "type": t,
                "location": city,
                "capacity": random.randint(60, 200)
            })

df = pd.DataFrame(data)

# ================== SIDEBAR ==================
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", cities)
resource_type = st.sidebar.selectbox("Resource Type", ["Shelter", "Medical", "Food"])
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 80)

st.sidebar.success(f"🌍 {len(cities)} Cities Supported")

# ================== FILTER ==================
filtered = df[(df["location"] == location) & (df["type"] == resource_type)].copy()

# scoring
urgency_weight = {"Low":1, "Medium":2, "High":3}[urgency]
filtered["score"] = filtered["capacity"] * urgency_weight
filtered = filtered.sort_values(by="score", ascending=False)

best = filtered.iloc[0]

# ================== TITLE ==================
st.title("🚨 AI Disaster Resource Optimizer")

st.markdown('<div class="warning-box">⚠️ Every second matters in disaster response. Choose wisely.</div>', unsafe_allow_html=True)

st.markdown(f'<div class="best-match">🚀 Best Match: {best["name"]}</div>', unsafe_allow_html=True)

# ================== DEPLOYMENT ==================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(filtered.head(3).iterrows()):
    with cols[i]:

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.markdown(f"### {row['name']}")
        st.write(f"📍 {row['location']}")
        st.write(f"👥 Capacity: {row['capacity']}")

        # capacity status
        if row["capacity"] < people_needed:
            st.error("🔴 Not enough capacity!")
        else:
            st.success("🟢 Sufficient capacity")

        key = f"ai_{i}"

        if st.button("✨ Explain", key=f"btn{i}"):

            # ===== AI CALL =====
            if AI_AVAILABLE:
                try:
                    prompt = f"""
                    Disaster scenario:
                    Location: {location}
                    Resource: {resource_type}
                    People: {people_needed}

                    Explain why {row['name']} is suitable.
                    """

                    response = model.generate_content(prompt)
                    st.session_state[key] = response.text

                except:
                    st.session_state[key] = "⚠️ AI busy, using fallback."

            # ===== FALLBACK =====
            if key not in st.session_state:
                st.session_state[key] = f"""
📊 Smart Analysis

Capacity: {row['capacity']} | Needed: {people_needed}

{'❌ Not sufficient capacity.' if row['capacity'] < people_needed else '✅ Fully capable of handling situation.'}

🚀 Recommendation: Deploy based on urgency.
"""

        # ===== DISPLAY CLEAN (NO BUG) =====
        if key in st.session_state:
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.write(st.session_state[key])   # ✅ FIXED HERE
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ================== CHART ==================
st.subheader(f"📊 Resource Distribution in {location}")

st.bar_chart(filtered.set_index("name")["capacity"])

# ================== TABLE ==================
st.subheader("📋 Available Resource Providers")
st.dataframe(filtered)
