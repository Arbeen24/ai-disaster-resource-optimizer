import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# ================= CONFIG =================
st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# ================= GEMINI =================
AI_AVAILABLE = False
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    AI_AVAILABLE = True
except:
    pass

def get_ai_response(prompt):
    if not AI_AVAILABLE:
        return {"status": "error"}
    try:
        response = model.generate_content(prompt)
        return {"status": "success", "data": response.text}
    except:
        return {"status": "error"}

# ================= CSS (FIXED FOR LIGHT + DARK) =================
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(0,0,0,0.1);
    transition: 0.3s ease;
    background: rgba(255,255,255,0.7);
    color: black;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .card {
        background: rgba(255,255,255,0.08);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
}

/* Hover */
.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 0 20px rgba(0,255,200,0.3);
}

/* Best card */
.best {
    border: 2px solid #00ffcc;
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", [
    "Bangalore","Mumbai","Chennai","Hyderabad",
    "Delhi","Kolkata","Pune","Ahmedabad"
])

resource_type = st.sidebar.selectbox("Resource Type", ["Shelter","Medical","Food"])
urgency = st.sidebar.selectbox("Urgency", ["Low","Medium","High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# ================= DATA =================
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

# ================= HEADER =================
st.title("🚨 AI Disaster Resource Optimizer")

st.warning("⚠️ Every second matters in disaster response.")

st.success(f"🚀 Best Match: {best['name']}")

# ================= 🔥 AI FEATURE BUTTONS (ADDED BACK) =================
st.markdown("## 🤖 AI Insights")

if st.button("🤖 Why this is Best?"):
    prompt = f"Why is {best['name']} best? Capacity {best['capacity']} Needed {people_needed}"
    result = get_ai_response(prompt)

    if result["status"] == "success":
        st.success(result["data"])
    else:
        st.warning("⚠️ Gemini API issue → fallback used")
        st.info("Selected based on highest capacity and demand match.")

if st.button("🧠 Generate Disaster Plan"):
    prompt = f"Disaster plan for {location}, {people_needed} people, urgency {urgency}"
    result = get_ai_response(prompt)

    if result["status"] == "success":
        st.success(result["data"])
    else:
        st.warning("⚠️ Gemini API issue → fallback used")
        st.info("Deploy resources, prioritize critical zones, monitor continuously.")

if st.button("⚠️ Risk Analysis"):
    prompt = f"Risk if capacity is insufficient. Needed {people_needed}"
    result = get_ai_response(prompt)

    if result["status"] == "success":
        st.error(result["data"])
    else:
        st.warning("⚠️ Gemini API issue → fallback used")
        st.error("High risk due to limited resources.")

# ================= CARDS =================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        key = f"ai_{i}"
        if key not in st.session_state:
            st.session_state[key] = None

        card_class = "card best" if row["name"] == best["name"] else "card"

        st.markdown(f"""
        <div class="{card_class}">
            <h3>{row['name']}</h3>
            <p>👥 Capacity: {row['capacity']}</p>
        </div>
        """, unsafe_allow_html=True)

        if row["capacity"] >= people_needed:
            st.success("🟢 Sufficient Capacity")
        else:
            st.error("🔴 Not Enough Capacity")

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
⚠️ Gemini API issue → fallback used

Capacity: {row['capacity']} | Needed: {people_needed}

{"Sufficient" if row['capacity'] >= people_needed else "Insufficient"}
"""

        if st.session_state[key]:
            st.info(st.session_state[key])

# ================= CHART =================
st.subheader("📊 Resource Distribution")
st.bar_chart(df.set_index("name")["capacity"])

# ================= TABLE =================
st.subheader("📋 Available Resources")
st.dataframe(df)
