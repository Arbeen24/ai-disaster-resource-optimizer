import streamlit as st
import pandas as pd
import random
import time

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
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.glass {
    background: rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.15);
    transition: 0.3s;
}
.glass:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 0 25px rgba(0,255,255,0.3);
}
.badge {
    padding: 5px 10px;
    border-radius: 10px;
    font-size: 12px;
}
.high { background: #ff4d4d; }
.medium { background: #ffa500; }
.low { background: #00cc66; }
</style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", [
    "Bangalore", "Mumbai", "Chennai", "Hyderabad",
    "Delhi", "Kolkata", "Pune", "Ahmedabad",
    "Jaipur", "Lucknow"
])

resource_type = st.sidebar.selectbox("Resource Type", ["Shelter", "Medical", "Food"])
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

st.sidebar.markdown("### 🌍 Coverage")
st.sidebar.success("10 Cities Supported")

# ==============================
# SMART DATA
# ==============================
city_base_capacity = {
    "Bangalore": 150,
    "Mumbai": 170,
    "Chennai": 130,
    "Hyderabad": 140,
    "Delhi": 180,
    "Kolkata": 120,
    "Pune": 135,
    "Ahmedabad": 125,
    "Jaipur": 110,
    "Lucknow": 115
}

base = city_base_capacity[location]

data = []
for i in range(1, 7):
    data.append({
        "name": f"{location} {resource_type} Hub {i}",
        "location": location,
        "capacity": random.randint(base - 40, base + 40)
    })

df = pd.DataFrame(data)

# ==============================
# SCORING
# ==============================
def calculate_score(row):
    score = row["capacity"]

    if urgency == "High":
        score += 40
    elif urgency == "Medium":
        score += 20

    if row["capacity"] >= people_needed:
        score += 50
    else:
        score -= 30

    return score

df["score"] = df.apply(calculate_score, axis=1)
df = df.sort_values(by="score", ascending=False)

# ==============================
# HEADER
# ==============================
st.title("🚨 AI Disaster Resource Optimizer")
st.warning("⚠️ Every second matters in disaster response. Choose wisely.")

best = df.iloc[0]
st.success(f"🚀 Best Match: {best['name']}")

# ==============================
# FUNCTIONS
# ==============================
def get_priority(capacity):
    if capacity >= people_needed:
        return "HIGH", "high"
    elif capacity >= people_needed * 0.7:
        return "MEDIUM", "medium"
    else:
        return "LOW", "low"

def type_writer(text):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(typed)
        time.sleep(0.01)

# ==============================
# CARDS
# ==============================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        level, css_class = get_priority(row["capacity"])
        status = "🟢 Sufficient" if row["capacity"] >= people_needed else "🔴 Not enough"

        st.markdown(f"""
        <div class="glass">
            <h3>{row['name']}</h3>
            📍 {row['location']} <br>
            👥 Capacity: {row['capacity']} <br><br>
            <span class="badge {css_class}">{level} PRIORITY</span><br><br>
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
                    Disaster scenario:
                    Location: {location}
                    Resource: {row['name']}
                    Capacity: {row['capacity']}
                    People needed: {people_needed}
                    Urgency: {urgency}

                    Give a short smart explanation.
                    """

                    response = model.generate_content(prompt)
                    st.session_state[key] = response.text

                except:
                    st.session_state[key] = f"""
⚠️ AI busy (quota)
📊 Capacity: {row['capacity']}
✅ Recommended based on logic
"""

            else:
                st.session_state[key] = f"""
⚠️ AI not available
📊 Capacity: {row['capacity']}
✅ Logic-based suggestion
"""

        if st.session_state[key]:
            st.markdown("🤖 **AI Explanation:**")
            type_writer(st.session_state[key])

# ==============================
# CHART
# ==============================
st.subheader(f"📊 Resource Distribution in {location}")
chart_data = df.set_index("name")["capacity"]
st.bar_chart(chart_data)

# ==============================
# TABLE
# ==============================
st.subheader("📋 Available Resource Providers")
st.dataframe(df)
