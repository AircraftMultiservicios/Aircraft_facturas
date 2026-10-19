import streamlit as st
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import textwrap

# --- CONFIGURACIÓN DE LA EMPRESA ---
NOMBRE_EMPRESA = "AIRCRAFT MULTISERVICIOS"
SLOGAN = "SISTEMAS DE CLIMATIZACION Y REFRIGERACION"
NIT = "1087200869"
TELEFONO = "+57 302 681 2764"
CORREO = "aircraftmultiservicios30@gmail.com"
ARCHIVO_CONTADOR = "contador_reportes.txt"

# --- FUNCIONES DE SOPORTE ---
def obtener_siguiente_numero():
    if not os.path.exists(ARCHIVO_CONTADOR):
        return 1
    with open(ARCHIVO_CONTADOR, "r") as f:
        try:
            return int(f.read().strip())
        except:
            return 1

def incrementar_contador(numero):
    with open(ARCHIVO_CONTADOR, "w") as f:
        f.write(str(numero + 1))

# --- GENERADOR DE PDF CON REPORTLAB ---
def generar_pdf_reporte(datos, numero_reporte):
    ruta_pdf = "reporte_temp.pdf"
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter

    # --- ENCABEZADO IZQUIERDO (Logo y Datos) ---
    y_centro = height - 75
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    try:
        if os.path.exists(ruta_logo):
            c.drawImage(ruta_logo, 40, y_centro - 25, width=50, height=50, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"Error logo: {e}")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(115, y_centro + 15, "AIRCRAFT")
    c.drawString(115, y_centro, "MULTISERVICIOS")
    
    c.setFont("Helvetica", 7.5) 
    c.setFillColor(colors.black)
    c.drawString(115, y_centro - 10, SLOGAN)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(115, y_centro - 19, f"NIT: {NIT}")
    c.setFont("Helvetica", 7.5)
    c.drawString(115, y_centro - 27, f"Telefono: {TELEFONO}")
    c.drawString(115, y_centro - 35, f"Correo: {CORREO}")

    # --- RECUADRO DERECHO (REPORTE TÉCNICO) ---
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(1)
    c.rect(width - 240, height - 140, 200, 90)
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width - 140, height - 65, "REPORTE TÉCNICO")
    
    c.setStrokeColor(colors.HexColor("#1e50b4"))
    c.setLineWidth(2)
    c.line(width - 230, height - 75, width - 50, height - 75)
    
    c.setFont("Helvetica", 9) 
    c.drawCentredString(width - 140, height - 90, f"Numero: #R-{numero_reporte:03d}")
    
    fecha_actual = datetime.now().strftime("%d de %B, %Y")
    meses = {"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril", "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto", "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"}
    for k, v in meses.items():
        fecha_actual = fecha_actual.replace(k, v)
    c.drawCentredString(width - 140, height - 105, f"Fecha: {fecha_actual}")

    # =======================================================
    # NUEVO DISEÑO: RECUADROS CON BARRA AZUL (DATOS)
    # =======================================================
    y_base_datos = height - 165 # Punto de partida
    alto_caja = 65 # Altura fija para que ambos lados queden perfectos

    # --- CAJA IZQUIERDA (CLIENTE) ---
    # Fondo gris
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(40, y_base_datos - alto_caja, 250, alto_caja, fill=1, stroke=0)
    # Barra azul
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.rect(40, y_base_datos - alto_caja, 4, alto_caja, fill=1, stroke=0)

    # Textos Cliente
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(50, y_base_datos - 15, "DATOS DEL CLIENTE")
    
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.black)
    c.drawString(50, y_base_datos - 28, f"Nombre: {datos['cliente_nombre']}")
    c.drawString(50, y_base_datos - 40, f"Teléfono: {datos['cliente_telefono']}")
    # Si la dirección es muy larga, la cortamos un poco para que no se salga de la caja
    dir_corta = datos['cliente_direccion'][:40] + "..." if len(datos['cliente_direccion']) > 40 else datos['cliente_direccion']
    c.drawString(50, y_base_datos - 52, f"Dirección: {dir_corta}")


    # --- CAJA DERECHA (EQUIPO) ---
    x_derecha = 310
    # Fondo gris
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(x_derecha, y_base_datos - alto_caja, 260, alto_caja, fill=1, stroke=0)
    # Barra azul
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.rect(x_derecha, y_base_datos - alto_caja, 4, alto_caja, fill=1, stroke=0)

    # Textos Equipo
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(x_derecha + 10, y_base_datos - 15, "DATOS DEL EQUIPO")
    
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.black)
    c.drawString(x_derecha + 10, y_base_datos - 28, f"Tipo: {datos['equipo_tipo']}")
    c.drawString(x_derecha + 10, y_base_datos - 40, f"Marca/Modelo: {datos['equipo_marca']}")
    c.drawString(x_derecha + 10, y_base_datos - 52, f"Serial: {datos['equipo_serial']}")

    # =======================================================

    # --- DIAGNÓSTICO Y TRABAJO ---
    y_seccion_texto = y_base_datos - alto_caja - 30 # Empezamos debajo de las cajas

    # 1. Diagnóstico
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, y_seccion_texto, "DIAGNÓSTICO INICIAL")
    
    texto_diag = datos['diagnostico'].replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
    lineas_diag = textwrap.wrap(texto_diag, width=110)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    y_diag = y_seccion_texto - 15
    for linea in lineas_diag:
        c.drawString(40, y_diag, linea)
        y_diag -= 13

    # 2. Trabajo Realizado
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, y_diag - 10, "TRABAJO REALIZADO")
    
    texto_trabajo = datos['trabajo'].replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
    lineas_trabajo = textwrap.wrap(texto_trabajo, width=110)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    y_trabajo = y_diag - 25
    for linea in lineas_trabajo:
        c.drawString(40, y_trabajo, linea)
        y_trabajo -= 13

    # --- RECOMENDACIONES ---
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, y_trabajo - 10, "RECOMENDACIONES")
    
    texto_recom = datos['recomendaciones'].replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
    lineas_recom = textwrap.wrap(texto_recom, width=110)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    y_recom = y_trabajo - 25
    for linea in lineas_recom:
        c.drawString(40, y_recom, linea)
        y_recom -= 13

    # --- FIRMAS ---
    y_firmas = 120
    
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    
    # Firma Técnico
    c.line(50, y_firmas, 250, y_firmas)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_firmas - 15, "Técnico Responsable")
    c.setFont("Helvetica", 8)
    c.drawString(50, y_firmas - 27, NOMBRE_EMPRESA)
    
    # Firma Cliente
    c.line(320, y_firmas, 520, y_firmas)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(320, y_firmas - 15, "Firma del Cliente")
    c.setFont("Helvetica", 8)
    c.drawString(320, y_firmas - 27, f"C.C. {datos['cliente_cedula']}")

    c.save()
    
    with open(ruta_pdf, "rb") as f:
        pdf_bytes = f.read()
    os.remove(ruta_pdf)
    
    return pdf_bytes

# --- INTERFAZ GRÁFICA (STREAMLIT) ---
st.set_page_config(page_title="Reportes - AIRCRAFT", page_icon="🔧", layout="wide")

st.title("🔧 Generador de Reportes Técnicos")
st.subheader("AIRCRAFT MULTISERVICIOS")

with st.form("formulario_reporte"):
    st.write("👤 Datos del Cliente")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cliente_nombre = st.text_input("Nombre del Cliente")
    with col_c2:
        cliente_cedula = st.text_input("Cédula del Cliente")
    with col_c3:
        cliente_telefono = st.text_input("Teléfono del Cliente")
    cliente_direccion = st.text_input("Dirección del Cliente")
    
    st.write("❄️ Datos del Equipo")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        equipo_tipo = st.text_input("Tipo de Equipo (Ej: Aire Acondicionado Split)")
    with col_e2:
        equipo_marca = st.text_input("Marca y Modelo")
    with col_e3:
        equipo_serial = st.text_input("Número de Serial")

    st.write("🛠️ Detalles del Servicio")
    diagnostico = st.text_area("Diagnóstico Inicial (¿Qué se encontró?)", height=100)
    trabajo = st.text_area("Trabajo Realizado (¿Qué se reparó?)", height=100)
    recomendaciones = st.text_area("Recomendaciones (Opcional)", height=80)
    
    submit = st.form_submit_button("Generar Reporte en PDF", type="primary")

if submit:
    if not cliente_nombre or not diagnostico or not trabajo:
        st.error("⚠️ Por favor, llena al menos el nombre del cliente, el diagnóstico y el trabajo realizado.")
    else:
        numero_actual = obtener_siguiente_numero()
        
        datos = {
            "cliente_nombre": cliente_nombre,
            "cliente_cedula": cliente_cedula,
            "cliente_telefono": cliente_telefono,
            "cliente_direccion": cliente_direccion,
            "equipo_tipo": equipo_tipo,
            "equipo_marca": equipo_marca,
            "equipo_serial": equipo_serial,
            "diagnostico": diagnostico,
            "trabajo": trabajo,
            "recomendaciones": recomendaciones
        }
        
        pdf_bytes = generar_pdf_reporte(datos, numero_actual)
        incrementar_contador(numero_actual)
        
        st.success(f"✅ Reporte Técnico #R-{numero_actual:03d} generado con éxito.")
        
        st.download_button(
            label="⬇️ Descargar Reporte PDF",
            data=pdf_bytes,
            file_name=f"Reporte_Tecnico_{numero_actual:03d}.pdf",
            mime="application/pdf"
        )
