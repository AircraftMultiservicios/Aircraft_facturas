import streamlit as st
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- CONFIGURACIÓN DE LA EMPRESA ---
NOMBRE_EMPRESA = "AIRCRAFT MULTISERVICIOS"
SLOGAN = "SISTEMAS DE CLIMATIZACION Y REFRIGERACION"
NIT = "1087200869"
TELEFONO = "+57 302 681 2764"
CORREO = "aircraftmultiservicios30@gmail.com"
ARCHIVO_CONTADOR = "contador_cotizaciones.txt"

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
def generar_pdf_cotizacion(items, total_neto, numero_cot):
    ruta_pdf = "cotizacion_temp.pdf"
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter

    # --- ENCABEZADO IZQUIERDO ---
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    try:
        if os.path.exists(ruta_logo):
            c.drawImage(ruta_logo, 40, height - 80, width=60, preserveAspectRatio=True)
    except:
        pass

    # Datos Empresa
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#1e50b4")) # Azul
    c.drawString(40, height - 110, "AIRCRAFT")
    c.drawString(40, height - 125, "MULTISERVICIOS")
    
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.black)
    c.drawString(40, height - 135, SLOGAN)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(40, height - 145, f"NIT: {NIT}")
    c.setFont("Helvetica", 7)
    c.drawString(40, height - 153, f"Telefono: {TELEFONO}")
    c.drawString(40, height - 161, f"Correo: {CORREO}")

    # --- RECUADRO DERECHO (COTIZACIÓN) ---
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(1)
    c.rect(width - 240, height - 140, 200, 90) # Caja gris
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width - 140, height - 65, "COTIZACION")
    
    c.setStrokeColor(colors.HexColor("#1e50b4"))
    c.setLineWidth(2)
    c.line(width - 230, height - 75, width - 50, height - 75)
    
    c.setFont("Helvetica", 8)
    c.drawCentredString(width - 140, height - 90, f"Numero: #2026-{numero_cot:03d}")
    
    fecha_actual = datetime.now().strftime("%d de %B, %Y")
    meses = {"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril", "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto", "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"}
    for k, v in meses.items():
        fecha_actual = fecha_actual.replace(k, v)
    c.drawCentredString(width - 140, height - 105, f"Fecha: {fecha_actual}")
    c.drawCentredString(width - 140, height - 120, "Validez: 15 dias calendario")

    # --- TÍTULO TABLA ---
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(40, height - 190, "DETALLE DEL PRESUPUESTO")

    # --- TABLA DE ITEMS CON REPORTLAB ---
    # Encabezados
    data = [["ITEM", "DESCRIPCION DEL MATERIAL / SERVICIO", "CANT.", "UNIDAD", "UNITARIO", "TOTAL"]]
    
    # Filas
    for i, item in enumerate(items, start=1):
        # Limpiamos acentos
        texto_limpio = item['descripcion'].replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
        lineas = [l.strip().lstrip('-').strip() for l in texto_limpio.split('\n') if l.strip()]
        
        # ReportLab acepta saltos de línea usando <br/> en formato Paragraph
        # Pero para mantenerlo simple, unimos con saltos de línea normales
        texto_celda = "\n".join([f"- {l}" for l in lineas])
        
        precio_str = f"${item['precio']:,.0f}".replace(",", ".")
        total_str = f"${item['total']:,.0f}".replace(",", ".")
        
        data.append([
            str(i), 
            texto_celda, 
            str(item['cantidad']), 
            item['unidad'], 
            precio_str, 
            total_str
        ])

    # Crear la tabla
    # Anchos: ITEM(30), DESCRIPCION(260), CANT(40), UNIDAD(50), UNITARIO(70), TOTAL(70)
    tabla = Table(data, colWidths=[35, 250, 40, 55, 65, 70])
    
    # Estilos de la tabla
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e50b4")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'), # Num item
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'), # Descripcion
        ('FONTNAME', (2, 1), (-1, -1), 'Helvetica'), # Resto
        
        ('ALIGN', (0, 1), (0, -1), 'CENTER'), # Centrar items
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),   # Alinear izq descripcion
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),# Centrar cant, unidad
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'), # Alinear der precios
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Centrado vertical
        
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (1, 1), (1, -1), 10), # Margen para la descripción
    ])
    tabla.setStyle(estilo_tabla)
    
    # Dibujar la tabla en el PDF
    ancho_tabla, alto_tabla = tabla.wrapOn(c, width, height)
    tabla.drawOn(c, 40, height - 210 - alto_tabla) # Ajuste de posición

    # --- TOTALES ---
    # Calculamos dónde quedó la tabla para poner los totales abajo
    y_totales = height - 220 - alto_tabla 
    
    # Recuadro de totales a la derecha
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setFont("Helvetica", 8)
    
    # Subtotal
    c.drawString(width - 200, y_totales - 10, "Subtotal:")
    c.drawRightString(width - 50, y_totales - 10, f"${total_neto:,.0f}".replace(",", "."))
    c.line(width - 210, y_totales - 15, width - 40, y_totales - 15)
    
    # IVA
    c.drawString(width - 200, y_totales - 25, "Impuestos (IVA 0%):")
    c.drawRightString(width - 50, y_totales - 25, "$0")
    c.line(width - 210, y_totales - 30, width - 40, y_totales - 30)
    
    # Total
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.drawString(width - 200, y_totales - 40, "Total Neto:")
    c.drawRightString(width - 50, y_totales - 40, f"${total_neto:,.0f}".replace(",", "."))
    c.line(width - 210, y_totales - 45, width - 40, y_totales - 45)

    # --- CONDICIONES COMERCIALES ---
    # Fondo gris de condiciones
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(40, 80, width - 80, 80, fill=1, stroke=0)
    
    # Barra azul izquierda
    c.setFillColor(colors.HexColor("#1e50b4"))
    c.rect(40, 80, 4, 80, fill=1, stroke=0)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 145, "CONDICIONES COMERCIALES")
    
    c.setFont("Helvetica", 7)
    condiciones = [
        ("- Forma de Pago:", "Anticipo establecido para la compra de materiales y saldo restante contra entrega a satisfaccion de los trabajos realizados."),
        ("- Tiempo de Ejecucion:", "A convenir y programar de manera conjunta tras la confirmacion formal del servicio."),
        ("- Garantia:", "Aplica garantia sobre el servicio tecnico y la mano de obra especializada brindada."),
        ("- Exclusiones:", "No se contemplan obras civiles mayores, resanes de pintura profundos ni acometidas electricas externas al alcance mencionado.")
    ]
    
    y_texto = 135
    for titulo, texto in condiciones:
        c.setFont("Helvetica-Bold", 7)
        c.drawString(50, y_texto, titulo)
        c.setFont("Helvetica", 7)
        c.drawString(120, y_texto, texto) # Texto alineado a la derecha del título
        y_texto -= 12

    c.save()
    
    # Leer el PDF generado y devolverlo como bytes
    with open(ruta_pdf, "rb") as f:
        pdf_bytes = f.read()
    os.remove(ruta_pdf) # Borrar el archivo temporal
    
    return pdf_bytes

# --- INTERFAZ GRÁFICA (STREAMLIT) ---
st.set_page_config(page_title="Cotizador - AIRCRAFT", page_icon="❄️", layout="wide")

st.title("❄️ Generador de Cotizaciones")
st.subheader("AIRCRAFT MULTISERVICIOS")

if 'items_cotizacion' not in st.session_state:
    st.session_state.items_cotizacion = []

st.write("### Añadir Material o Servicio")

with st.form("form_item", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([4, 1, 1, 2])
    with col1:
        desc = st.text_area("Descripción (Dale 'Enter' para separar cada ítem)", height=100, placeholder="Rollo de tubería de cobre 1/2\nRollo de tubería de cobre 1/8")
    with col2:
        cant = st.number_input("Cant.", min_value=1, step=1)
    with col3:
        unidad = st.selectbox("Unidad", ["Global", "Servicio", "Und", "Metro", "Caja"])
    with col4:
        precio = st.number_input("Precio Unitario ($)", min_value=0, step=1000)
    
    agregar = st.form_submit_button("➕ Añadir a la cotización", type="primary")

if agregar:
    if desc:
        total_item = cant * precio
        st.session_state.items_cotizacion.append({
            "descripcion": desc, 
            "cantidad": cant, 
            "unidad": unidad,
            "precio": precio,
            "total": total_item
        })
    else:
        st.error("Escribe una descripción.")

if st.session_state.items_cotizacion:
    st.write("### Ítems agregados")
    total_general = 0
    
    for i, item in enumerate(st.session_state.items_cotizacion):
        total_general += item['total']
        desc_web = item['descripcion'].replace('\n', ' | ')
        if len(desc_web) > 80: desc_web = desc_web[:80] + "..."
        st.write(f"**{i+1}.** {desc_web} — *{item['cantidad']} {item['unidad']} x ${item['precio']:,.0f}* = **${item['total']:,.0f}**")
    
    st.write(f"## Total Neto: ${total_general:,.0f}")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Borrar todo"):
            st.session_state.items_cotizacion = []
            st.rerun()
            
    with col_btn2:
        if st.button("Generar Cotización PDF", type="primary"):
            numero_actual = obtener_siguiente_numero()
            
            # Generar PDF con ReportLab
            pdf_bytes = generar_pdf_cotizacion(st.session_state.items_cotizacion, total_general, numero_actual)
            incrementar_contador(numero_actual)
            
            st.success("✅ PDF Generado con éxito.")
            st.download_button(
                label="⬇️ Descargar Cotización PDF",
                data=pdf_bytes,
                file_name=f"Cotizacion_{numero_actual:03d}.pdf",
                mime="application/pdf"
            )
else:
    st.info("Aún no has agregado ítems a la cotización.")
