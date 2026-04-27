import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# ------------------ CONFIG ------------------
st.set_page_config(page_title="AI Disaster Resource Optimizer", layout="wide")

# Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# ------------------ DATA ------------------
cities = ["Bangalore", "Mumbai", "Chennai", "Hyderabad", "Delhi"]

resources = []

for city in cities:
    for i in range(1, 6):
        resources.append({
            "name": f"{city} Medical Hub {i}",
            "type": "Medical",
            "location": city,
            "capacity": random.randint(80, 200)
        })

        resources.append({
            "name": f"{city} Shelter Hub {i}",
            "type": "Shelter",
            "location": city,
            "capacity": random.randint(60, 180)
        })

df = pd.DataFrame(resources)

# ------------------ SIDEBAR ------------------
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", cities)
resource_type = st.sidebar.selectbox("Resource Type", ["Medical", "Shelter"])
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

st.sidebar.markdown("🌍 **10 Cities Supported**")

# ------------------ FILTER ------------------
filtered = df[(df["location"] == location) & (df["type"] == resource_type)]

# scoring logic
filtered["score"] = filtered["capacity"] - people_needed
filtered = filtered.sort_values(by="score", ascending=False)

best = filtered.iloc[0]

# ------------------ HEADER ------------------
st.title("🚨 AI Disaster Resource Optimizer")

st.warning("⚠️ Every second matters in disaster response. Choose wisely.")

st.success(f"🚀 Best Match: {best['name']}")

st.subheader("🏆 Deployment Options")

# ------------------ GLASS CARD STYLE ------------------
st.markdown("""
<style>
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

# ------------------ CARDS ------------------
cols = st.columns(3)

for i, row in enumerate(filtered.head(3).itertuples()):
    with cols[i]:

        st.markdown(f"""
        <div class="card">
        <h3>{row.name}</h3>
        📍 {row.location}<br>
        👥 Capacity: {row.capacity}<br>
        """, unsafe_allow_html=True)

        if row.capacity >= people_needed:
            st.success("🟢 Sufficient Capacity")
        else:
            st.error("🔴 Insufficient Capacity")

        st.markdown("</div>", unsafe_allow_html=True)

        # ----------- EXPLAIN BUTTON (FIXED) -----------
        if st.button("✨ Explain", key=f"explain_{i}"):

            prompt = f"""
            You are an AI disaster management assistant.

            Location: {row.location}
            Resource: {row.name}
            Capacity: {row.capacity}
            People Needed: {people_needed}
            Urgency: {urgency}

            Explain briefly whether this resource is suitable.
            """

            if AI_AVAILABLE:
                try:
                    response = model.generate_content(prompt)
                    st.success("🤖 AI Explanation")
                    st.write(response.text)

                except:
                    st.warning("⚠️ Gemini API quota exceeded or error. Showing fallback explanation.")

                    # fallback
                    if row.capacity >= people_needed:
                        st.info(f"""
📊 Smart Analysis  
Capacity: {row.capacity} | Needed: {people_needed}

🟢 This resource is sufficient.

🚀 Recommendation: Deploy.
""")
                    else:
                        st.error(f"""
📊 Smart Analysis  
Capacity: {row.capacity} | Needed: {people_needed}

🔴 Not sufficient.

⚠️ Recommendation: Use additional hubs.
""")

            else:
                st.warning("⚠️ AI not configured. Showing fallback.")

                if row.capacity >= people_needed:
                    st.info("🟢 Enough capacity. Safe to deploy.")
                else:
                    st.error("🔴 Not enough capacity.")

# ------------------ CHART ------------------
st.subheader("📊 Resource Distribution")

chart_data = filtered.head(5)

st.bar_chart(chart_data.set_index("name")["capacity"])

# ------------------ TABLE ------------------
st.subheader("📋 Available Resource Providers")
st.dataframe(filtered.reset_index(drop=True))
