from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtGui import QImage, QImageReader

from .AppConfigManager import AppConfigManager
class FutsalPreSumulaGenerator:
    """
    Class to generate a futsal pre-match summary (pre-sumula).

    Args:
        None

    Example Usage:
        generator = FutsalPreSumulaGenerator()
        total_athletes = 15
        athletes = [['', ''] for _ in range(total_athletes)]  # Add up to 15 players
        category_name = "U18 Boys"
        generator.generate_pre_sumula(athletes, category_name)

    """

    def __init__(self):
        """
        Initializes the FutsalPreSumulaGenerator class.

        Args:
            None

        Returns:
            None
        """
        self.config,_ = AppConfigManager().loadConfig()

        # Conversion from centimeters to points (1 cm = 28.35 points)
        self.cm_to_points = lambda cm: cm * 28.35

        # Initial parameters (in centimeters)
        self.line_height_cm = 0.75
        self.space_cm = 0.25
        self.side_margin_cm = 1.5
        self.top_margin_cm = 2
        self.column_width1_cm = 2
        self.column_width2_cm = 16

        # Conversion of parameters to points
        self.line_height = self.cm_to_points(self.line_height_cm)
        self.space = self.cm_to_points(self.space_cm)
        self.side_margin = self.cm_to_points(self.side_margin_cm)
        self.top_margin = self.cm_to_points(self.top_margin_cm)
        self.column_width1 = self.cm_to_points(self.column_width1_cm)
        self.column_width2 = self.cm_to_points(self.column_width2_cm)

        # Page size
        self.width, self.height = A4

    def shaded_cell_style(self, ALIGN='CENTER'):
        """
        Defines a style for shaded cells.

        Args:
            ALIGN (str): The text alignment ('CENTER' by default).

        Returns:
            TableStyle: A TableStyle instance.
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),  # Define a light grey background color for all cells.
            ('ALIGN', (0, 0), (-1, -1), ALIGN),  # Set text alignment for all cells.
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Set vertical alignment to middle for all cells.
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 12)  # Set the font to Helvetica with a size of 12 for all cells.
        ])

    def shaded_cell_with_border_style(self, ALIGN='CENTER'):
        """
        Defines a style for shaded cells with borders.

        Args:
            ALIGN (str): The text alignment ('CENTER' by default).

        Returns:
            TableStyle: A TableStyle instance.
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),  # Define a light grey background color for all cells.
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Draw a black border around all cells.
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Draw inner grid lines within cells.
            ('ALIGN', (0, 0), (-1, -1), ALIGN),  # Set text alignment for all cells.
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Set vertical alignment to middle for all cells.
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 12)  # Set the font to Helvetica with a size of 12 for all cells.
        ])

    def normal_cell_style(self, ALIGN='LEFT'):
        """
        Defines a style for normal cells.

        Args:
            ALIGN (str): The text alignment ('LEFT' by default).

        Returns:
            TableStyle: A TableStyle instance.
        """
        return TableStyle([
            ('ALIGN', (0, 0), (-1, -1), ALIGN),  # Set text alignment for all cells.
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Set vertical alignment to middle for all cells.
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 12)  # Set the font to Helvetica with a size of 12 for all cells.
        ])

    def excel_style(self, ALIGN='LEFT'):
        """
        Defines an Excel-like style for cells.

        Args:
            ALIGN (str): The text alignment ('LEFT' by default).

        Returns:
            TableStyle: A TableStyle instance.
        """
        return TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Draw a black border around all cells.
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Draw inner grid lines within cells.
            ('ALIGN', (0, 0), (-1, -1), ALIGN),  # Set text alignment for all cells.
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Set vertical alignment to middle for all cells.
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10)  # Set the font to Helvetica with a size of 10 for all cells.
        ])

    def add_table(self, canvas, x, y, data, style, colWidths):
        """
        Adds a table to the PDF canvas.

        Args:
            canvas (Canvas): The PDF canvas.
            x (float): The x-coordinate for the table.
            y (float): The y-coordinate for the table.
            data (list): The table data.
            style (TableStyle): The table style.
            colWidths (list): The column widths.

        Returns:
            None
        """
        table = Table(data, colWidths=colWidths, rowHeights=self.line_height)
        table.setStyle(style)
        table.wrapOn(canvas, self.width, self.height)
        table.drawOn(canvas, x, y)
    def generate_pre_sumula(self, athletes, category_name):
        """
        Generates a futsal pre-sumula PDF document.

        Args:
            athletes (list): A list of athlete data, where each element is a list containing athlete information.
            category_name (str): The name of the futsal category.

        Returns:
            None
        """
        # Create a new canvas
        c = canvas.Canvas(f'Final_Futsal_Scoresheet_{category_name}.pdf', pagesize=A4)

        start_y = self.height - self.top_margin

        # Add header
        header = [['Lista de Atletas']]
        self.add_table(c, x=self.side_margin, y=start_y, data=header, style=self.shaded_cell_style(), colWidths=[self.width - 2 * self.side_margin])

        # Add team Name section
        width = self.width*0.6
        team_name_y = start_y - 2 * self.line_height
        team_header = [['Equipe']]
        self.add_table(c, x=self.side_margin, y=team_name_y, data=team_header, style=self.shaded_cell_with_border_style('CENTER'), colWidths=[width])

        team_name_y = team_name_y -  self.line_height
        team_name = [[self.config.nome]]
        self.add_table(c, x=self.side_margin, y=team_name_y, data=team_name, style=self.excel_style('CENTER'), colWidths=[width])

        # Add category section
        width = self.width*0.3
        category_y = team_name_y - 2 * self.line_height
        category_data = [['Categoria']]
        self.add_table(c, x=self.side_margin, y=category_y, data=category_data, style=self.shaded_cell_with_border_style('CENTER'), colWidths=[width])

        category_y = category_y -  self.line_height
        category_data = [[category_name.upper()]]
        self.add_table(c, x=self.side_margin, y=category_y, data=category_data, style=self.excel_style('CENTER'), colWidths=[width])

        # Add Athlete header section
        athlete_header = [['Nº', 'Nome do Atleta']] 
        athlete_header_y = category_y - 2 * self.line_height
        self.add_table(c, x=self.side_margin, y=athlete_header_y, data=athlete_header, style=self.shaded_cell_with_border_style(), colWidths=[self.column_width1, self.column_width2])

        # Add athletes table
        players_table_data = athletes
        athletes_y = athlete_header_y - len(players_table_data) * self.line_height
        self.add_table(c, x=self.side_margin, y=athletes_y, data=players_table_data, style=self.excel_style(), colWidths=[self.column_width1, self.column_width2])

        # Add technical team positions
#        positions_data = [['REPRESENTANTE:', ''], ['TÉCNICO:', ''], ['MASSAGISTA:', ''], ['PREP. FÍSICO:', '']]
#        technic_team_y = athletes_y - (1 + len(positions_data)) * self.line_height
#        self.add_table(c, x=self.side_margin, y=technic_team_y, data=positions_data, style=self.normal_cell_style(), colWidths=[self.column_width1, self.column_width2])

        # Save the PDF
        c.save()
        print(f'PDF generated successfully: Final_Futsal_Scoresheet_{category_name}.pdf')


    def generate_pre_sumula_(self, athletes, category_name):
        """
        Generates a futsal pre-sumula PDF document.

        Args:
            athletes (list): A list of athlete data, where each element is a list containing athlete information.
            category_name (str): The name of the futsal category.

        Returns:
            None
        """
        # Create a new canvas
        c = canvas.Canvas(f'Final_Futsal_Scoresheet_{category_name}.pdf', pagesize=A4)

        start_y = self.height - self.top_margin

        # Add header
        header = [['PRÉ-SÚMULA']]
        self.add_table(c, x=self.side_margin, y=start_y, data=header, style=self.shaded_cell_style(), colWidths=[self.width - 2 * self.side_margin])

        # Add team Name section
        width = self.width*0.6
        team_name_y = start_y - 2 * self.line_height
        team_header = [['Equipe']]
        self.add_table(c, x=self.side_margin, y=team_name_y, data=team_header, style=self.shaded_cell_with_border_style('CENTER'), colWidths=[width])

        team_name_y = team_name_y -  self.line_height
        team_name = [[self.config.nome]]
        self.add_table(c, x=self.side_margin, y=team_name_y, data=team_name, style=self.excel_style('CENTER'), colWidths=[width])

        # Add category section
        width = self.width*0.3
        category_y = team_name_y - 2 * self.line_height
        category_data = [['Categoria']]
        self.add_table(c, x=self.side_margin, y=category_y, data=category_data, style=self.shaded_cell_with_border_style('CENTER'), colWidths=[width])

        category_y = category_y -  self.line_height
        category_data = [[category_name.upper()]]
        self.add_table(c, x=self.side_margin, y=category_y, data=category_data, style=self.excel_style('CENTER'), colWidths=[width])

        # Add Athlete header section
        athlete_header = [['Nº', 'Nome do Atleta']] 
        athlete_header_y = category_y - 2 * self.line_height
        self.add_table(c, x=self.side_margin, y=athlete_header_y, data=athlete_header, style=self.shaded_cell_with_border_style(), colWidths=[self.column_width1, self.column_width2])

        # Add athletes table
        players_table_data = athletes
        athletes_y = athlete_header_y - len(players_table_data) * self.line_height
        self.add_table(c, x=self.side_margin, y=athletes_y, data=players_table_data, style=self.excel_style(), colWidths=[self.column_width1, self.column_width2])

        # Add technical team positions
        positions_data = [['REPRESENTANTE:', ''], ['TÉCNICO:', ''], ['MASSAGISTA:', ''], ['PREP. FÍSICO:', '']]
        technic_team_y = athletes_y - (1 + len(positions_data)) * self.line_height
        self.add_table(c, x=self.side_margin, y=technic_team_y, data=positions_data, style=self.normal_cell_style(), colWidths=[self.column_width1, self.column_width2])

        # Save the PDF
        c.save()
        print(f'PDF generated successfully: Final_Futsal_Scoresheet_{category_name}.pdf')

      
# Example usage
if __name__ == "__main__":
    generator = FutsalPreSumulaGenerator()
    total_athletes = 15
    athletes = [['', ''] for _ in range(total_athletes)]  # Add up to 15 players
    category_name = "U18 Boys"
    generator.generate_pre_sumula(athletes, category_name)
    generator.visualize_pdf('Final_Futsal_Scoresheet.pdf')
