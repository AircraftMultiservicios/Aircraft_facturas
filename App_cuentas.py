import streamlit as st
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import textwrap

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
    from num2words import num2words
    letras = num2words(numero, lang='es').capitalize()
    return f"{letras} pesos M/CTE"

# --- GENERADOR DE PDF CON REPORTLAB ---
def generar_pdf_cuenta(datos, numero_cuenta):
    ruta_pdf = "cuenta_temp.pdf"
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
    c.drawString(115, y_centro - 10, "SISTEMAS DE CLIMATIZACION Y REFRIGERACION")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(115, y_centro - 19, f"NIT: 1087200869")
    c.setFont("Helvetica", 7.5)
    c.drawString(115, y_centro - 27, f"Telefono: +57 302 681 2764")
    c.drawString(115, y_centro - 35, f"Correo: aircraftmultiservicios30@gmail.com")

    # --- RECUADRO DERECHO (CUENTA DE COBRO) ---
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(1)
    c.rect(width - 240, height - 140, 200, 90) # Termina en width - 40
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width - 140, height - 65, "CUENTA DE COBRO")
    
    c.setStrokeColor(colors.HexColor("#1e50b4"))
    c.setLineWidth(2)
    c.line(width - 230, height - 75, width - 50, height - 75)
    
    c.setFont("Helvetica", 9) 
    c.drawCentredString(width - 140, height - 90, f"Numero: #{numero_cuenta:03d}")
    
    fecha_actual = datetime.now().strftime("%d de %B, %Y")
    meses = {"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril", "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto", "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"}
    for k, v in meses.items():
        fecha_actual = fecha_actual.replace(k, v)
    c.drawCentredString(width - 140, height - 105, f"Fecha: {fecha_actual}")
    c.drawCentredString(width - 140, height - 120, f"Lugar: {CIUDAD}")

    # --- DATOS DEL CLIENTE ---
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, height - 180, "DEBE A:")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(40, height - 195, f"Nombre: {NOMBRE_COBRADOR}")
    c.drawString(40, height - 207, f"Cédula: {CEDULA_COBRADOR}")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, height - 230, "A:")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(40, height - 245, f"Nombre: {datos['cliente_nombre']}")
    c.drawString(40, height - 257, f"Cédula: {datos['cliente_cedula']}")
    c.drawString(40, height - 269, f"Teléfono: {datos['cliente_telefono']}")

    # --- TÍTULO TABLA ---
    c.setFont("Helvetica-Bold", 10) 
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, height - 295, "DETALLE DEL SERVICIO")

    # --- TABLA DE CONCEPTO ---
    data = [["CONCEPTO / DESCRIPCIÓN DEL SERVICIO", "VALOR"]]
    
    estilo_celda = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=8.5, 
        leading=12, 
        alignment=TA_LEFT
    )

    texto_limpio = datos['concepto'].replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
    celda_parrafo = Paragraph(texto_limpio, estilo_celda)
    precio_str = f"${datos['valor']:,.0f}".replace(",", ".")
    data.append([celda_parrafo, precio_str])

    tabla = Table(data, colWidths=[420, 92])
    
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e50b4")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9), 
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'), 
        
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        ('FONTSIZE', (1, 1), (1, -1), 9), 
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('TOPPADDING', (0, 1), (-1, -1), 15), 
        ('BOTTOMPADDING', (0, 1), (-1, -1), 15),
        ('LEFTPADDING', (0, 1), (0, -1), 10),
    ])
    tabla.setStyle(estilo_tabla)
    
    ancho_tabla, alto_tabla = tabla.wrapOn(c, width, height)
    tabla.drawOn(c, 40, height - 315 - alto_tabla)

    # --- TOTAL A PAGAR ---
    y_totales = height - 325 - alto_tabla 
    
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setFont("Helvetica-Bold", 10) 
    c.setFillColor(colors.HexColor("#1e50b4"))
    
    # El texto del total termina en width - 40
    c.drawString(width - 210, y_totales - 15, "TOTAL A PAGAR:")
    c.drawRightString(width - 40, y_totales - 15, f"${datos['valor']:,.0f}".replace(",", "."))
    c.line(width - 220, y_totales - 20, width - 40, y_totales - 20)

    # --- VALOR EN LETRAS (Recuadro gris) ---
    # El recuadro va exactamente de X=40 hasta width - 40 (mismo ancho que la tabla y los totales)
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(40, y_totales - 75, width - 80, 40, fill=1, stroke=0)
    
    # Barra azul de la izquierda. Para que no robe espacio, la dibujamos encima del borde
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.rect(40, y_totales - 75, 5, 40, fill=1, stroke=0)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Oblique", 9)
    letras = numero_a_letras(datos['valor'])
    
    # Movemos el texto para que quede alineado con el borde de la tabla (X=50)
    c.drawString(55, y_totales - 55, "La suma de:")
    c.setFont("Helvetica", 9)
    lineas_letras = textwrap.wrap(letras, width=95)
    c.drawString(115, y_totales - 55, lineas_letras[0])
    if len(lineas_letras) > 1:
        c.drawString(115, y_totales - 67, lineas_letras[1])

    # --- FIRMA ---
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.line(50, 120, 250, 120) 
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 105, NOMBRE_COBRADOR)
    c.setFont("Helvetica", 9)
    c.drawString(50, 93, f"C.C. {CEDULA_COBRADOR}")

    c.save()
    
    with open(ruta_pdf, "rb") as f:
        pdf_bytes = f.read()
    os.remove(ruta_pdf)
    
    return pdf_bytes

# --- INTERFAZ GRÁFICA (STREAMLIT) ---
st.set_page_config(page_title="Cuentas de Cobro - AIRCRAFT", page_icon="🧾", layout="wide")

st.title("🧾 Generador de Cuentas de Cobro")
st.subheader("AIRCRAFT MULTISERVICIOS")

with st.form("formulario_cuenta"):
    st.write("Datos del Cliente")
    cliente_nombre = st.text_input("Nombre del Cliente")
    cliente_cedula = st.text_input("Cédula del Cliente")
    cliente_telefono = st.text_input("Teléfono del Cliente")
    
    st.write("Detalles del Servicio")
    concepto = st.text_area("Concepto / Descripción", height=100)
    valor = st.number_input("Valor a cobrar ($)", min_value=0, step=10000)
    
    submit = st.form_submit_button("Generar Cuenta de Cobro", type="primary")

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
        
        pdf_bytes = generar_pdf_cuenta(datos, numero_actual)
        incrementar_contador(numero_actual)
        
        st.success(f"✅ Cuenta de cobro N° {numero_actual:03d} generada con éxito.")
        
        st.download_button(
            label="⬇️ Descargar Cuenta de Cobro PDF",
            data=pdf_bytes,
            file_name=f"Cuenta_Cobro_{numero_actual:03d}.pdf",
            mime="application/pdf"
    )
