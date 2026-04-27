import streamlit as st
import pandas as pd
import random

# ==============================
# GEMINI SETUP
# ==============================
AI_AVAILABLE = False

try:
    import google.generativeai as genai

    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# ==============================
# GLASS UI
# ==============================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.glass {
    background: rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
}
.card:hover {
    transform: scale(1.03);
    transition: 0.3s;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR INPUT
# ==============================
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", ["Bangalore", "Mumbai", "Chennai"])
resource_type = st.sidebar.selectbox("Resource Type", ["Shelter", "Medical", "Food"])
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# ==============================
# DUMMY DATA
# ==============================
data = []
for i in range(1, 6):
    data.append({
        "name": f"{location} {resource_type} Hub {i}",
        "location": location,
        "capacity": random.randint(60, 200)
    })

df = pd.DataFrame(data)

# ==============================
# SCORING LOGIC
# ==============================
def calculate_score(row):
    score = row["capacity"]

    if urgency == "High":
        score += 30
    elif urgency == "Medium":
        score += 15

    if row["capacity"] >= people_needed:
        score += 40
    else:
        score -= 20

    return score

df["score"] = df.apply(calculate_score, axis=1)
df = df.sort_values(by="score", ascending=False)

# ==============================
# HEADER
# ==============================
st.title("🚨 AI Disaster Resource Optimizer")

st.warning("Every second matters in disaster response. Choose wisely.")

best = df.iloc[0]
st.success(f"🚀 Best Match: {best['name']}")

# ==============================
# CARDS
# ==============================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        status = "🟢 Sufficient capacity" if row["capacity"] >= people_needed else "🔴 Not enough capacity"

        st.markdown(f"""
        <div class="glass card">
            <h3>{row['name']}</h3>
            📍 {row['location']} <br>
            👥 Capacity: {row['capacity']} <br><br>
            <b>{status}</b>
        </div>
        """, unsafe_allow_html=True)

        key = f"ai_{i}"

        if key not in st.session_state:
            st.session_state[key] = ""

        if st.button(f"✨ Explain", key=f"btn_{i}"):

            if AI_AVAILABLE:
                try:
                    prompt = f"""
                    Disaster resource allocation:
                    Location: {location}
                    Resource: {row['name']}
                    Capacity: {row['capacity']}
                    People needed: {people_needed}
                    Urgency: {urgency}

                    Give a short decision explanation.
                    """

                    response = model.generate_content(prompt)
                    st.session_state[key] = response.text

                except:
                    st.session_state[key] = f"""
⚠️ AI busy (quota)
📊 Capacity: {row['capacity']}
✅ Recommended based on availability
"""

            else:
                st.session_state[key] = f"""
⚠️ AI not configured
📊 Capacity: {row['capacity']}
✅ Suitable based on logic
"""

        if st.session_state[key]:
            st.info(st.session_state[key])

# ==============================
# CHART
# ==============================
st.subheader(f"📊 Resource Distribution in {location}")

chart_data = df.head(5).set_index("name")["capacity"]
st.bar_chart(chart_data)

# ==============================
# TABLE
# ==============================
st.subheader("📋 Available Resource Providers")
st.dataframe(df)
