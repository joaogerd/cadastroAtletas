from reportlab.lib import pagesizes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image

def create_authorization_form(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Estrutura da tabela com mesclagem de colunas
    data = [
        ["EU"],
        ["RESIDENTE"],
        ["AUTORIZO O MENOR"],
        ["PORTADOR DO R.G. nº:", "NASCIDO EM DATA DE _______/_______/_______"],
        ["A PARTICIPAR DAS COMPETIÇÕES PROMOVIDAS PELA LPF, DENTRO DOS TERMOS REGULAMENTADOS."]
    ]

    # Criação da tabela com mesclagem de colunas
    line_tickness=0.5
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

    # Adicionando uma imagem no cabeçalho
    image_path = 'header_liga.png'
    largura_imagem, altura_imagem = get_image_size(image_path)
    x = (width - (largura_imagem*0.25)) / 2
    y = height - (altura_imagem*.25) -10 # Ajuste '100' para mudar a distância do topo da página
    c.drawImage(image_path, x, y, largura_imagem*0.25, altura_imagem*0.25)

    # Configurando os estilos
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']

    # Adicionando o texto "AUTORIZAÇÃO DO ATLETA"
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 125, "AUTORIZAÇÃO DO ATLETA")

    # Adicionando o ano "2024" em negrito e sublinhado
    c.setFont("Helvetica", 24)
    text_2024 = "2024"
    text_width = c.stringWidth(text_2024, "Helvetica", 24)
    c.drawCentredString(width / 2, height - 165, text_2024)
    c.line((width - text_width) / 2, height - 167, (width + text_width) / 2, height - 167)  # Linha de sublinhado


    # Desenha a tabela no canvas
    table.wrapOn(c, width, height)
    table.drawOn(c, 45, height - 400)

    # Texto da assinatura centralizado
    signature_text = "ASSINATURA DO RESPONSÁVEL"
    recognition_text = "RECONHECIMENTO FIRMA"
    signature_width = c.stringWidth(signature_text, "Helvetica", 10)

    # Coordenadas para a linha de assinatura
    x_start = (width/2) - signature_width*0.65
    x_end = (width/2) + signature_width*0.65
    y_position = height - 525
    # Desenha a linha para a assinatura
    c.line(x_start, y_position, x_end, y_position)

    # Escreve o texto da assinatura centralizado
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 545, signature_text)
    c.drawCentredString(width / 2, height - 565, recognition_text)

    # Rodapé centralizado
    footer_text1 = "LIGA PAULISTA FUTSAL"
    footer_text2 = "CNPJ/MF 16.640.323-0001/80"
    footer_text3 = "RUA BORGES DE FIGUEIREDO, 303 - SALA 522 – MOOCA – CEP. 03110-010 SÃO PAULO- SP"
    
    c.setFont("Helvetica-Bold", 8)
    voffset=35
    c.drawCentredString(width / 2, 50+voffset, footer_text1)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 40+voffset, footer_text2)
    c.drawCentredString(width / 2, 30+voffset, footer_text3)

    # Finaliza o documento
    c.save()
def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size  # Retorna uma tupla (largura, altura)
# Nome do arquivo PDF a ser gerado
create_authorization_form("autorizacao_lpf.pdf")

