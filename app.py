import streamlit as st
import pandas as pd
import random

# =========================
# GEMINI SETUP
# =========================
AI_AVAILABLE = False
try:
    import google.generativeai as genai
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        AI_AVAILABLE = True
except:
    pass

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# =========================
# CSS
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
    margin-bottom: 25px;
    color: white;
    font-weight: bold;
}

.card {
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:15px;
    border:1px solid rgba(255,255,255,0.15);
    transition: 0.3s;
    min-height: 270px;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 25px rgba(0,255,200,0.4);
}

.best-card {
    border:2px solid #00ffcc;
}

.ai-box {
    background: rgba(255,255,255,0.12);
    padding:12px;
    border-radius:10px;
    margin-top:12px;
}

.good {color:#00ff99;}
.bad {color:#ff5c5c;}
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

st.sidebar.success("🌍 10 Cities Supported")

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

# =========================
# SCORING
# =========================
df["score"] = df["capacity"] - people_needed
df = df.sort_values(by="score", ascending=False)
best = df.iloc[0]

# =========================
# HEADER
# =========================
st.title("🚨 AI Disaster Resource Optimizer")

st.markdown("""
<div class="info-bar">
⚠️ Every second matters in disaster response. Choose wisely.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
🚀 Best Match: {best['name']}
</div>
""", unsafe_allow_html=True)

# =========================
# CARDS
# =========================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        key = f"ai_{i}"

        # ✅ FIX: initialize properly
        if key not in st.session_state:
            st.session_state[key] = None

        is_best = row["name"] == best["name"]
        card_class = "card best-card" if is_best else "card"

        status = (
            "<span class='good'>🟢 Sufficient Capacity</span>"
            if row["capacity"] >= people_needed
            else "<span class='bad'>🔴 Not Enough Capacity</span>"
        )

        st.markdown(f"""
        <div class="{card_class}">
        <h3>{row['name']}</h3>
        👥 Capacity: {row['capacity']} <br><br>
        {status}
        """, unsafe_allow_html=True)

        # =========================
        # BUTTON
        # =========================
        if st.button("✨ Explain", key=f"btn_{i}"):

            # ✅ RESET FIRST (fix bug)
            st.session_state[key] = None

            if AI_AVAILABLE:
                try:
                    with st.spinner("🤖 AI analyzing..."):
                        prompt = f"""
                        Resource: {row['name']}
                        Capacity: {row['capacity']}
                        Required: {people_needed}
                        Urgency: {urgency}

                        Explain briefly.
                        """
                        res = model.generate_content(prompt)
                        st.session_state[key] = res.text

                except:
                    st.session_state[key] = f"""
📊 Smart Analysis

Capacity: {row['capacity']} | Needed: {people_needed}

{"🟢 Sufficient capacity to handle the situation." if row['capacity'] >= people_needed else "🔴 Insufficient capacity — requires backup hubs."}

🚀 Recommendation: {"Deploy immediately." if urgency=="High" else "Deploy as needed."}
"""

            else:
                st.session_state[key] = f"""
🤖 AI Insight (Fallback Mode)

This hub can support {row['capacity']} people.

{"🟢 Fully meets the requirement." if row['capacity'] >= people_needed else "🔴 Does not fully meet demand — consider additional hubs."}

⚡ Urgency Level: {urgency}
"""

        # =========================
        # DISPLAY (FIXED)
        # =========================
        if st.session_state[key] is not None:
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.write(st.session_state[key])  # ✅ NO HTML BUG
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

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
