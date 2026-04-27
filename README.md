# 🌍 AI Disaster Resource Optimizer

🏆 **Hackathon Project | AI-Powered Disaster Management**

🔗 **Live App:**
https://ai-disaster-resource-optimizer-cuem4vunqmwgwxqbhjjlse.streamlit.app/

---

## 📌 Problem Statement

During disaster situations, efficient allocation of critical resources such as shelters, medical aid, food, and volunteers is extremely challenging. Delays, poor prioritization, and lack of real-time decision support often lead to mismanagement and increased risk to human lives.

There is a strong need for an **intelligent system** that can:

* Analyze demand vs availability
* Prioritize urgent needs
* Recommend optimal resource allocation instantly

---

## 💡 Solution

**AI Disaster Resource Optimizer** is a smart decision-support system designed to:

* Match available resources with disaster needs
* Rank options using priority scoring
* Provide quick and effective deployment recommendations

The system ensures:
⚡ Faster decisions
🎯 Better prioritization
📊 Data-driven allocation

---

## 🚀 Key Features

* 🧠 **Smart Resource Matching**
  Automatically identifies the best-fit shelters/resources based on demand

* 🏷️ **Priority-Based Allocation System**
  Dynamic scoring using:

  * Capacity
  * Volunteers
  * Urgency level

* 📊 **Live Resource Visualization**
  Interactive charts for better decision understanding

* 🧑‍🚒 **Multi-Resource Support**
  Supports:

  * Shelter
  * Medical
  * Food
  * Volunteers

* 🤖 **AI Explainability with Fallback**

  * Uses Gemini API when available
  * Falls back to intelligent rule-based explanations when API fails

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **Backend Logic:** Python
* **Data Handling:** Pandas
* **AI Integration:** Google Gemini API (with fallback system)

---

## 🤖 AI Integration

This project integrates **Google Gemini API** to enhance decision-making.

### ✅ What AI does:

* Explains why a resource is selected
* Provides smart deployment suggestions
* Assists in disaster planning insights

### ⚠️ Limitation:

Due to API quota or access restrictions, AI responses may sometimes be unavailable.

### 🔁 Smart Fallback System:

To ensure reliability:

* A **rule-based intelligent fallback system** is implemented
* It continues to provide:

  * Capacity analysis
  * Resource suitability
  * Deployment recommendations

👉 This ensures the app **never breaks**, even if AI is unavailable.

---

## ▶️ How to Run Locally

```bash
# Clone the repository
git clone <your-repo-link>

# Navigate into the project
cd <your-project-folder>

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📈 Future Enhancements

* 🔥 Full Gemini AI integration (no quota limits)
* 🗺️ Live map-based resource tracking
* 📡 Real-time alerts & notifications
* 📱 Mobile-friendly version
* 📊 Predictive disaster demand analysis

---

## 👤 Author

**Arbeen Arif**

---

## 🌟 Project Vision

To build a **scalable AI-powered disaster management system** that enables authorities and organizations to make **faster, smarter, and life-saving decisions** during critical situations.
