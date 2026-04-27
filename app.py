import streamlit as st
import pandas as pd
import random

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# -------------------------
# SAMPLE DATA
# -------------------------
data = []
cities = ["Bangalore", "Mumbai", "Chennai", "Hyderabad"]

for city in cities:
    for i in range(1, 4):
        data.append({
            "name": f"{city} Shelter Hub {i}",
            "type": "Shelter",
            "location": city,
            "capacity": random.randint(50, 180)
        })

df = pd.DataFrame(data)

# -------------------------
# SIDEBAR INPUTS
# -------------------------
st.sidebar.title("🎯 Disaster Input Panel")

location = st.sidebar.selectbox("Location", df["location"].unique())

resource_type = st.sidebar.selectbox(
    "Resource Type",
    ["Shelter", "Medical", "Food", "Rescue"]
)

urgency = st.sidebar.selectbox(
    "Urgency",
    ["Low", "Medium", "High"]
)

people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# -------------------------
# FILTER + SMART SCORING
# -------------------------
filtered = df[df["location"] == location].copy()

urgency_weight = {"Low": 1, "Medium": 2, "High": 3}

filtered["score"] = (
    filtered["capacity"]
    - people_needed
    + urgency_weight[urgency] * 20
)

sorted_df = filtered.sort_values(by="score", ascending=False)
best = sorted_df.iloc[0]

# -------------------------
# HEADER
# -------------------------
st.title("🚨 AI Disaster Resource Optimizer")

st.warning("Every second matters in disaster response. Choose wisely.")

# -------------------------
# BEST MATCH
# -------------------------
st.markdown(f"""
<div style="
background: linear-gradient(135deg,#00c6ff,#0072ff);
padding:20px;
border-radius:15px;
color:white;
font-size:24px;
font-weight:bold;">
🚀 Best Match: {best['name']}
</div>
""", unsafe_allow_html=True)

# -------------------------
# DEPLOYMENT CARDS
# -------------------------
st.subheader("🏆 Deployment Options")

cols = st.columns(3)

for i, (_, row) in enumerate(sorted_df.head(3).iterrows()):
    with cols[i]:

        # -------------------------
        # CAPACITY WARNING LOGIC
        # -------------------------
        if people_needed > row["capacity"]:
            status = "🔴 Cannot handle required people"
            color = "#ff4d4d"
        elif row["capacity"] - people_needed < 20:
            status = "🟡 Limited capacity"
            color = "#ffc107"
        else:
            status = "🟢 Sufficient capacity"
            color = "#28a745"

        st.markdown(f"""
        <div style="
        backdrop-filter: blur(10px);
        background: rgba(255,255,255,0.05);
        padding:20px;
        border-radius:15px;
        border:1px solid rgba(255,255,255,0.1);
        color:white;
        ">
        <h3>{row['name']}</h3>
        <p>📍 {row['location']}</p>
        <p>👥 Capacity: {row['capacity']}</p>
        <p style="color:{color}; font-weight:bold;">{status}</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# RESOURCE DISTRIBUTION CHART
# -------------------------
st.subheader(f"📊 Resource Distribution in {location}")

chart_df = sorted_df.head(3)

st.bar_chart(chart_df.set_index("name")["capacity"])

# -------------------------
# TABLE
# -------------------------
st.subheader("📋 Available Resource Providers")

st.dataframe(sorted_df)
