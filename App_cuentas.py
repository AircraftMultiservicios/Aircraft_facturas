import streamlit as st
import os
import json
from datetime import datetime
from fpdf import FPDF
from num2words import num2words

# --- CONFIGURACIÓN DE DATOS FIJOS ---
NOMBRE_COBRADOR = "Eduardo Alexander Méndez Realpe"
CEDULA_COBRADOR = "1.087.200.869"
CIUDAD = "San Andrés de Tumaco"
ARCHIVO_CONTADOR = "contador.txt"

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

def numero_a_letras(numero):
    letras = num2words(numero, lang='es').capitalize()
    return f"{letras} pesos M/CTE"

# --- GENERADOR DE PDF ---
def generar_pdf(datos, numero_cuenta):
    pdf = FPDF()
    pdf.add_page()
    
    # --- LOGO ---
    # Busca el logo en la misma carpeta del script
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    
    try:
        # Si el archivo existe, lo pone en la esquina superior derecha
        if os.path.exists(ruta_logo):
            pdf.image(ruta_logo, x=10, y=10, w=22)
        else:
            # Si no lo encuentra, avisa en la consola (no rompe la app)
            print("ADVERTENCIA: No se encontró el archivo logo.png en la carpeta.")
    except Exception as e:
        print(f"Error al cargar el logo: {e}")

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CUENTA DE COBRO", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Número de cuenta
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"N° {numero_cuenta:03d}", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Fecha
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    meses = {"January": "enero", "February": "febrero", "March": "marzo", "April": "abril", "May": "mayo", "June": "junio", "July": "julio", "August": "agosto", "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre"}
    for k, v in meses.items():
        fecha_actual = fecha_actual.replace(k, v)
        
    pdf.cell(0, 15, f"{CIUDAD}, {fecha_actual}", align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Sección DEBE A
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "DEBE A:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Nombre:   {NOMBRE_COBRADOR}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Cédula:   {CEDULA_COBRADOR}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Sección A (Cliente)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "A:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Nombre:   {datos['cliente_nombre']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Cédula:   {datos['cliente_cedula']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Teléfono: {datos['cliente_telefono']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Tabla de conceptos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(130, 10, "CONCEPTO / DESCRIPCIÓN", border=1, fill=True, align="C")
    pdf.cell(45, 10, "VALOR", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 20, datos['concepto'], border=1)
    valor_formateado = f"${datos['valor']:,.0f}".replace(",", ".")
    pdf.cell(45, 20, valor_formateado, border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(130, 10, "TOTAL A PAGAR:", border=1, align="R")
    pdf.cell(45, 10, valor_formateado, border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Suma en letras
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    letras = numero_a_letras(datos['valor'])
    pdf.cell(0, 10, f"La suma de: {letras}", new_x="LMARGIN", new_y="NEXT")
    
    # Firma
    pdf.ln(20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, "_________________________________________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, NOMBRE_COBRADOR, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"C.C. {CEDULA_COBRADOR}", new_x="LMARGIN", new_y="NEXT")

    # Retornar el PDF como bytes (forma actualizada)
    return bytes(pdf.output())

# --- INTERFAZ GRÁFICA (STREAMLIT) ---
st.set_page_config(page_title="Cuentas de Cobro - AIRCRAFT", page_icon="🧾")

st.title("🧾 Generador de Cuentas de Cobro")
st.subheader("AIRCRAFT MULTISERVICIOS")

with st.form("formulario_cuenta"):
    st.write("Datos del Cliente")
    cliente_nombre = st.text_input("Nombre del Cliente")
    cliente_cedula = st.text_input("Cédula del Cliente")
    cliente_telefono = st.text_input("Teléfono del Cliente")
    
    st.write("Detalles del Servicio")
    concepto = st.text_area("Concepto / Descripción")
    valor = st.number_input("Valor a cobrar ($)", min_value=0, step=10000)
    
    submit = st.form_submit_button("Generar Cuenta de Cobro")

if submit:
    if not cliente_nombre or not concepto or valor == 0:
        st.error("⚠️ Por favor, llena todos los campos y asegúrate de que el valor sea mayor a 0.")
    else:
        numero_actual = obtener_siguiente_numero()
        
        datos = {
            "cliente_nombre": cliente_nombre,
            "cliente_cedula": cliente_cedula,
            "cliente_telefono": cliente_telefono,
            "concepto": concepto,
            "valor": valor
        }
        
        # Generar PDF
        pdf_bytes = generar_pdf(datos, numero_actual)
        
        # Actualizar contador
        incrementar_contador(numero_actual)
        
        st.success(f"✅ Cuenta de cobro N° {numero_actual:03d} generada con éxito.")
        
        st.download_button(
            label="⬇️ Descargar PDF",
            data=pdf_bytes,
            file_name=f"Cuenta_Cobro_{numero_actual:03d}.pdf",
            mime="application/pdf"
    )
