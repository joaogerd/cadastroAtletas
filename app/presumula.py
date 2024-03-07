from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# Conversão de centímetros para pontos (1 cm = 28.35 pontos)
def cm_para_pontos(cm):
    return cm * 28.35

# Função para criar estilo de célula sombreada
def shaded_cell():
    return TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
                       ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                       ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                       ('FONT', (0,0), (-1,-1), 'Helvetica', 12)])

# Função para criar estilo de célula normal
def normal_cell():
    return TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                       ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                       ('FONT', (0,0), (-1,-1), 'Helvetica', 12)])

# Função para criar estilo estilo Excel
def excel_style():
    return TableStyle([
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10)
    ])

# Função para adicionar tabela ao canvas
def add_table(canvas, x, y, data, style, colWidths):
    table = Table(data, colWidths=colWidths, rowHeights=altura_linha)
    table.setStyle(style)
    table.wrapOn(canvas, width, height)
    table.drawOn(canvas, x, y)

# Definindo os parâmetros iniciais (em centímetros)
altura_linha_cm = 0.75  # Altura de cada linha da tabela
espaco_cm = 0.25       # Espaço entre as tabelas
margem_x_cm = 1.5      # Margem lateral
margem_topo_cm = 2     # Margem superior
largura_coluna1_cm = 2  # Largura da primeira coluna da tabela de jogadores
largura_coluna2_cm = 16 # Largura da segunda coluna da tabela de jogadores

# Conversão de parâmetros para pontos
altura_linha = cm_para_pontos(altura_linha_cm)
espaco = cm_para_pontos(espaco_cm)
margem_x = cm_para_pontos(margem_x_cm)
margem_topo = cm_para_pontos(margem_topo_cm)
largura_coluna1 = cm_para_pontos(largura_coluna1_cm)
largura_coluna2 = cm_para_pontos(largura_coluna2_cm)

# Criando um novo canvas
c = canvas.Canvas('Final_Futsal_Scoresheet.pdf', pagesize=A4)
width, height = A4  # Dimensões da página

Start_y = height - margem_topo

# Adicionando cabeçalho
header = [['PRÉ-SÚMULA']]
add_table(c, x=margem_x, y = Start_y, data=header, style=shaded_cell(), colWidths=[width - 2 * margem_x])

# Adicionando a seção de categoria
categoria_y = Start_y - 2 * altura_linha 
add_table(c, x=margem_x, y=categoria_y, data=[['Categoria', '']], style=shaded_cell(), colWidths=[largura_coluna1, largura_coluna2])

# Adicionando a tabela de jogadores
athletes=15
players_table_data = [['Nº', 'Nome do Atleta']] + [['', ''] for _ in range(athletes)]
athletes_y = categoria_y - (1+len(players_table_data)) * altura_linha


add_table(c, x=margem_x, y=athletes_y, data=players_table_data, style=excel_style(), colWidths=[largura_coluna1, largura_coluna2])

# Adicionando as posições de equipe técnica
positions_data = [['REPRESENTANTE:', ''], ['TÉCNICO:', ''], ['MASSAGISTA:', ''], ['PREP. FÍSICO:', '']]
technic_team_y = athletes_y - (1+len(positions_data))*altura_linha

add_table(c, x=margem_x, y=technic_team_y, data=positions_data, style=normal_cell(), colWidths=[largura_coluna1, largura_coluna2])

# Salvando o PDF
c.save()

print('PDF gerado com sucesso: Final_Futsal_Scoresheet.pdf')


