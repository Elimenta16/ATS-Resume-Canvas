# 📄 ATS Resume Canvas Studio

An interactive, open-source web application engineered to build, customize, and optimize resumes for Applicant Tracking Systems (ATS). Features real-time job description compatibility analysis powered by Groq API (LLMs), automated ATS-compliant PDF generation with ReportLab, live PDF previewing, and complete JSON data portability.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Groq](https://img.shields.io/badge/AI-Groq%20API-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Key Features

* **🎨 Interactive Canvas Builder:** Intuitive Streamlit UI to edit contact details, professional summary, work experience, key projects, technical skills, languages/certifications, and education in real time.
* **🌐 Multilingual Support (I18n):** Dynamically updates application text and standardizes PDF section headers in **English 🇺🇸**, **Español 🇲🇽**, and **Français 🇫🇷**.
* **⚡ AI Job Match Analysis (Groq API):** Compares your resume (either generated in-app or uploaded as an external PDF/TXT file) against any job description using open-source LLMs (`openai/gpt-oss-120b`). Returns:
  * **ATS Match Score (%)**
  * **Executive Summary & Key Strengths / Areas for Improvement**
  * **Keyword Breakdown** (Detected vs. Missing industry terms)
  * **Actionable Recommendations**
* **📄 ATS-Optimized PDF Export:** Generates clean, single-column, parseable PDFs using ReportLab to ensure full readability by automated HR screeners.
* **👁️ Live PDF Preview:** Integrated PDF viewer (`streamlit_pdf_viewer`) allowing instant visual feedback of layout and typographic adjustments.
* **⚙️ Layout & Typography Control:** Fine-tune margins (pt), base font sizes, and ATS-safe font families (*Helvetica*, *Times-Roman*, *Courier*).
* **💾 Data Backup & Portability:** Export your entire resume data structure into JSON format for safe backup and reuse.

---

## 🛠️ Tech Stack & Architecture

* **Web Framework:** [Streamlit](https://streamlit.io/)
* **AI & Natural Language Processing:** [Groq API](https://groq.com/) (`groq` Python SDK) using `openai/gpt-oss-120b`
* **PDF Generation:** [ReportLab Flowables](https://www.reportlab.com/)
* **PDF Parsing & Viewing:** `pypdf` / `PyPDF2` & `streamlit_pdf_viewer`
* **Data Visualization & Analytics:** Pandas, Plotly Express
* **Language:** Python 3.10+

---

## 🚀 Quick Start

### Prerequisites
* Python 3.10 or higher
* A **Groq API Key** (obtainable from [Groq Console](https://console.groq.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Elimenta16/ats-resume-canvas.git](https://github.com/Elimenta16/ats-resume-canvas.git)
   cd ats-resume-canvas
