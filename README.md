# 📄 ATS Resume Canvas Studio

An interactive, dynamic resume canvas designed to craft, customize, and optimize resumes for **Applicant Tracking Systems (ATS)**. Features real-time job compatibility analysis powered by **Google Gemini AI**, automated ATS-friendly PDF generation, and JSON data backup.

---

## ✨ Key Features

* **🎨 Real-Time Interactive Builder:** Intuitive Streamlit UI to manage contact information, professional summary, work experience, key projects, skills, education, and certifications.
* **🌐 Multilingual Support (i18n):** Generates standardized headers and document templates in **Spanish 🇲🇽**, **English 🇺🇸**, and **French 🇫🇷**.
* **🤖 AI-Powered Job Match Analysis (Gemini 2.5):** Compares your resume (either generated in-app or uploaded as an external PDF/TXT file) against a job description. Provides:
  * ATS Compatibility Score (%).
  * Visual keyword breakdown (Detected vs. Missing).
  * Key strengths, areas for improvement, and actionable recommendations.
* **📄 ATS-Optimized PDF Export:** Generates clean, parseable PDFs using ReportLab to ensure full readability by HR recruitment software.
* **⚙️ Typography & Layout Control:** Fine-tune margins, font sizes, and ATS-friendly font families (`Helvetica`, `Times-Roman`, `Courier`).
* **💾 JSON Backup & Restore:** Export and restore your complete resume data structure anytime.

---

## 🛠️ Built With

* **Language:** Python 3.10+
* **Web Framework:** Streamlit
* **Artificial Intelligence:** `google-genai` SDK (`gemini-2.5-flash` model)
* **Document Generation:** ReportLab
* **Data Visualization:** Plotly Express & Pandas
* **PDF Parsing:** `pypdf`

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/ats-resume-canvas-studio.git](https://github.com/YOUR_USERNAME/ats-resume-canvas-studio.git)
cd ats-resume-canvas-studio
