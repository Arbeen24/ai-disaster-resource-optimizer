import streamlit as st
import pandas as pd
import random
import time

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
# PAGE
# =========================
st.set_page_config(layout="wide")

# =========================
# CSS (CLEAN GLASS UI)
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

/* Info bar */
.info-bar {
    background: #fde68a;
    color: black;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 15px;
}

/* Best match */
.hero {
    background: rgba(0, 201, 167, 0.2);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.07);
    padding:20px;
    border-radius:12px;
    border:1px solid rgba(255,255,255,0.1);
    transition: 0.3s;
    min-height: 260px;
}

.card:hover {
    transform: translateY(-5px);
    border:1px solid #00C9A7;
}

/* AI box */
.ai-box {
    background: rgba(255,255,255,0.1);
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
<h2>🚀 Best Match: {best['name']}</h2>
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

        if key not in st.session_state:
            st.session_state[key] = ""

        # CARD CONTENT
        st.markdown(f"""
        <div class="card">
        <h3>{row['name']}</h3>
        👥 Capacity: {row['capacity']}
        """, unsafe_allow_html=True)

        # BUTTON INSIDE CARD
        if st.button("✨ Explain", key=f"btn_{i}"):

            if AI_AVAILABLE:
                try:
                    prompt = f"""
                    Resource: {row['name']}
                    Capacity: {row['capacity']}
                    Required: {people_needed}
                    Urgency: {urgency}

                    Give short decision.
                    """
                    res = model.generate_content(prompt)
                    st.session_state[key] = res.text
                except:
                    st.session_state[key] = "⚠️ AI busy, using fallback"

            else:
                st.session_state[key] = "⚠️ AI not available"

        # AI OUTPUT INSIDE CARD
        if st.session_state[key]:
            st.markdown(f"""
            <div class="ai-box">
            🤖 {st.session_state[key]}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# CHART
# =========================
st.subheader("📊 Resource Distribution")

st.bar_chart(df.set_index("name")["capacity"])

# =========================
# TABLE
# =========================
st.subheader("📋 All Resources")
st.dataframe(df)
