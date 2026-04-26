import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(layout="wide", page_title="AI Disaster Resource Optimizer")

# ----------------------------
# 🎨 GLASS UI STYLING
# ----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0E1117, #1a1f2b);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

/* Glass card */
.card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(10px);
    border-radius:15px;
    padding:15px;
    border: 1px solid rgba(255,255,255,0.2);
    transition: 0.3s;
}

.card:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px rgba(0,201,167,0.5);
}

/* Hero glass */
.hero {
    background: rgba(0, 201, 167, 0.15);
    backdrop-filter: blur(15px);
    border-radius:15px;
    padding:25px;
    border:1px solid rgba(0,201,167,0.4);
    box-shadow: 0px 0px 25px rgba(0,201,167,0.4);
}

h1, h2, h3 {
    color: #00C9A7;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 📊 REALISTIC DATA
# ----------------------------
def get_donors():
    city_profiles = {
        "Bangalore": ["Medical", "Volunteers", "Food"],
        "Mumbai": ["Food", "Shelter"],
        "Delhi": ["Volunteers", "Shelter"],
        "Chennai": ["Medical", "Food"],
        "Hyderabad": ["Food", "Shelter"],
        "Kolkata": ["Medical", "Volunteers"],
        "Pune": ["Food", "Volunteers"],
        "Ahmedabad": ["Shelter", "Food"],
        "Jaipur": ["Shelter"],
        "Lucknow": ["Food"],
    }

    all_types = ["Shelter", "Food", "Blood", "Volunteers", "Medical"]
    donors = []

    for city, strong_types in city_profiles.items():
        for t in strong_types:
            for i in range(2):
                donors.append({
                    "name": f"{city} {t} Hub {i+1}",
                    "type": t,
                    "location": city,
                    "capacity": random.randint(120, 200)
                })

        weak_types = [t for t in all_types if t not in strong_types]
        for t in weak_types:
            donors.append({
                "name": f"{city} {t} Support",
                "type": t,
                "location": city,
                "capacity": random.randint(30, 80)
            })

    return pd.DataFrame(donors)

# ----------------------------
# 🤖 AI EXPLANATION
# ----------------------------
def get_ai_explanation(donor, people_needed):
    return f"""
{donor['name']} can support {donor['capacity']} people.

Requirement is {people_needed}, making it a strong match.

Deploy immediately for best results.
"""

# ----------------------------
# LOAD DATA
# ----------------------------
df = get_donors()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.markdown("## 🎯 Disaster Input Panel")
st.sidebar.markdown("---")

location = st.sidebar.selectbox("Location", sorted(df["location"].unique()))
resource_type = st.sidebar.selectbox(
    "Resource Type", ["Shelter", "Food", "Blood", "Volunteers", "Medical"]
)
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])
people_needed = st.sidebar.slider("People Needed", 10, 200, 50)

# ----------------------------
# FILTERING
# ----------------------------
filtered_df = df[df["type"] == resource_type].copy()

if filtered_df.empty:
    st.warning("⚠️ No exact match found. Showing alternatives.")
    filtered_df = df.copy()

# ----------------------------
# SCORING
# ----------------------------
def calculate_score(row):
    score = 0

    if row["location"] == location:
        score += 50

    score += min(row["capacity"], people_needed) / people_needed * 40

    if urgency == "High":
        score += 10

    return int(score)

with st.spinner("🤖 Analyzing best resources..."):
    time.sleep(0.5)
    filtered_df["score"] = filtered_df.apply(calculate_score, axis=1)

df_sorted = filtered_df.sort_values(by="score", ascending=False)

# ----------------------------
# HEADER
# ----------------------------
st.title("🚨 AI Disaster Resource Optimizer")
st.caption("AI-powered disaster response decision system for real-time resource allocation")

col1, col2, col3 = st.columns(3)
col1.metric("🌆 Cities Covered", len(df["location"].unique()))
col2.metric("🏢 Total Providers", len(df))

# ✅ UPDATED URGENCY DISPLAY
with col3:
    if urgency == "High":
        st.error("🔴 HIGH URGENCY")
    elif urgency == "Medium":
        st.warning("🟡 MEDIUM URGENCY")
    else:
        st.success("🟢 LOW URGENCY")

st.warning("⚠️ Every second matters in disaster response. Choose wisely.")

st.markdown("---")

# ----------------------------
# BEST MATCH
# ----------------------------
best = df_sorted.iloc[0]

st.markdown(f"""
<div class="hero">
<h2>🚀 Best Match: {best['name']}</h2>
<p>Recommended for immediate deployment</p>
</div>
""", unsafe_allow_html=True)

# Decision Summary
st.markdown(f"""
### 🚨 Decision Summary

- 📍 Location: **{location}**
- 📦 Resource Needed: **{resource_type}**
- 👥 People Affected: **{people_needed}**

✅ **Recommended Action:** Deploy **{best['name']}**  
⚡ Capacity Available: **{best['capacity']} people**
""")

# Shortage warning
if best["capacity"] < people_needed:
    shortage = people_needed - best["capacity"]
    st.error(f"🚨 Resource Shortage: {shortage} more people need support!")

st.success(f"✅ Deploy {best['name']} immediately")

# ✅ NEW: SIMULATION BUTTON
if st.button("🚀 Simulate Deployment"):
    with st.spinner("Deploying resources..."):
        time.sleep(1.5)
    st.success(f"✅ {best['name']} successfully deployed!")

# ✅ NEW: STATUS TIMELINE
st.markdown("""
### 📡 Deployment Status

- 🔄 Request Received  
- ⚙️ Processing Resources  
- 🚚 Dispatch Initiated  
- ✅ Deployment Completed  
""")

st.markdown("---")

# ----------------------------
# DEPLOYMENT OPTIONS
# ----------------------------
st.subheader("🏆 Deployment Options")

top_donors = df_sorted.head(3)
cols = st.columns(3)

for i, (_, row) in enumerate(top_donors.iterrows()):
    with cols[i]:
        st.markdown(f"""
        <div class="card">
        <h3>{row['name']}</h3>
        <p>📦 {row['type']}</p>
        <p>📍 {row['location']}</p>
        <p>⭐ Score: {row['score']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(row["score"] / 100)

        if st.button(f"🤖 Explain - {row['name']}"):
            st.info(get_ai_explanation(row, people_needed))

st.markdown("---")

# ----------------------------
# AI INSIGHT
# ----------------------------
st.subheader("🧠 AI Insight")

city_data = df[df["location"] == location]
top_resource = city_data.groupby("type")["capacity"].sum().idxmax()

st.info(f"""
📍 Strongest resource in {location}: {top_resource}

💡 Recommendation: Allocate based on city strengths.
""")

# ----------------------------
# METRIC
# ----------------------------
total_capacity = city_data["capacity"].sum()
st.metric("🏗️ Total Capacity in City", total_capacity)

# ----------------------------
# RESOURCE DISTRIBUTION
# ----------------------------
st.subheader(f"📊 Resource Distribution in {location}")

if city_data.empty:
    st.warning("No data available for this city")
else:
    chart_data = (
        city_data.groupby("type")["capacity"]
        .sum()
        .reset_index()
        .sort_values(by="capacity", ascending=False)
    )

    chart_data = chart_data.set_index("type")

    st.bar_chart(chart_data, use_container_width=True)

# ----------------------------
# TABLE
# ----------------------------
st.subheader("📋 Available Resource Providers")
st.dataframe(df_sorted, use_container_width=True)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("""
---
<center>🚨 AI Disaster Resource Optimizer | Hackathon Project 🚀</center>
""", unsafe_allow_html=True)