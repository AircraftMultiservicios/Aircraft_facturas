import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Agenda Aircraft", page_icon="❄️", layout="wide")

# --- ESTILOS CSS (Para que se vea como tu reporte) ---
st.markdown("""
    <style>
    /* Estilo del recuadro gris con borde azul */
    .card {
        background-color: #F3F4F6;
        border-left: 5px solid #1A437A;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .card-title {
        color: #1A437A;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 10px;
    }
    /* Estilo para el recuadro del número de reporte */
    .report-box {
        border: 1px solid #D1D5DB;
        padding: 15px;
        text-align: center;
        border-radius: 5px;
        background-color: white;
    }
    .report-box h3 {
        margin: 0;
        color: #1F2937;
        font-size: 16px;
    }
    .report-box p {
        margin: 5px 0 0 0;
        font-size: 14px;
        color: #4B5563;
    }
    /* Botón azul */
    .stButton>button {
        background-color: #1A437A;
        color: white;
        font-weight: bold;
        width: 100%;
        height: 50px;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #3B82F6;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- MANEJO DE DATOS (Base de datos simple en CSV) ---
ARCHIVO_DATOS = "citas.csv"

def cargar_citas():
    if os.path.exists(ARCHIVO_DATOS):
        return pd.read_csv(ARCHIVO_DATOS)
    else:
        return pd.DataFrame(columns=["ID", "Fecha", "Hora", "Cliente", "Telefono", "Direccion", "Equipo", "Marca", "Serial", "Motivo"])

def guardar_cita(nueva_cita):
    df = cargar_citas()
    df = pd.concat([df, pd.DataFrame([nueva_cita])], ignore_index=True)
    df.to_csv(ARCHIVO_DATOS, index=False)

def generar_id():
    df = cargar_citas()
    if len(df) == 0:
        return "R-001"
    else:
        ultimo_id = df.iloc[-1]["ID"]
        numero = int(ultimo_id.split("-")[1]) + 1
        return f"R-{numero:03d}"

# --- ENCABEZADO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    # Si subiste un logo.png al repositorio, lo mostrará. Si no, muestra un texto.
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.info("Sube tu logo.png aquí")

with col_titulo:
    st.markdown("<h2 style='color:#1A437A; margin-bottom:0;'>AIRCRAFT MULTISERVICIOS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#4B5563; margin-top:0;'>SISTEMAS DE CLIMATIZACIÓN Y REFRIGERACIÓN</p>", unsafe_allow_html=True)

st.markdown("<hr style='border: 2px solid #1A437A;'>", unsafe_allow_html=True)

# --- FORMULARIO DE AGENDAMIENTO ---
st.markdown("### 📝 Nueva Cita")

# Mostramos el número de cita que toca
proximo_id = generar_id()

col_izq, col_der = st.columns(2)

with col_izq:
    # Tarjeta Datos Cliente
    st.markdown('<div class="card"><div class="card-title">DATOS DEL CLIENTE</div></div>', unsafe_allow_html=True)
    nombre = st.text_input("Nombre completo", key="nom")
    telefono = st.text_input("Teléfono", key="tel")
    direccion = st.text_input("Dirección", key="dir")
    
    # Tarjeta Datos Equipo
    st.markdown('<div class="card"><div class="card-title">DATOS DEL EQUIPO</div></div>', unsafe_allow_html=True)
    equipo = st.text_input("Tipo de equipo (Ej: Aire acondicionado split)", key="eq")
    marca = st.text_input("Marca/Modelo", key="mar")
    serial = st.text_input("Serial", key="ser")

with col_der:
    # Recuadro del ID
    st.markdown(f"""
        <div class="report-box">
            <h3>NUEVA CITA</h3>
            <p>Número: <b>#{proximo_id}</b></p>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    
    # Calendario y Hora
    fecha_cita = st.date_input("Seleccione la fecha (Día/Mes/Año)", min_value=date.today())
    hora_cita = st.time_input("Seleccione la hora")
    
    motivo = st.text_area("Motivo / Diagnóstico inicial", key="mot")

st.write("---")

# Botón para guardar
if st.button("AGENDAR CITA"):
    if nombre and telefono and fecha_cita and hora_cita:
        nueva_cita = {
            "ID": proximo_id,
            "Fecha": fecha_cita.strftime("%d/%m/%Y"),
            "Hora": hora_cita.strftime("%I:%M %p"),
            "Cliente": nombre,
            "Telefono": telefono,
            "Direccion": direccion,
            "Equipo": equipo,
            "Marca": marca,
            "Serial": serial,
            "Motivo": motivo
        }
        guardar_cita(nueva_cita)
        st.success(f"✅ ¡Cita #{proximo_id} agendada con éxito!")
        st.balloons() # Animación de globos
        st.rerun() # Recarga para actualizar el número
    else:
        st.error("⚠️ Por favor, llena los campos obligatorios (Nombre, Teléfono, Fecha y Hora).")

# --- VER AGENDA ---
st.markdown("### 📅 Citas Agendadas")
df_citas = cargar_citas()

if not df_citas.empty:
    # Mostramos la tabla de citas
    st.dataframe(df_citas, use_container_width=True, hide_index=True)
else:
    st.info("Aún no hay citas agendadas.")
