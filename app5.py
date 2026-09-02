import base64
import html
import importlib
import io
import json
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    Groq = importlib.import_module("groq").Groq
except ImportError as exc:
    Groq = None
    GROQ_IMPORT_ERROR = exc

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


# =========================================================
# MAIN CONFIGURATION
# =========================================================

MODEL_NAME = "openai/gpt-oss-120b"


# =========================================================
# PDF READER
# =========================================================

def get_pdf_reader(file_object):
    """Gets PDF reader using pypdf or PyPDF2."""
    for package_name in ("pypdf", "PyPDF2"):
        try:
            pdf_module = importlib.import_module(package_name)
            return pdf_module.PdfReader(file_object)
        except ImportError:
            continue
    raise ImportError(
        "PDF reader not found. "
        "Install the dependency with: pip install pypdf"
    )


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

st.set_page_config(
    layout="wide",
    page_title="ATS Resume Canvas Studio",
    page_icon="📄",
)


# =========================================================
# GROQ API KEY (SECURE INJECTION VIA ST.SECRETS)
# =========================================================

groq_api_key = st.secrets.get("GROQ_API_KEY", "")


# =========================================================
# LANGUAGES / I18N
# =========================================================

I18N = {
    "English 🇺🇸": {
        "sec_contact": "📌 Contact Information",
        "sec_profile": "📝 Professional Summary",
        "sec_exp": "💼 Work Experience",
        "sec_proj": "🔬 Key Projects",
        "sec_skills": "🎯 Skills & Competencies",
        "sec_edu": "🎓 Education",
        "sec_lang": "🌐 Languages & Certifications",
        "pdf_profile": "PROFESSIONAL SUMMARY",
        "pdf_exp": "WORK EXPERIENCE",
        "pdf_proj": "KEY PROJECTS",
        "pdf_skills": "SKILLS & COMPETENCIES",
        "pdf_edu": "EDUCATION",
        "pdf_lang": "LANGUAGES & CERTIFICATIONS",
        "btn_dl_pdf": "📥 Download ATS PDF",
        "btn_dl_json": "💾 Backup Data (.JSON)",
    },
    "Español 🇲🇽": {
        "sec_contact": "📌 Contacto",
        "sec_profile": "📝 Perfil Profesional",
        "sec_exp": "💼 Experiencia Laboral",
        "sec_proj": "🔬 Proyectos Destacados",
        "sec_skills": "🎯 Habilidades & Competencias",
        "sec_edu": "🎓 Educación",
        "sec_lang": "🌐 Idiomas & Certificaciones",
        "pdf_profile": "PERFIL PROFESIONAL",
        "pdf_exp": "EXPERIENCIA LABORAL",
        "pdf_proj": "PROYECTOS DESTACADOS",
        "pdf_skills": "HABILIDADES & COMPETENCIAS",
        "pdf_edu": "EDUCACIÓN",
        "pdf_lang": "IDIOMAS Y CERTIFICACIONES",
        "btn_dl_pdf": "📥 Descargar PDF ATS",
        "btn_dl_json": "💾 Respaldar Datos (.JSON)",
    },
    "Français 🇫🇷": {
        "sec_contact": "📌 Coordonnées",
        "sec_profile": "📝 Profil Professionnel",
        "sec_exp": "💼 Expérience Professionnelle",
        "sec_proj": "🔬 Projets Majeurs",
        "sec_skills": "🎯 Compétences",
        "sec_edu": "🎓 Éducation",
        "sec_lang": "🌐 Langues & Certifications",
        "pdf_profile": "PROFIL PROFESSIONNEL",
        "pdf_exp": "EXPÉRIENCE PROFESSIONNELLE",
        "pdf_proj": "PROJETS MAJEURS",
        "pdf_skills": "COMPÉTENCES",
        "pdf_edu": "ÉDUCATION",
        "pdf_lang": "LANGUES ET CERTIFICATIONS",
        "btn_dl_pdf": "📥 Télécharger PDF ATS",
        "btn_dl_json": "💾 Sauvegarder (.JSON)",
    },
}


# =========================================================
# CSS STYLES
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    .ats-badge {
        background-color: #238636;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .os-badge {
        background-color: #1F6FEB;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SANITIZE TEXT FUNCTION
# =========================================================

def sanitize(text):
    if not text:
        return ""
    return html.escape(str(text).strip())


# =========================================================
# ATS PDF GENERATOR
# =========================================================

def generate_ats_pdf(data, config, t):
    buffer = io.BytesIO()
    margin = config["margin"]

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    styles = getSampleStyleSheet()
    font_family = config["font_family"]
    base_size = config["base_size"]

    font_map = {
        "Helvetica": ("Helvetica", "Helvetica-Bold"),
        "Times-Roman": ("Times-Roman", "Times-Bold"),
        "Courier": ("Courier", "Courier-Bold"),
    }

    font_regular, font_bold = font_map.get(
        font_family,
        ("Helvetica", "Helvetica-Bold"),
    )

    style_name = ParagraphStyle(
        "ATS_Name",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=base_size + 8,
        leading=base_size + 12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1A1A1A"),
    )

    style_contact = ParagraphStyle(
        "ATS_Contact",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=base_size - 1,
        leading=base_size + 2,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4A4A4A"),
    )

    style_heading = ParagraphStyle(
        "ATS_Heading",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=base_size + 1.5,
        leading=base_size + 5,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#1A1A1A"),
    )

    style_body = ParagraphStyle(
        "ATS_Body",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=base_size,
        leading=base_size + 3.5,
        spaceAfter=4,
        textColor=colors.HexColor("#2D2D2D"),
    )

    style_job_title = ParagraphStyle(
        "ATS_Job",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=base_size + 0.5,
        leading=base_size + 4,
        spaceBefore=4,
        textColor=colors.HexColor("#1A1A1A"),
    )

    story = []

    # CONTACT
    story.append(Paragraph(sanitize(data["full_name"]).upper(), style_name))

    contact_parts = [
        sanitize(data[key])
        for key in ["email", "phone", "location", "linkedin"]
        if data.get(key)
    ]

    story.append(Paragraph(" | ".join(contact_parts), style_contact))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CCCCCC"), spaceAfter=6))

    # SUMMARY
    if data.get("summary"):
        story.append(Paragraph(t["pdf_profile"], style_heading))
        story.append(Paragraph(sanitize(data["summary"]), style_body))

    # EXPERIENCE
    if data.get("experience"):
        story.append(Paragraph(t["pdf_exp"], style_heading))
        for exp in data["experience"]:
            header_exp = (
                f"<b>{sanitize(exp['role'])}</b> &mdash; "
                f"{sanitize(exp['company'])} <i>({sanitize(exp['period'])})</i>"
            )
            story.append(Paragraph(header_exp, style_job_title))
            for resp in exp["responsibilities"].split("\n"):
                clean_resp = sanitize(resp)
                if clean_resp:
                    story.append(Paragraph(f"&bull; {clean_resp}", style_body))
            story.append(Spacer(1, 3))

    # PROJECTS
    if data.get("projects"):
        story.append(Paragraph(t["pdf_proj"], style_heading))
        for proj in data["projects"]:
            header_proj = f"<b>{sanitize(proj['title'])}</b> <i>({sanitize(proj['tech'])})</i>"
            story.append(Paragraph(header_proj, style_job_title))
            for desc in proj["details"].split("\n"):
                clean_desc = sanitize(desc)
                if clean_desc:
                    story.append(Paragraph(f"&bull; {clean_desc}", style_body))
            story.append(Spacer(1, 3))

    # SKILLS
    if data.get("skills"):
        story.append(Paragraph(t["pdf_skills"], style_heading))
        story.append(Paragraph(sanitize(data["skills"]), style_body))

    # EDUCATION
    if data.get("education"):
        story.append(Paragraph(t["pdf_edu"], style_heading))
        for edu in data["education"]:
            edu_text = (
                f"<b>{sanitize(edu['degree'])}</b> &mdash; "
                f"{sanitize(edu['institution'])} <i>({sanitize(edu['year'])})</i>"
            )
            story.append(Paragraph(edu_text, style_body))

    # LANGUAGES
    if data.get("languages"):
        story.append(Paragraph(t["pdf_lang"], style_heading))
        story.append(Paragraph(sanitize(data["languages"]), style_body))

    doc.build(story)
    buffer.seek(0)
    return buffer


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.header("🌐 Language Selection")
    selected_lang = st.selectbox(
        "Document Language",
        options=list(I18N.keys()),
        index=0,
    )
    t = I18N[selected_lang]

    st.markdown("---")
    st.header("⚙️ AI Engine Status")

    if groq_api_key:
        st.success("🟢 API Key Securely Connected")
    else:
        st.error("🔴 GROQ_API_KEY Missing in Secrets")

    st.info(f"🤖 Active Model:\n\n`{MODEL_NAME}`")
    st.markdown("---")

    st.header("⚙️ ATS Layout Settings")
    font_choice = st.selectbox(
        "ATS Font Family",
        options=["Helvetica", "Times-Roman", "Courier"],
        index=0,
    )
    base_font_size = st.slider(
        "Font Size", min_value=8.0, max_value=12.0, value=9.5, step=0.5
    )
    margin_size = st.slider(
        "Margins (pt)", min_value=20, max_value=60, value=35, step=5
    )

pdf_config = {
    "font_family": font_choice,
    "base_size": base_font_size,
    "margin": margin_size,
}


# =========================================================
# MAIN INTERFACE
# =========================================================

st.title("📄 ATS Resume Canvas Studio")
st.markdown(
    """
    <span class='ats-badge'>ATS Compliance</span>
    <span class='os-badge'>Powered by Groq AI</span>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Active model in this application: {MODEL_NAME}")
st.markdown("<br>", unsafe_allow_html=True)

col_canvas, col_preview = st.columns([1.1, 1])


# =========================================================
# SESSION STATE
# =========================================================

if "exp_count" not in st.session_state:
    st.session_state.exp_count = 1

if "proj_count" not in st.session_state:
    st.session_state.proj_count = 1


# =========================================================
# CANVAS EDITING COLUMN
# =========================================================

with col_canvas:
    st.subheader("🛠️ Editing Canvas")

    # CONTACT
    with st.expander(t["sec_contact"], expanded=True):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("Full Name", "Ana Aguilar, B.S.")
        email = c2.text_input("Email Address", "ana.aguilar@email.com")
        phone = c1.text_input("Phone Number", "+1 (555) 019-2831")
        location = c2.text_input("Location", "Austin, TX")
        linkedin = st.text_input("LinkedIn / Portfolio URL", "linkedin.com/in/ana-biomedical")

    # SUMMARY
    with st.expander(t["sec_profile"], expanded=True):
        summary = st.text_area(
            "Professional Summary",
            height=80,
            value=(
                "Biomedical Engineer specializing in medical software development, "
                "biological signal processing, and clinical compliance standards. "
                "Proven experience using Python, MATLAB, and developing interactive healthcare applications."
            ),
        )

    # EXPERIENCE
    with st.expander(t["sec_exp"], expanded=True):
        experiences = []
        for i in range(st.session_state.exp_count):
            st.markdown(f"**Role {i + 1}**")
            ec1, ec2 = st.columns(2)
            role = ec1.text_input(f"Job Title {i + 1}", "Medical Software Engineer", key=f"role_{i}")
            company = ec2.text_input(f"Company {i + 1}", "HealthTech Innovations", key=f"company_{i}")
            period = st.text_input(f"Period {i + 1}", "2024 - Present", key=f"period_{i}")
            responsibilities = st.text_area(
                f"Responsibilities {i + 1}",
                value=(
                    "Developed a Streamlit-based web app for pre-audit clinical documentation checks.\n"
                    "Implemented Python algorithms for signal filtering and biological data analysis.\n"
                    "Streamlined medical data record review workflows."
                ),
                key=f"responsibilities_{i}",
                height=100,
            )
            experiences.append({
                "role": role,
                "company": company,
                "period": period,
                "responsibilities": responsibilities,
            })
            st.divider()

        if st.button("➕ Add Experience"):
            st.session_state.exp_count += 1
            st.rerun()

    # PROJECTS
    with st.expander(t["sec_proj"], expanded=False):
        projects = []
        for j in range(st.session_state.proj_count):
            st.markdown(f"**Project {j + 1}**")
            pc1, pc2 = st.columns(2)
            project_title = pc1.text_input(f"Project Title {j + 1}", "Hybrid Magnetic Hemocitapheresis System (HMS)", key=f"project_title_{j}")
            project_tech = pc2.text_input(f"Technologies {j + 1}", "Python, Magnetite Nanoflowers", key=f"project_tech_{j}")
            project_details = st.text_area(
                f"Description {j + 1}",
                value=(
                    "Designed a conceptual prototype for endotoxin extraction from blood microfluidic channels.\n"
                    "Simulated fluid mechanics and calculated magnetic capture rates for targeted separation."
                ),
                key=f"project_details_{j}",
                height=90,
            )
            projects.append({
                "title": project_title,
                "tech": project_tech,
                "details": project_details,
            })
            st.divider()

        if st.button("➕ Add Project"):
            st.session_state.proj_count += 1
            st.rerun()

    # SKILLS
    with st.expander(t["sec_skills"], expanded=True):
        skills = st.text_area(
            "Skills",
            value=(
                "Python, MATLAB, Streamlit, Biological Signal Processing (ECG), "
                "Git, PyVis, Regex, Data Analysis, Medical Device Standards."
            ),
        )

    # LANGUAGES & CERTIFICATIONS
    with st.expander(t["sec_lang"], expanded=False):
        languages = st.text_area(
            "Languages & Certifications",
            value=(
                "English (Native/Fluent), Spanish (Professional), "
                "French (Intermediate), Introduction to AI Certification."
            ),
        )

    # EDUCATION
    with st.expander(t["sec_edu"], expanded=False):
        degree = st.text_input("Degree", "B.S. in Biomedical Engineering")
        institution = st.text_input("University / Institution", "State University")
        year = st.text_input("Graduation Year", "2026")
        education = [{"degree": degree, "institution": institution, "year": year}]

    # AI FEEDBACK
    with st.expander("🤖 Open Source AI ATS Feedback", expanded=False):
        st.info(f"💡 **Active Model:** `{MODEL_NAME}`\n\nThe AI compares your resume content against a job description.")

        st.markdown("##### Option 1: Use Form Resume")
        st.caption("Information filled in the form sections above will be analyzed.")

        st.markdown("##### Option 2: Upload External Resume")
        uploaded_cv = st.file_uploader("Upload Resume File", type=["pdf", "txt"], key="ai_cv_uploader")

        st.divider()
        job_offer = st.text_area("Paste the job description here:", height=150)
        btn_analyze = st.button("⚡ Analyze ATS Match", type="primary")

        if btn_analyze:
            if Groq is None:
                st.error("❌ The 'groq' package is not installed. Run: `pip install groq`")
            elif not groq_api_key.strip():
                st.error("⚠️ GROQ_API_KEY is missing in secrets.toml / Streamlit Cloud Settings.")
            elif not job_offer.strip():
                st.warning("⚠️ Please paste the job description before running the analysis.")
            else:
                with st.spinner(f"⚡ Analyzing with {MODEL_NAME}..."):
                    try:
                        cv_text_to_analyze = ""
                        if uploaded_cv is not None:
                            if uploaded_cv.name.lower().endswith(".pdf"):
                                reader = get_pdf_reader(uploaded_cv)
                                for page in reader.pages:
                                    text_page = page.extract_text()
                                    if text_page:
                                        cv_text_to_analyze += text_page + "\n"
                            elif uploaded_cv.name.lower().endswith(".txt"):
                                cv_text_to_analyze = uploaded_cv.read().decode("utf-8", errors="ignore")
                        else:
                            cv_text_to_analyze = f"""
Name: {full_name}
Summary: {summary}
Experience: {json.dumps(experiences, ensure_ascii=False, indent=2)}
Projects: {json.dumps(projects, ensure_ascii=False, indent=2)}
Skills: {skills}
Languages: {languages}
Education: {json.dumps(education, ensure_ascii=False, indent=2)}
"""
                        if not cv_text_to_analyze.strip():
                            st.error("❌ Could not extract text from the resume.")
                        else:
                            client = Groq(api_key=groq_api_key.strip())
                            prompt = f"""
Analyze the following Resume against the Job Description.

RESUME CONTENT:
{cv_text_to_analyze}

JOB DESCRIPTION:
{job_offer}

Respond ONLY with valid JSON using the following structure:
{{
    "match_percentage": 0,
    "summary": "",
    "strengths": [],
    "weaknesses": [],
    "keywords_found": [],
    "keywords_missing": [],
    "actionable_recommendations": []
}}
"""
                            chat_completion = client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": "You are an expert ATS recruitment analyst. Respond strictly in valid JSON format."},
                                    {"role": "user", "content": prompt},
                                ],
                                model=MODEL_NAME,
                                response_format={"type": "json_object"},
                                temperature=0.3,
                            )

                            raw_text = chat_completion.choices[0].message.content
                            if not raw_text:
                                raise ValueError("Groq returned empty content.")

                            ai_data = json.loads(raw_text)
                            score = ai_data.get("match_percentage", 0)
                            try:
                                score = int(score)
                            except (TypeError, ValueError):
                                score = 0
                            score = max(0, min(score, 100))

                            st.success("🎉 Analysis complete!")
                            st.metric("ATS Match Score", f"{score}%")
                            st.write(ai_data.get("summary", ""))

                            col_str, col_weak = st.columns(2)
                            with col_str:
                                st.markdown("##### 🟢 Strengths")
                                for s in ai_data.get("strengths", []):
                                    st.markdown(f"- {s}")
                            with col_weak:
                                st.markdown("##### 🔴 Areas for Improvement")
                                for w in ai_data.get("weaknesses", []):
                                    st.markdown(f"- {w}")

                            st.markdown("##### 🔑 Keywords Found")
                            st.write(", ".join(ai_data.get("keywords_found", [])))

                            st.markdown("##### ⚠️ Missing Keywords")
                            st.write(", ".join(ai_data.get("keywords_missing", [])))

                            st.markdown("##### 📌 Actionable Recommendations")
                            for rec in ai_data.get("actionable_recommendations", []):
                                st.markdown(f"- {rec}")

                    except Exception as err:
                        st.error(f"❌ An error occurred while processing your request: {err}")


# =========================================================
# PREVIEW AND EXPORT COLUMN
# =========================================================

cv_full_data = {
    "full_name": full_name,
    "email": email,
    "phone": phone,
    "location": location,
    "linkedin": linkedin,
    "summary": summary,
    "experience": experiences,
    "projects": projects,
    "skills": skills,
    "languages": languages,
    "education": education,
}

with col_preview:
    st.subheader("👁️ Preview & Export")

    # Generate PDF
    pdf_bytes = generate_ats_pdf(cv_full_data, pdf_config, t)

    st.download_button(
        label=t["btn_dl_pdf"],
        data=pdf_bytes,
        file_name=f"Resume_{full_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
        key="btn_download_pdf_preview",
    )

    json_str = json.dumps(cv_full_data, indent=2, ensure_ascii=False)
    st.download_button(
        label=t["btn_dl_json"],
        data=json_str,
        file_name=f"Resume_{full_name.replace(' ', '_')}.json",
        mime="application/json",
        key="btn_download_json_preview",
    )

    st.markdown("---")
    st.markdown("### Document Live Preview")

    from streamlit_pdf_viewer import pdf_viewer

    pdf_viewer(input=pdf_bytes.getvalue(), height=750)
