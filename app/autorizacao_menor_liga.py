import os
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from .paths import path

def get_image_size(image_path):
    """
    Get the size of an image.

    Args:
        image_path (str): The file path of the image.

    Returns:
        tuple: Width and height of the image.
    """
    with Image.open(image_path) as img:
        return img.size  

def add_header(canvas, width, height):
    """
    Add a header to the canvas, including an image and title text.

    Args:
        canvas (Canvas): The canvas of the PDF document.
        width (int): Width of the PDF document.
        height (int): Height of the PDF document.
    """
    # Adding an image to the header
    image_path = os.path.join(path.logos,'header_liga.png')
    if os.path.exists(image_path):
        image_width, image_height = get_image_size(image_path)
        x = (width - (image_width * 0.25)) / 2
        y = height - (image_height * 0.25) - 10 
        canvas.drawImage(image_path, x, y, image_width * 0.25, image_height * 0.25)
    else:
        print("Image not found:", image_path)

    # Adding the "AUTHORIZATION OF ATHLETE" text
    canvas.setFont("Helvetica", 12)
    canvas.drawCentredString(width / 2, height - 125, "AUTORIZAÇÃO DO ATLETA")

    # Adding the year "2024" in bold and underlined
    canvas.setFont("Helvetica", 24)
    text_2024 = "2024"
    text_width = canvas.stringWidth(text_2024, "Helvetica", 24)
    canvas.drawCentredString(width / 2, height - 165, text_2024)
    canvas.line((width - text_width) / 2, height - 167, (width + text_width) / 2, height - 167)

def add_footer(canvas, width):
    """
    Add a footer to the canvas.

    Args:
        canvas (Canvas): The canvas of the PDF document.
        width (int): Width of the PDF document.
    """
    # Centralized footer
    footer_text1 = "LIGA PAULISTA FUTSAL"
    footer_text2 = "CNPJ/MF 16.640.323-0001/80"
    footer_text3 = "RUA BORGES DE FIGUEIREDO, 303 - SALA 522 – MOOCA – CEP. 03110-010 SÃO PAULO- SP"
    
    voffset = 35
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(width / 2, 50 + voffset, footer_text1)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(width / 2, 40 + voffset, footer_text2)
    canvas.drawCentredString(width / 2, 30 + voffset, footer_text3)


def create_styled_text(text, color='black', bold=False, italic=False, font_size=10):
    """
    Create styled text for ReportLab Paragraph.

    Args:
        text (str): The text to be styled.
        color (str): Text color.
        bold (bool): If True, text will be bold.
        italic (bool): If True, text will be italic.
        font_size (int): Font size of the text.

    Returns:
        str: Styled text in HTML-like format for ReportLab.
    """
    style = ''
    if bold:
        style += '<b>'
    if italic:
        style += '<i>'

    styled_text = f'<font color={color} size={font_size}>{style}{text}</font>'

    if italic:
        styled_text += '</i>'
    if bold:
        styled_text += '</b>'

    return styled_text

def create_table_text(text_parts):
    """
    Combine multiple styled text parts into a single Paragraph.

    Args:
        text_parts (list of tuples): Each tuple contains text and its styles.

    Returns:
        Paragraph: A ReportLab Paragraph object with combined styled texts.
    """
    combined_text = ' '.join([create_styled_text(*part) for part in text_parts])
    return Paragraph(combined_text, ParagraphStyle(name='Normal'))

def create_authorization_table(canvas, data, width, height):
    """
    Create the authorization table on the canvas.

    Args:
        canvas (Canvas): The canvas of the PDF document.
        width (int): Width of the PDF document.
        height (int): Height of the PDF document.
    """

    EU        = create_table_text([('EU', 'black', False, False, 10), (data['responsavelLegal'], 'blue', False, False, 10)])
    RESIDENTE = create_table_text([('RESIDENTE À', 'black'), (f"{data['rua']}, nº {data['numero']}, {data['bairro']}, {data['cidade']} - {data['UF']}", 'blue')])
    AUTORIZO  = create_table_text([('AUTORIZO O MENOR', 'black'), (data['nome'], 'blue')])
    RG        = create_table_text([('PORTADOR DO R.G. nº:','black'),(data['docRG'],'blue')])
    NASC      = create_table_text([('NASCIDO EM DATA DE','black'),(data['dtNascimento'],'blue')])

    data = [
        [EU], [RESIDENTE], [AUTORIZO],
        [RG, NASC],
        ["A PARTICIPAR DAS COMPETIÇÕES PROMOVIDAS PELA LPF, DENTRO DOS TERMOS REGULAMENTADOS."]
    ]

    # Criação da tabela com mesclagem de colunas
    line_tickness = 0.5
    table = Table(data, colWidths=[260, 260], rowHeights=40)
    table.setStyle(TableStyle([
        ('VALIGN',    (0,0), (-1,-1),'MIDDLE'),
        ('BOX',       (0,0), (-1,-1),line_tickness, colors.black),
        ('LINEABOVE', (0,1), (-1, 1),line_tickness, colors.black),
        ('LINEABOVE', (0,2), (-1, 2),line_tickness, colors.black),
        ('LINEABOVE', (0,3), (-1, 3),line_tickness, colors.black),
        ('LINEABOVE', (0,4), (-1, 4),line_tickness, colors.black),
        ('LINEABOVE', (0,5), (-1, 5),line_tickness, colors.black),
        ('SPAN',      (0,0), (-1, 0)),  # Mesclagem para "EU"
        ('SPAN',      (0,1), (-1, 1)),  # Mesclagem para "RESIDENTE"
        ('SPAN',      (0,2), (-1, 2)),  # Mesclagem para "AUTORIZO O MENOR"
        ('SPAN',      (0,4), (-1, 4)),  # Mesclagem para a última linha
    ]))


    table.wrapOn(canvas, width, height)
    table.drawOn(canvas, 45, height - 400)

def add_signature_section(canvas, width, height):
    """
    Add a signature section to the canvas.

    Args:
        canvas (Canvas): The canvas of the PDF document.
        width (int): Width of the PDF document.
        height (int): Height of the PDF document.
    """
    signature_text = "ASSINATURA DO RESPONSÁVEL"
    recognition_text = "RECONHECIMENTO FIRMA"
    signature_width = canvas.stringWidth(signature_text, "Helvetica", 10)

    x_start = (width / 2) - signature_width * 0.65
    x_end = (width / 2) + signature_width * 0.65
    y_position = height - 525

    canvas.line(x_start, y_position, x_end, y_position)
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(width / 2, y_position - 20, signature_text)
    canvas.drawCentredString(width / 2, y_position - 40, recognition_text)

def create_authorization_form(filename, data):
    """
    Create an authorization form as a PDF document.

    Args:
        filename (str): The name of the PDF file to be created.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    add_header(c, width, height)
    create_authorization_table(c, data, width, height)
    add_signature_section(c, width, height)
    add_footer(c, width)

    c.save()

# Generate the PDF file
#create_authorization_form("autorizacao_lpf.pdf")

