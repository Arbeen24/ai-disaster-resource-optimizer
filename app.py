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

# ================= CSS FIX =================
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(0,0,0,0.15);
    transition: 0.3s ease;
    background: rgba(255,255,255,0.85);
    color: #111111 !important;
}

@media (prefers-color-scheme: dark) {
    .card {
        background: rgba(255,255,255,0.08);
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2);
    }
}

.card h3, .card p {
    color: inherit !important;
}

.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 0 25px rgba(0,255,200,0.35);
}

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

# ✅ ADDED VOLUNTEERS HERE
resource_type = st.sidebar.selectbox("Resource Type", ["Shelter","Medical","Food","Volunteers"])

urgency = st.sidebar.selectbox("Urgency", ["Low","Medium","High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# ================= DATA =================
data = []
for i in range(1,6):
    data.append({
        "name": f"{location} {resource_type} Hub {i}",
        "capacity": random.randint(60,200),
        "volunteers": random.randint(20,150)   # ✅ NEW FIELD
    })

df = pd.DataFrame(data)
df["score"] = df["capacity"] - people_needed
df = df.sort_values(by="score", ascending=False)

best = df.iloc[0]

# ================= HEADER =================
st.title("🚨 AI Disaster Resource Optimizer")
st.warning("⚠️ Every second matters in disaster response.")
st.success(f"🚀 Best Match: {best['name']}")

# ================= AI BUTTONS =================
st.subheader("🤖 AI Insights")

if st.button("🤖 Why this is Best?"):
    result = get_ai_response(f"Why is {best['name']} best for {people_needed} people?")
    if result["status"] == "success":
        st.success(result["data"])
    else:
        st.warning("⚠️ Gemini API issue → showing fallback")
        st.info("Selected based on highest capacity and demand match.")

if st.button("🧠 Generate Disaster Plan"):
    result = get_ai_response(f"Disaster plan for {location} for {people_needed} people.")
    if result["status"] == "success":
        st.success(result["data"])
    else:
        st.warning("⚠️ Gemini API issue → showing fallback")
        st.info("Deploy resources, prioritize critical zones, monitor continuously.")

if st.button("⚠️ Risk Analysis"):
    result = get_ai_response(f"Risk if capacity is insufficient for {people_needed}")
    if result["status"] == "success":
        st.error(result["data"])
    else:
        st.warning("⚠️ Gemini API issue → showing fallback")
        st.error("High risk due to insufficient resources.")

# ================= CARDS =================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        key = f"explain_{i}"
        if key not in st.session_state:
            st.session_state[key] = None

        card_class = "card best" if row["name"] == best["name"] else "card"

        st.markdown(f"""
        <div class="{card_class}">
            <h3>{row['name']}</h3>
            <p>👥 Capacity: {row['capacity']}</p>
            <p>🧑‍🚒 Volunteers: {row['volunteers']}</p>   <!-- ✅ ADDED -->
        </div>
        """, unsafe_allow_html=True)

        # Capacity status
        if row["capacity"] >= people_needed:
            st.success("🟢 Sufficient Capacity")
        else:
            st.error("🔴 Not Enough Capacity")

        # Volunteers status (NEW)
        if row["volunteers"] >= people_needed * 0.5:
            st.success("🧑‍🚒 Enough Volunteers")
        else:
            st.warning("⚠️ Limited Volunteers")

        # Explain button
        if st.button("✨ Explain", key=f"btn_{i}"):

            result = get_ai_response(
                f"Explain why {row['name']} is suitable. Capacity {row['capacity']}, volunteers {row['volunteers']}, needed {people_needed}"
            )

            if result["status"] == "success":
                st.session_state[key] = result["data"]
            else:
                st.session_state[key] = f"""
⚠️ Gemini API quota exceeded / unavailable

Capacity: {row['capacity']}
Volunteers: {row['volunteers']}
Needed: {people_needed}

{"✔️ Sufficient capacity" if row["capacity"] >= people_needed else "❌ Not sufficient"}
"""

        if st.session_state[key]:
            st.info(st.session_state[key])

# ================= CHART =================
st.subheader("📊 Resource Distribution")
st.bar_chart(df.set_index("name")[["capacity","volunteers"]])  # ✅ UPDATED

# ================= TABLE =================
st.subheader("📋 Available Resource Providers")
st.dataframe(df)
