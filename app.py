import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# =========================
# GEMINI SETUP
# =========================
AI_AVAILABLE = False
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    AI_AVAILABLE = True
except:
    pass

# =========================
# UNIVERSAL AI HANDLER
# =========================
def get_ai_response(prompt):
    if not AI_AVAILABLE:
        return {"status": "error", "data": "AI not configured"}
    try:
        response = model.generate_content(prompt)
        return {"status": "success", "data": response.text}
    except Exception as e:
        return {"status": "error", "data": str(e)}

# =========================
# UI STYLING
# =========================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.info-bar {
    background: #fde68a;
    color: black;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.hero {
    background: linear-gradient(90deg, #00c9a7, #007cf0);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    font-weight: bold;
}

.card {
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:15px;
    border:1px solid rgba(255,255,255,0.15);
    transition: 0.3s;
    min-height: 260px;
}

.card:hover {
    transform: translateY(-6px);
}

.best-card {
    border:2px solid #00ffcc;
}

.ai-box {
    background: rgba(255,255,255,0.12);
    padding:10px;
    border-radius:10px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", [
    "Bangalore","Mumbai","Chennai","Hyderabad",
    "Delhi","Kolkata","Pune","Ahmedabad","Jaipur","Lucknow"
])

resource_type = st.sidebar.selectbox("Resource Type", ["Shelter","Medical","Food"])
urgency = st.sidebar.selectbox("Urgency", ["Low","Medium","High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# =========================
# DATA
# =========================
data = []
for i in range(1,6):
    data.append({
        "name": f"{location} {resource_type} Hub {i}",
        "capacity": random.randint(60,200)
    })

df = pd.DataFrame(data)
df["score"] = df["capacity"] - people_needed
df = df.sort_values(by="score", ascending=False)

best = df.iloc[0]

# =========================
# HEADER
# =========================
st.title("🚨 AI Disaster Resource Optimizer")

st.markdown('<div class="info-bar">⚠️ Every second matters in disaster response.</div>', unsafe_allow_html=True)

st.markdown(f'<div class="hero">🚀 Best Match: {best["name"]}</div>', unsafe_allow_html=True)

# =========================
# BEST MATCH AI
# =========================
if st.button("🤖 Why this is Best?"):
    prompt = f"Explain why {best['name']} is best. Capacity {best['capacity']}, Needed {people_needed}"
    result = get_ai_response(prompt)

    if result["status"] == "success":
        st.success("🤖 AI Insight")
        st.write(result["data"])
    else:
        st.warning("⚠️ Gemini API issue. Showing fallback.")
        st.info("Selected based on highest capacity and demand match.")

# =========================
# CARDS
# =========================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        key = f"ai_{i}"
        if key not in st.session_state:
            st.session_state[key] = None

        is_best = row["name"] == best["name"]
        card_class = "card best-card" if is_best else "card"

        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

        st.markdown(f"### {row['name']}")
        st.write(f"👥 Capacity: {row['capacity']}")

        if row["capacity"] >= people_needed:
            st.success("🟢 Sufficient")
        else:
            st.error("🔴 Not Enough")

        # ===== EXPLAIN =====
        if st.button("✨ Explain", key=f"btn_{i}"):

            prompt = f"""
            Resource: {row['name']}
            Capacity: {row['capacity']}
            Needed: {people_needed}
            Urgency: {urgency}
            """

            result = get_ai_response(prompt)

            if result["status"] == "success":
                st.session_state[key] = result["data"]
            else:
                st.session_state[key] = f"""
📊 Smart Analysis

Capacity: {row['capacity']} | Needed: {people_needed}

{"🟢 Sufficient capacity." if row['capacity'] >= people_needed else "🔴 Insufficient capacity."}

⚠️ Gemini API issue detected → fallback used
"""

        if st.session_state[key] is not None:
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.write(st.session_state[key])
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# DISASTER PLAN
# =========================
if st.button("🧠 Generate Disaster Plan"):
    prompt = f"Give disaster plan for {location}, {people_needed} people, urgency {urgency}"
    result = get_ai_response(prompt)

    if result["status"] == "success":
        st.success("🚨 AI Plan")
        st.write(result["data"])
    else:
        st.warning("⚠️ Gemini API issue. Showing fallback.")
        st.info("Deploy resources, prioritize critical zones, monitor continuously.")

# =========================
# RISK ANALYSIS
# =========================
if st.button("⚠️ Risk Analysis"):
    prompt = f"Risk if capacity is low. Needed {people_needed}"
    result = get_ai_response(prompt)

    if result["status"] == "success":
        st.error(result["data"])
    else:
        st.warning("⚠️ Gemini API issue. Showing fallback.")
        st.error("High risk due to insufficient capacity.")

# =========================
# CHART
# =========================
st.subheader("📊 Resource Distribution")
st.bar_chart(df.set_index("name")["capacity"])

# =========================
# TABLE
# =========================
st.subheader("📋 Available Resource Providers")
st.dataframe(df)
