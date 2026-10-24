import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y COLORES
# ==========================================
st.set_page_config(page_title="Facturación - Aircraft Multiservicios", page_icon="📄", layout="wide")

AZUL_CORPORATIVO = colors.HexColor("#1F4E79")
AZUL_BARRA = colors.HexColor("#2E5C8A")
GRIS_FONDO = colors.HexColor("#F2F2F2")
NEGRO = colors.HexColor("#000000")

# ==========================================
# FUNCIÓN PARA DIBUJAR EL PIE DE PÁGINA (FIRMAS)
# ==========================================
def dibujar_pie_pagina(canvas, doc, datos_cliente):
    canvas.saveState()
    
    estilo_texto = ParagraphStyle(
        'TextoPie', parent=getSampleStyleSheet()['Normal'], fontName='Helvetica', fontSize=9, textColor=NEGRO
    )
    
    firma_tecnico = Paragraph("<b>Técnico / Emisor</b><br/>AIRCRAFT MULTISERVICIOS", estilo_texto)
    firma_cliente = Paragraph(f"<b>Firma del Cliente</b><br/>C.C. {datos_cliente['cedula']}", estilo_texto)

    # Creamos una tabla de 3 columnas: [Firma Técnico] [Espacio en blanco] [Firma Cliente]
    # El espacio en blanco mide 1 pulgada, asegurando que se vean separadas.
    tabla_firmas = Table([["", "", ""], [firma_tecnico, "", firma_cliente]], colWidths=[3.0*inch, 1.0*inch, 3.0*inch])
    
    tabla_firmas.setStyle(TableStyle([
        # Línea negra independiente para el técnico (columna 0)
        ('LINEABOVE', (0,0), (0,0), 1, colors.black), 
        # Línea negra independiente para el cliente (columna 2)
        ('LINEABOVE', (2,0), (2,0), 1, colors.black),
        
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,0), 5), # Espacio entre línea y texto
    ]))
    
    ancho_pagina, alto_pagina = letter
    ancho_tabla, alto_tabla = tabla_firmas.wrapOn(canvas, doc.width, doc.height)
    
    y_pos = 1.2 * inch 
    # Centramos la tabla completa en la página
    x_pos = doc.leftMargin + (doc.width - ancho_tabla) / 2
    
    tabla_firmas.drawOn(canvas, x_pos, y_pos)
    canvas.restoreState()

# ==========================================
# FUNCIÓN PARA GENERAR EL PDF
# ==========================================
def generar_pdf(datos_empresa, datos_factura, datos_cliente, items, totales):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=100)
    elements = []
    
    styles = getSampleStyleSheet()
    estilo_subtitulo = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=NEGRO, alignment=1)
    estilo_texto = ParagraphStyle('Texto', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=NEGRO)
    estilo_seccion = ParagraphStyle('Seccion', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=AZUL_CORPORATIVO, spaceAfter=5)

    # --- 1. CABECERA ---
    try:
        logo = Image("logo.png", width=0.9*inch, height=0.9*inch)
    except:
        logo = Paragraph("[Falta logo.png]", estilo_texto)

    # Se ve igual a tu imagen original: Nombre en dos líneas
    texto_empresa = f"""
    <font color="#1F4E79" size="16"><b>{datos_empresa['nombre']}</b></font><br/>
    <font size="8">{datos_empresa['descripcion']}</font><br/>
    <font size="8"><b>NIT:</b> {datos_empresa['nit']}</font><br/>
    <font size="8"><b>Teléfono:</b> {datos_empresa['telefono']}</font><br/>
    <font size="8"><b>Correo:</b> {datos_empresa['correo']}</font>
    """
    col_empresa = Paragraph(texto_empresa, estilo_texto)

    info_factura = f"""
    <font size="12"><b>FACTURA DE VENTA</b></font><br/><br/>
    <font size="9">Número: <b>{datos_factura['numero']}</b></font><br/>
    <font size="9">Fecha: <b>{datos_factura['fecha']}</b></font>
    """
    col_factura = Paragraph(info_factura, estilo_subtitulo)
    
    tabla_cabecera = Table([[logo, col_empresa, col_factura]], colWidths=[1.0*inch, 4.0*inch, 2.5*inch])
    tabla_cabecera.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (2,0), (2,0), 1, AZUL_CORPORATIVO),
        ('ALIGN', (2,0), (2,0), 'CENTER'),
        ('TOPPADDING', (2,0), (2,0), 10),
        ('BOTTOMPADDING', (2,0), (2,0), 10),
    ]))
    elements.append(tabla_cabecera)
    elements.append(Spacer(1, 20))

    # --- 2. DATOS DEL CLIENTE Y FACTURA (CORREGIDO CON ESPACIO EN BLANCO) ---
    texto_cliente = f"""
    <font color="#1F4E79"><b>DATOS DEL CLIENTE</b></font><br/>
    <font size="9">Nombre: {datos_cliente['nombre']}</font><br/>
    <font size="9">NIT/CC: {datos_cliente['cedula']}</font><br/>
    <font size="9">Teléfono: {datos_cliente['telefono']}</font><br/>
    <font size="9">Dirección: {datos_cliente['direccion']}</font>
    """
    col_cliente = Paragraph(texto_cliente, estilo_texto)

    texto_pago = f"""
    <font color="#1F4E79"><b>INFORMACIÓN DE PAGO</b></font><br/>
    <font size="9">Método: {datos_factura['metodo_pago']}</font><br/>
    <font size="9">Estado: Pagado</font><br/>
    """
    col_pago = Paragraph(texto_pago, estilo_texto)

    # Agregamos una columna central vacía ("") de 0.3 pulgadas para separar los recuadros
    # Los recuadros pasan a medir 3.6 pulgadas cada uno (3.6 + 0.3 + 3.6 = 7.5 total)
    tabla_datos = Table([[col_cliente, "", col_pago]], colWidths=[3.6*inch, 0.3*inch, 3.6*inch])
    
    tabla_datos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), GRIS_FONDO), # Fondo gris cliente
        ('BACKGROUND', (2,0), (2,0), GRIS_FONDO), # Fondo gris pago
        ('LINEBEFORE', (0,0), (0,0), 3, AZUL_BARRA), # Barra azul cliente
        ('LINEBEFORE', (2,0), (2,0), 3, AZUL_BARRA), # Barra azul pago
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(tabla_datos)
    elements.append(Spacer(1, 20))

    # --- 3. TABLA DE ITEMS ---
    elements.append(Paragraph("DETALLE DE LA FACTURA", estilo_seccion))
    
    data_items = [["Cant.", "Descripción", "V. Unitario", "Total"]]
    
    for item in items:
        data_items.append([
            str(item['cantidad']), 
            item['descripcion'], 
            f"${item['precio_unitario']:,.2f}", 
            f"${item['total']:,.2f}"
        ])
    
    data_items.append(["", "", "Subtotal:", f"${totales['subtotal']:,.2f}"])
    data_items.append(["", "", "IVA (19%):", f"${totales['iva']:,.2f}"])
    data_items.append(["", "", "TOTAL:", f"${totales['total']:,.2f}"])

    tabla_items = Table(data_items, colWidths=[0.6*inch, 4.3*inch, 1.2*inch, 1.4*inch])
    tabla_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_CORPORATIVO),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-4), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('LINEBELOW', (0,0), (-1,-4), 0.5, colors.grey),
        ('LINEABOVE', (0,-3), (-1,-3), 1, AZUL_CORPORATIVO),
        ('FONTNAME', (2,-3), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (2,-1), (-1,-1), 11),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(tabla_items)

    # --- 4. CONSTRUCCIÓN DEL PDF CON EL PIE DE PÁGINA ---
    def on_page(canvas, doc):
        dibujar_pie_pagina(canvas, doc, datos_cliente)

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFAZ DE STREAMLIT
# ==========================================
st.title("📄 Generador de Facturas - Aircraft Multiservicios")

datos_empresa = {
    "nombre": "AIRCRAFT MULTISERVICIOS",
    "descripcion": "SISTEMAS DE CLIMATIZACIÓN Y REFRIGERACIÓN",
    "nit": "1087200869",
    "telefono": "+57 302 681 2764",
    "correo": "aircraftmultiservicios30@gmail.com"
}

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos del Cliente")
        cliente_nombre = st.text_input("Nombre del Cliente", "Fernando Mendez")
        cliente_cedula = st.text_input("NIT / Cédula", "1087202958")
        cliente_telefono = st.text_input("Teléfono", "3186919844")
        cliente_direccion = st.text_input("Dirección", "Cl. 14 #6a-74 a 6a-118")
    with col2:
        st.subheader("Datos de la Factura")
        factura_numero = st.text_input("Número de Factura", "#F-001")
        factura_fecha = st.date_input("Fecha", datetime.now())
        metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Tarjeta"])

st.subheader("Ítems de la Factura")
if "factura_items" not in st.session_state:
    st.session_state.factura_items = [{"cantidad": 1, "descripcion": "Mantenimiento preventivo aire acondicionado", "precio_unitario": 150000.0}]

def agregar_item():
    st.session_state.factura_items.append({"cantidad": 1, "descripcion": "", "precio_unitario": 0.0})

def eliminar_item(index):
    st.session_state.factura_items.pop(index)

for i, item in enumerate(st.session_state.factura_items):
    c1, c2, c3, c4 = st.columns([1, 4, 2, 1])
    item['cantidad'] = c1.number_input("Cant.", min_value=1, value=item['cantidad'], key=f"qty_{i}")
    item['descripcion'] = c2.text_input("Descripción", value=item['descripcion'], key=f"desc_{i}")
    item['precio_unitario'] = c3.number_input("V. Unitario", min_value=0.0, value=item['precio_unitario'], step=1000.0, key=f"price_{i}")
    item['total'] = item['cantidad'] * item['precio_unitario']
    c4.write(" ")
    c4.write(" ")
    if c4.button("❌", key=f"del_{i}"):
        eliminar_item(i)
        st.rerun()

col_btn1, col_btn2 = st.columns([1, 5])
col_btn1.button("➕ Agregar Ítem", on_click=agregar_item)

subtotal = sum(item['total'] for item in st.session_state.factura_items)
iva = subtotal * 0.19
total = subtotal + iva

st.markdown(f"### Subtotal: ${subtotal:,.2f} | IVA (19%): ${iva:,.2f} | **Total: ${total:,.2f}**")

if st.button("📥 Generar y Descargar PDF", type="primary"):
    datos_cliente = {
        "nombre": cliente_nombre,
        "cedula": cliente_cedula,
        "telefono": cliente_telefono,
        "direccion": cliente_direccion
    }
    datos_factura = {
        "numero": factura_numero,
        "fecha": factura_fecha.strftime("%d de %B, %Y"),
        "metodo_pago": metodo_pago
    }
    totales = {
        "subtotal": subtotal,
        "iva": iva,
        "total": total
    }
    
    pdf_buffer = generar_pdf(datos_empresa, datos_factura, datos_cliente, st.session_state.factura_items, totales)
    
    st.download_button(
        label="⬇️ Descargar Factura en PDF",
        data=pdf_buffer,
        file_name=f"Factura_{factura_numero.replace('#', '')}.pdf",
        mime="application/pdf"
    )
    st.success("¡PDF generado con éxito! Haz clic en el botón de arriba para descargar.")
