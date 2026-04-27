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

# ================= SIDEBAR =================
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", [
    "Bangalore","Mumbai","Chennai","Hyderabad",
    "Delhi","Kolkata","Pune","Ahmedabad"
])

resource_type = st.sidebar.selectbox(
    "Resource Type",
    ["Shelter","Medical","Food","Volunteers"]
)

urgency = st.sidebar.selectbox("Urgency", ["Low","Medium","High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# ================= DATA =================
data = []
for i in range(1,6):

    capacity = random.randint(60,200)
    volunteers = random.randint(20,150)

    # Priority logic
    urgency_bonus = 50 if urgency == "High" else 20 if urgency == "Medium" else 0
    priority = capacity + volunteers + urgency_bonus

    data.append({
        "name": f"{location} {resource_type} Hub {i}",
        "capacity": capacity,
        "volunteers": volunteers,
        "priority": priority
    })

df = pd.DataFrame(data)
df["score"] = df["priority"] - people_needed
df = df.sort_values(by="score", ascending=False)

best = df.iloc[0]

# ================= HEADER =================
st.title("🚨 AI Disaster Resource Optimizer")
st.warning("⚠️ Every second matters in disaster response.")
st.success(f"🚀 Best Match: {best['name']}")

# ================= AI BUTTONS =================
st.subheader("🤖 AI Insights")

if st.button("🤖 Why this is Best?"):
    result = get_ai_response(
        f"Why is {best['name']} best? Capacity {best['capacity']}, Volunteers {best['volunteers']}"
    )
    if result["status"] == "success":
        st.success(result["data"])
    else:
        st.warning("⚠️ AI unavailable → fallback used")
        st.info("Selected based on capacity, volunteers, and urgency.")

# ================= CARDS =================
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(df.head(3).iterrows()):
    with cols[i]:

        key = f"explain_{i}"
        if key not in st.session_state:
            st.session_state[key] = None

        border = "#00ffcc" if row["name"] == best["name"] else "rgba(0,0,0,0.2)"

        # Priority Badge Color
        if row["priority"] > 300:
            badge_color = "#00ffcc"
            label = "HIGH PRIORITY"
        elif row["priority"] > 200:
            badge_color = "#ffaa00"
            label = "MEDIUM"
        else:
            badge_color = "#999999"
            label = "LOW"

        # CARD
        st.markdown(f"""
        <div style="
            padding:20px;
            border-radius:18px;
            border:2px solid {border};
            background:rgba(255,255,255,0.6);
            backdrop-filter:blur(10px);
        ">
            <div style="
                display:inline-block;
                padding:5px 10px;
                border-radius:10px;
                background:{badge_color};
                color:black;
                font-size:12px;
                margin-bottom:10px;
            ">
                {label}
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### {row['name']}")
        st.write(f"👥 Capacity: {row['capacity']}")
        st.write(f"🧑‍🚒 Volunteers: {row['volunteers']}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Status
        if row["capacity"] >= people_needed:
            st.success("🟢 Sufficient Capacity")
        else:
            st.error("🔴 Not Enough Capacity")

        if row["volunteers"] >= people_needed * 0.5:
            st.success("🧑‍🚒 Enough Volunteers")
        else:
            st.warning("⚠️ Limited Volunteers")

        # Explain
        if st.button("✨ Explain", key=f"btn_{i}"):

            result = get_ai_response(
                f"""
                Resource: {row['name']}
                Capacity: {row['capacity']}
                Volunteers: {row['volunteers']}
                Needed: {people_needed}
                Urgency: {urgency}
                """
            )

            if result["status"] == "success":
                st.session_state[key] = result["data"]
            else:
                st.session_state[key] = f"""
⚠️ Gemini API unavailable

Capacity: {row['capacity']}
Volunteers: {row['volunteers']}
Needed: {people_needed}

{"✔️ Enough resources" if row["capacity"] >= people_needed else "❌ Limited capacity"}
"""

        if st.session_state[key] is not None:
            st.info(st.session_state[key])

# ================= CHART =================
st.subheader("📊 Resource Distribution")
st.bar_chart(df.set_index("name")[["capacity","volunteers"]])

# ================= TABLE =================
st.subheader("📋 Available Resources")
st.dataframe(df)

# ================= FOOTER =================
st.markdown("---")
st.markdown(
    "<center>🚀 Built with AI for Disaster Management | Streamlit + Gemini</center>",
    unsafe_allow_html=True
)
