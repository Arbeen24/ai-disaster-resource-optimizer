import streamlit as st
import pandas as pd
import random
import time
import google.generativeai as genai
import os

# ----------------------------
# 🔑 CONFIGURE GEMINI (SECURE)
# ----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# ----------------------------
# 🎨 UI STYLING
# ----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0E1117, #1a1f2b);
    color: white;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(10px);
    border-radius:15px;
    padding:15px;
    border: 1px solid rgba(255,255,255,0.2);
}
.hero {
    background: rgba(0, 201, 167, 0.15);
    backdrop-filter: blur(15px);
    border-radius:15px;
    padding:25px;
}
h1, h2, h3 {
    color: #00C9A7;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 📊 DATA
# ----------------------------
def get_donors():
    city_profiles = {
        "Bangalore": ["Medical", "Volunteers", "Food"],
        "Mumbai": ["Food", "Shelter"],
        "Delhi": ["Volunteers", "Shelter"],
        "Chennai": ["Medical", "Food"],
        "Hyderabad": ["Food", "Shelter"],
        "Kolkata": ["Medical", "Volunteers"],
        "Pune": ["Food", "Volunteers"],
        "Ahmedabad": ["Shelter", "Food"],
        "Jaipur": ["Shelter"],
        "Lucknow": ["Food"],
    }

    all_types = ["Shelter", "Food", "Blood", "Volunteers", "Medical"]
    donors = []

    for city, strong_types in city_profiles.items():
        for t in strong_types:
            for i in range(2):
                donors.append({
                    "name": f"{city} {t} Hub {i+1}",
                    "type": t,
                    "location": city,
                    "capacity": random.randint(120, 200)
                })

        weak_types = [t for t in all_types if t not in strong_types]
        for t in weak_types:
            donors.append({
                "name": f"{city} {t} Support",
                "type": t,
                "location": city,
                "capacity": random.randint(30, 80)
            })

    return pd.DataFrame(donors)

# ----------------------------
# 🤖 AI (CACHED + FALLBACK)
# ----------------------------
@st.cache_data(show_spinner=False)
def get_ai_explanation_cached(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None


def get_ai_explanation(donor, people_needed):
    prompt = f"""
    You are an intelligent disaster response AI.

    Resource: {donor['name']}
    Type: {donor['type']}
    City: {donor['location']}
    Capacity: {donor['capacity']}
    Demand: {people_needed}

    Give:
    - Suitability
    - Risk
    - Final recommendation
    """

    result = get_ai_explanation_cached(prompt)

    if result:
        return result
    else:
        return f"""
⚠️ AI temporarily unavailable (quota limit)

📊 Smart Suggestion:
{donor['name']} can support {donor['capacity']} people.

✅ Recommended to deploy based on capacity and location.
"""

# ----------------------------
# LOAD DATA
# ----------------------------
df = get_donors()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.markdown("## 🎯 Disaster Input Panel")
location = st.sidebar.selectbox("Location", sorted(df["location"].unique()))
resource_type = st.sidebar.selectbox(
    "Resource Type", ["Shelter", "Food", "Blood", "Volunteers", "Medical"]
)
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# ----------------------------
# FILTER + SCORE
# ----------------------------
filtered_df = df[df["type"] == resource_type].copy()

def calculate_score(row):
    score = 0
    if row["location"] == location:
        score += 50
    score += min(row["capacity"], people_needed) / people_needed * 40
    if urgency == "High":
        score += 10
    return int(score)

filtered_df["score"] = filtered_df.apply(calculate_score, axis=1)
df_sorted = filtered_df.sort_values(by="score", ascending=False)

# ----------------------------
# HEADER
# ----------------------------
st.title("🚨 AI Disaster Resource Optimizer")

best = df_sorted.iloc[0]

st.markdown(f"""
<div class="hero">
<h2>🚀 Best Match: {best['name']}</h2>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
### 🚨 Decision Summary
- 📍 {location}
- 📦 {resource_type}
- 👥 {people_needed}
""")

# ----------------------------
# OPTIONS
# ----------------------------
st.subheader("🏆 Deployment Options")

for _, row in df_sorted.head(3).iterrows():
    st.write(f"### {row['name']}")
    st.progress(row["score"] / 100)

    if st.button(f"🤖 Explain - {row['name']}"):
        st.info(get_ai_explanation(row, people_needed))

# ----------------------------
# TABLE
# ----------------------------
st.dataframe(df_sorted)
