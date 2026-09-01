import io
import html
import json
import base64
import importlib
import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai
from google.genai import types
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


def get_pdf_reader(file_object):
    """Return a PDF reader without requiring a specific package at import time."""
    for package_name in ("pypdf", "PyPDF2"):
        try:
            pdf_module = importlib.import_module(package_name)
            return pdf_module.PdfReader(file_object)
        except ImportError:
            continue
    raise ImportError("Instala la dependencia PDF con `pip install pypdf`.")

st.set_page_config(layout="wide", page_title="ATS Resume Canvas Studio", page_icon="📄")

# Obtener API Key desde secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Diccionario de Idiomas (i18n)
I18N = {
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
        "pdf_lang": "IDIOMAS & CERTIFICACIONES",
        "btn_dl_pdf": "📥 Descargar PDF ATS",
        "btn_dl_json": "💾 Respaldar Datos (.JSON)"
    },
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
        "btn_dl_json": "💾 Backup Data (.JSON)"
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
        "btn_dl_json": "💾 Sauvegarder (.JSON)"
    }
}

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E6ED; }
    .ats-badge { background-color: #238636; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def sanitize(text: str) -> str:
    if not text:
        return ""
    return html.escape(text.strip())

# --- GENERADOR PDF ATS DINÁMICO MULTILINGÜE ---
def generate_ats_pdf(data, config, t):
    buffer = io.BytesIO()
    m = config['margin']
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=m, leftMargin=m, topMargin=m, bottomMargin=m
    )
    
    styles = getSampleStyleSheet()
    font_family = config['font_family']
    base_size = config['base_size']
    
    font_map = {
        "Helvetica": ("Helvetica", "Helvetica-Bold"),
        "Times-Roman": ("Times-Roman", "Times-Bold"),
        "Courier": ("Courier", "Courier-Bold")
    }
    font_regular, font_bold = font_map.get(font_family, ("Helvetica", "Helvetica-Bold"))
    
    style_name = ParagraphStyle('ATS_Name', parent=styles['Normal'], fontName=font_bold, fontSize=base_size+8, leading=base_size+12, alignment=TA_CENTER, textColor=colors.HexColor('#1A1A1A'))
    style_contact = ParagraphStyle('ATS_Contact', parent=styles['Normal'], fontName=font_regular, fontSize=base_size-1, leading=base_size+2, alignment=TA_CENTER, textColor=colors.HexColor('#4A4A4A'))
    style_heading = ParagraphStyle('ATS_Heading', parent=styles['Normal'], fontName=font_bold, fontSize=base_size+1.5, leading=base_size+5, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor('#1A1A1A'))
    style_body = ParagraphStyle('ATS_Body', parent=styles['Normal'], fontName=font_regular, fontSize=base_size, leading=base_size+3.5, spaceAfter=4, textColor=colors.HexColor('#2D2D2D'))
    style_job_title = ParagraphStyle('ATS_Job', parent=styles['Normal'], fontName=font_bold, fontSize=base_size+0.5, leading=base_size+4, spaceBefore=4, textColor=colors.HexColor('#1A1A1A'))

    story = []

    # 1. Contact
    story.append(Paragraph(sanitize(data['full_name']).upper(), style_name))
    contact_parts = [sanitize(data[k]) for k in ['email', 'phone', 'location', 'linkedin'] if data[k]]
    story.append(Paragraph(" | ".join(contact_parts), style_contact))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CCCCCC'), spaceAfter=6))

    # 2. Perfil
    if data['summary']:
        story.append(Paragraph(t['pdf_profile'], style_heading))
        story.append(Paragraph(sanitize(data['summary']), style_body))

    # 3. Experiencia
    if data['experience']:
        story.append(Paragraph(t['pdf_exp'], style_heading))
        for exp in data['experience']:
            header_exp = f"<b>{sanitize(exp['role'])}</b> &mdash; {sanitize(exp['company'])} <i>({sanitize(exp['period'])})</i>"
            story.append(Paragraph(header_exp, style_job_title))
            for resp in exp['responsibilities'].split('\n'):
                clean_resp = sanitize(resp)
                if clean_resp:
                    story.append(Paragraph(f"&bull; {clean_resp}", style_body))
            story.append(Spacer(1, 3))

    # 4. Proyectos
    if data['projects']:
        story.append(Paragraph(t['pdf_proj'], style_heading))
        for proj in data['projects']:
            header_proj = f"<b>{sanitize(proj['title'])}</b> <i>({sanitize(proj['tech'])})</i>"
            story.append(Paragraph(header_proj, style_job_title))
            for desc in proj['details'].split('\n'):
                clean_desc = sanitize(desc)
                if clean_desc:
                    story.append(Paragraph(f"&bull; {clean_desc}", style_body))
            story.append(Spacer(1, 3))

    # 5. Habilidades
    if data['skills']:
        story.append(Paragraph(t['pdf_skills'], style_heading))
        story.append(Paragraph(sanitize(data['skills']), style_body))

    # 6. Educación
    if data['education']:
        story.append(Paragraph(t['pdf_edu'], style_heading))
        for edu in data['education']:
            edu_text = f"<b>{sanitize(edu['degree'])}</b> &mdash; {sanitize(edu['institution'])} <i>({sanitize(edu['year'])})</i>"
            story.append(Paragraph(edu_text, style_body))

    # 7. Idiomas & Certificaciones
    if data.get('languages'):
        story.append(Paragraph(t['pdf_lang'], style_heading))
        story.append(Paragraph(sanitize(data['languages']), style_body))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🌐 Language / Idioma")
    selected_lang = st.selectbox("Seleccionar Idioma del Documento", options=list(I18N.keys()), index=0)
    t = I18N[selected_lang]
    
    st.markdown("---")
    st.header("⚙️ Design Settings")
    font_choice = st.selectbox("Tipografía ATS", options=["Helvetica", "Times-Roman", "Courier"], index=0)
    base_font_size = st.slider("Tamaño Fuente", min_value=8.0, max_value=12.0, value=9.5, step=0.5)
    margin_size = st.slider("Márgenes (pt)", min_value=20, max_value=60, value=35, step=5)
    
    st.markdown("---")
    st.header("💾 Backup / Restaurar")
    uploaded_file = st.file_uploader("Cargar JSON de CV", type=["json"])

pdf_config = {'font_family': font_choice, 'base_size': base_font_size, 'margin': margin_size}

# --- INTERFAZ PRINCIPAL ---
st.title("📄 Resume Canvas ATS Studio")
st.markdown("<span class='ats-badge'>Multilingual ATS Compliance</span>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col_canvas, col_preview = st.columns([1.1, 1])

if 'exp_count' not in st.session_state:
    st.session_state.exp_count = 1
if 'proj_count' not in st.session_state:
    st.session_state.proj_count = 1

with col_canvas:
    st.subheader("🛠️ Lienzo de Edición")
    
    with st.expander(t["sec_contact"], expanded=True):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("Nombre Completo / Full Name", "Ing. Ana Aguilar")
        email = c2.text_input("Correo / Email", "ana.aguilar@email.com")
        phone = c1.text_input("Teléfono / Phone", "+52 55 1234 5678")
        location = c2.text_input("Ubicación / Location", "Ciudad de México, MX")
        linkedin = st.text_input("LinkedIn / Portfolio URL", "linkedin.com/in/ana-biomedica")

    with st.expander(t["sec_profile"], expanded=True):
        summary = st.text_area(
            "Resumen / Summary",
            height=80,
            value="Ingeniera biomédica enfocada en el desarrollo de software médico, análisis de señales biológicas y cumplimiento normativo (NOM-004-SSA3-2012). Experiencia en Python, MATLAB y herramientas clínicas interactivas."
        )

    with st.expander(t["sec_exp"], expanded=True):
        experiences = []
        for i in range(st.session_state.exp_count):
            st.markdown(f"**Puesto / Role {i+1}**")
            ec1, ec2 = st.columns(2)
            role = ec1.text_input(f"Título del Cargo {i+1}", "Desarrolladora de Software Médico", key=f"role_{i}")
            company = ec2.text_input(f"Empresa {i+1}", "Hospital / Red Médica", key=f"comp_{i}")
            period = st.text_input(f"Periodo {i+1}", "2024 - Presente", key=f"per_{i}")
            resp = st.text_area(f"Responsabilidades {i+1}", 
                                "Desarrollo de sistema web en Streamlit para pre-auditoría clínica.\nImplementación de algoritmos en Python para filtrado de señales fisiológicas.\nOptimizó la revisión de expedientes clínicos en un 35%.", 
                                key=f"resp_{i}", height=80)
            experiences.append({"role": role, "company": company, "period": period, "responsibilities": resp})
            st.divider()
        
        if st.button("➕ Añadir Experiencia"):
            st.session_state.exp_count += 1
            st.rerun()

    with st.expander(t["sec_proj"], expanded=False):
        projects = []
        for j in range(st.session_state.proj_count):
            st.markdown(f"**Proyecto {j+1}**")
            pc1, pc2 = st.columns(2)
            p_title = pc1.text_input(f"Nombre {j+1}", "Sistema de Hemocitaféresis Magnética (HMS)", key=f"ptr_{j}")
            p_tech = pc2.text_input(f"Tecnologías {j+1}", "Python, Nanoflores de Magnetita", key=f"ptch_{j}")
            p_details = st.text_area(f"Descripción {j+1}", 
                                     "Diseño de prototipo conceptual para extracción de endotoxinas en sangre.\nSimulación de mecánica de fluidos y cálculos de tasas de captura de magnetita.", 
                                     key=f"pdet_{j}", height=70)
            projects.append({"title": p_title, "tech": p_tech, "details": p_details})
            st.divider()

        if st.button("➕ Añadir Proyecto"):
            st.session_state.proj_count += 1
            st.rerun()

    with st.expander(t["sec_skills"], expanded=True):
        skills = st.text_area(
            "Skills",
            value="Python, MATLAB, Streamlit, NOM-004-SSA3-2012, Procesamiento de Señales (ECG), Git, PyVis, Regex, Análisis de Datos Clínicos."
        )

    with st.expander(t["sec_lang"], expanded=False):
        languages = st.text_area(
            "Idiomas & Certificaciones",
            value="Español (Nativo), Inglés (C1 Avanzado), Francés (B1 Intermedio), Certificación Introducción a IA - Iberoamerican Technology."
        )

    with st.expander(t["sec_edu"], expanded=False):
        degree = st.text_input("Grado / Degree", "Licenciatura en Ingeniería Biomédica")
        institution = st.text_input("Universidad / University", "Universidad Nacional")
        year = st.text_input("Año / Year", "2024")
        education = [{"degree": degree, "institution": institution, "year": year}]

    # --- MÓDULO IA GEMINI OPTIMIZADO Y CON MÉTRICAS VISUALES Y DISCLAIMER ---
    with st.expander("🤖 Feedback de Vacante con IA (Gemini)", expanded=False):
        
        st.info(
            "💡 **Aviso sobre el uso de Inteligencia Artificial:**\n"
            "El análisis de compatibilidad es generado de forma automatizada mediante IA. "
            "Los modelos automatizados pueden cometer errores o tener imprecisiones. "
            "Utiliza los resultados como una guía de referencia y no como un dictamen definitivo."
        )
        
        st.markdown("##### Opción 1: Usar el CV creado en esta app")
        st.caption("Se utilizarán los datos que llenaste en los formularios superiores.")
        
        st.markdown("##### Opción 2: Cargar un CV externo (PDF o TXT)")
        uploaded_cv = st.file_uploader("Sube tu archivo de CV", type=["pdf", "txt"], key="ai_cv_uploader")
        
        st.divider()
        job_offer = st.text_area("Pega aquí la descripción completa de la vacante:", height=120)
        btn_analyze = st.button("✨ Analizar Coincidencia ATS", type="primary")
        
        if btn_analyze:
            if not api_key:
                st.error("⚠️ Falta configurar la `GEMINI_API_KEY` en `.streamlit/secrets.toml`.")
            elif not job_offer.strip():
                st.warning("Pega la descripción de la vacante para analizarla.")
            else:
                with st.spinner("🤖 Procesando CV y analizando métricas con Gemini..."):
                    try:
                        cv_text_to_analyze = ""
                        
                        if uploaded_cv is not None:
                            if uploaded_cv.name.endswith(".pdf"):
                                reader = get_pdf_reader(uploaded_cv)
                                for page in reader.pages:
                                    text_page = page.extract_text()
                                    if text_page:
                                        cv_text_to_analyze += text_page + "\n"
                            elif uploaded_cv.name.endswith(".txt"):
                                cv_text_to_analyze = uploaded_cv.read().decode("utf-8")
                        else:
                            cv_text_to_analyze = f"""
                            Nombre: {full_name}
                            Resumen: {summary}
                            Experiencia: {experiences}
                            Proyectos: {projects}
                            Skills: {skills}
                            Idiomas: {languages}
                            Educación: {education}
                            """

                        if not cv_text_to_analyze.strip():
                            st.error("No se pudo extraer texto del CV para el análisis.")
                        else:
                            # Uso del SDK actualizado google-genai
                            client = genai.Client(api_key=str(api_key).strip())
                            
                            prompt = f"""
                            Eres un experto reclutador y especialista en filtros ATS. 
                            Analiza el siguiente CV frente a la descripción de la vacante recibida.

                            CONTENIDO DEL CV:
                            {cv_text_to_analyze}

                            DESCRIPCIÓN DE LA VACANTE:
                            {job_offer}

                            Devuelve un JSON estricto con la siguiente estructura exacta:
                            {{
                                "match_percentage": <entero del 0 al 100>,
                                "summary": "<diagnóstico general del perfil>",
                                "strengths": ["<fortaleza 1>", "<fortaleza 2>"],
                                "weaknesses": ["<área de mejora 1>", "<área de mejora 2>"],
                                "keywords_found": ["<palabra clave encontrada 1>", "<palabra clave encontrada 2>"],
                                "keywords_missing": ["<palabra clave faltante 1>", "<palabra clave faltante 2>"],
                                "actionable_recommendations": ["<sugerencia 1>", "<sugerencia 2>"]
                            }}
                            """
                            
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=prompt,
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json"
                                )
                            )
                            
                            data = json.loads(response.text)
                            st.success("¡Análisis completado!")
                            
                            # --- SECCIÓN VISUAL DE RESULTADOS ---
                            score = data.get("match_percentage", 0)
                            
                            col_m1, col_m2 = st.columns([1, 1.5])
                            with col_m1:
                                st.metric("Compatibilidad ATS", f"{score}%")
                                st.progress(score / 100)
                                if score >= 80:
                                    st.success("¡Excelente encaje!")
                                elif score >= 60:
                                    st.warning("Buena coincidencia, requiere afinar detalles.")
                                else:
                                    st.error("Baja coincidencia. Revisa las palabras clave.")

                            with col_m2:
                                found = data.get("keywords_found", [])
                                missing = data.get("keywords_missing", [])
                                
                                df_keywords = pd.DataFrame({
                                    "Estado": ["Detectadas"] * len(found) + ["Faltantes"] * len(missing),
                                    "Palabra Clave": found + missing
                                })
                                
                                if not df_keywords.empty:
                                    fig = px.bar(
                                        df_keywords, 
                                        x="Palabra Clave", 
                                        color="Estado",
                                        color_discrete_map={"Detectadas": "#238636", "Faltantes": "#da3633"},
                                        title="Palabras Clave (Keywords)",
                                        height=250
                                    )
                                    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
                                    st.plotly_chart(fig, use_container_width=True)

                            st.markdown("---")
                            
                            st.markdown(f"**Diagnóstico:** {data.get('summary', '')}")
                            
                            c_res1, c_res2 = st.columns(2)
                            with c_res1:
                                st.markdown("##### ✅ Puntos Fuertes")
                                for s in data.get("strengths", []):
                                    st.write(f"- {s}")
                                
                                st.markdown("##### 💡 Recomendaciones")
                                for r in data.get("actionable_recommendations", []):
                                    st.write(f"- {r}")

                            with c_res2:
                                st.markdown("##### ⚠️ Áreas de Mejora")
                                for w in data.get("weaknesses", []):
                                    st.write(f"- {w}")

                            st.divider()
                            st.caption(
                                "⚠️ *Aviso de responsabilidad:* Las métricas y sugerencias presentadas son generadas por Inteligencia Artificial. "
                                "Revisa manualmente las recomendaciones antes de enviar tu candidatura."
                            )

                    except Exception as err:
                        st.error(f"Error procesando la solicitud: {err}")

with col_preview:
    st.subheader("👁️ Previsualización & Exportación")
    
    cv_data = {
        "full_name": full_name, "email": email, "phone": phone,
        "location": location, "linkedin": linkedin, "summary": summary,
        "experience": experiences, "projects": projects, "skills": skills,
        "languages": languages, "education": education
    }

    pdf_buffer = generate_ats_pdf(cv_data, pdf_config, t)
    pdf_bytes = pdf_buffer.getvalue()
    
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="550" type="application/pdf" style="border-radius:8px; border:1px solid #30363D; background-color: white;"></iframe>'
    
    st.markdown(pdf_display, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.download_button(
            label=t["btn_dl_pdf"],
            data=pdf_bytes,
            file_name=f"CV_{full_name.replace(' ', '_')}_{selected_lang[:2]}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with c_btn2:
        json_str = json.dumps(cv_data, indent=4)
        st.download_button(
            label=t["btn_dl_json"],
            data=json_str,
            file_name=f"Backup_CV_{full_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
