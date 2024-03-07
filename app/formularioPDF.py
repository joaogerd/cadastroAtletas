from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from io import BytesIO
from PIL import Image
import yaml


class FormularioPDF:
    """
    A class for creating PDF forms using the ReportLab library.

    Attributes:
        canvas (Canvas): A ReportLab Canvas instance for drawing the form.
        cm_to_points (float): Conversion factor from centimeters to points.

    Methods:
        set_styles: Sets default styles for form elements.
        draw_labeled_rectangle: Draws a rectangle with a label.
        draw_checkboxes_dynamic: Draws a series of dynamic checkboxes.
        draw_labeled_rectangle_with_checkboxes: Draws a rectangle with checkboxes.
        create_form_block: Creates a block of form fields.
    """

    def __init__(self, file_name, papersize=A4):
        """
        Initializes a new instance of the FormularioPDF class.
    
        This constructor sets up the canvas for the PDF and initializes default values for various properties 
        like the page size and conversion factor from centimeters to points.
    
        Args:
            file_name (str): The name of the PDF file to be created.
            papersize (tuple, optional): The size of the pages in the PDF. Defaults to A4.
        """

        self.canvas = Canvas(file_name, pagesize=papersize)
        self.papersize = papersize
        self.width, self.height = papersize
        self.cm_to_points = 28.35  # 1 cm = 28.35 points
        self.set_styles()


    def set_styles(self, line_color="#000000", label_color="#000000", line_width=1,font_name="Helvetica", font_size=10,
                   inner_label_color="#3465a4", inner_font_name="Helvetica",inner_font_size=10,
                   corner_radius=5, line_height=0.9, field_height=0.7, 
                   checkbox_size=10, checkmark_label_color="#3465a4", checkmark_font_name="Helvetica", checkmark_font_size=14 ):
        """
        Sets default styles for form elements.

        Args:
            label_color (str, optional): Hexadecimal color for label text. Defaults to "#000000".
            line_color (str, optional): Hexadecimal color for line and rectangles. Defaults to "#3465a4".
            font_name (str, optional): Font name for text. Defaults to "Helvetica".
            font_size (int, optional): Font size for text. Defaults to 10.
            corner_radius (int, optional): Corner radius for rounded rectangles. Defaults to 5.
            line_height (float, optional): Height of lines in cm. Defaults to 0.9.
            field_height (float, optional): Height of fields in cm. Defaults to 0.7.
        """

        self.label_color   = label_color
        self.font_name     = font_name
        self.font_size     = font_size

        self.inner_label_color = inner_label_color
        self.inner_font_name   = inner_font_name
        self.inner_font_size   = inner_font_size

        self.line_color    = line_color
        self.line_width    = line_width
        self.corner_radius = corner_radius

        self.line_height   = line_height * self.cm_to_points  # Espaçamento entre as linhas
        self.field_height  = field_height * self.cm_to_points  # Altura do campo

        self.checkbox_size        = checkbox_size
        self.checkmark_label_color= checkmark_label_color
        self.checkmark_font_name  = checkmark_font_name
        self.checkmark_font_size  = checkmark_font_size
        

    def set_default_values(self, **kwargs):
        """
        Set default values for optional keyword arguments.
    
        Args:
            **kwargs: Optional keyword arguments and their default values.
    
                label_color (str, optional): The color of the label text. Defaults to the instance's label_color.
                line_color (str, optional): The color of the rectangle's line. Defaults to the instance's line_color.
                font_name (str, optional): The font name for the label text. Defaults to the instance's font_name.
                font_size (int, optional): The font size for the label text. Defaults to the instance's font_size.
                corner_radius (int, optional): The corner radius for the rectangle. Defaults to the instance's corner_radius.
                line_height (float, optional): Height of lines in cm. Defaults to 0.9 cm.
                field_height (float, optional): Height of fields in cm. Defaults to 0.7 cm.
    
        Returns:
            dict: A dictionary containing the default values for each optional argument.
        """
        defaults = {
            'label_color': self.label_color,
            'font_name': self.font_name,
            'font_size': self.font_size,

            'line_color': self.line_color,
            'line_height': self.line_height,  # Default height in points
            'line_width': self.line_width,

            'inner_label_color': self.inner_label_color,
            'inner_font_name': self.inner_font_name,
            'inner_font_size': self.inner_font_size,

            'corner_radius': self.corner_radius,
            'field_height': self.field_height,  # Default field height in points

            'checkbox_size': self.checkbox_size,
            'checkmark_label_color': self.checkmark_label_color,
            'checkmark_font_name': self.checkmark_font_name,
            'checkmark_font_size': self.checkmark_font_size
        }
        
        # Update defaults with provided values, convert line_height and field_height to points if provided
        for key, value in kwargs.items():
            if value is not None:
                if key in ['line_height', 'field_height']:
                    defaults[key] = value * self.cm_to_points
                else:
                    defaults[key] = value
        
        return defaults

    def draw_rectangle(self, x, y, width, height, line_color, corner_radius, fill=1, line_width=1):
        """
        Draws a rectangle with rounded corners.
    
        Args:
            x (float): The x-coordinate of the rectangle's lower-left corner.
            y (float): The y-coordinate of the rectangle's lower-left corner.
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            line_color (str): Hexadecimal color code for the rectangle's border.
            corner_radius (float): The radius of the corners for rounded rectangle.
            fill (int, optional): Flag to specify whether to fill the rectangle. Defaults to 1 (filled).
            line_width (float, optional): The width of the line for the rectangle's border. Defaults to 1.
    
        """
        canvas = self.canvas
        canvas.setLineWidth(line_width)
        canvas.setFillColor(HexColor("#FFFFFF"))
        canvas.setStrokeColor(HexColor(line_color))
        canvas.roundRect(x, y, width, height, radius=corner_radius, stroke=1, fill=fill)
                    
    def draw_label(self, x, y, width, height, label_text, label_color, font_name, font_size):
        """
        Draws a label on the canvas.
    
        Args:
            x (float): The x-coordinate for the label's position.
            y (float): The y-coordinate for the label's position.
            width (float): The width of the area where the label should be centered.
            height (float): The height of the area where the label should be placed.
            label_text (str): The text of the label.
            label_color (str): Hexadecimal color code for the label's text.
            font_name (str): The name of the font for the label's text.
            font_size (float): The size of the font for the label's text.
    
        """
        canvas = self.canvas
        label_width, label_height = canvas.stringWidth(label_text, font_name, font_size), font_size
        label_x = x + (width - label_width) / 2.0
        label_y = y + height - label_height*0.5
    
        # Draw the white rectangle for the text
        canvas.setFillColor(HexColor("#FFFFFF"))
        canvas.rect(label_x, label_y, label_width, label_height, stroke=0, fill=1)
    
        # Draw the label
        canvas.setFillColor(HexColor(label_color))
        canvas.setFont(font_name, font_size)
        canvas.drawString(label_x, label_y, label_text)

    def draw_inner_text(self, x, y, width, height, inner_text, inner_label_color, inner_font_name, inner_font_size, line_height):
        """
        Draws inner text inside a rectangle, supporting line breaks.
    
        Args:
            x (float): The x-coordinate of the inner text's starting position.
            y (float): The y-coordinate of the inner text's starting position.
            width (float): The width of the area for the inner text.
            height (float): The height of the area for the inner text.
            inner_text (str): The actual text to be drawn inside the rectangle.
            inner_label_color (str): Hexadecimal color code for the inner text.
            inner_font_name (str): The name of the font for the inner text.
            inner_font_size (float): The size of the font for the inner text.
            line_height (float): The height of each line of text.
    
        """
        canvas = self.canvas
        inner_lines = inner_text.split('\\n')
        num_lines = len(inner_lines)
        total_text_height = num_lines * inner_font_size + (num_lines - 1) * (0.25*line_height)
    
        inner_text_y = y + (height - total_text_height) / 2 + (num_lines - 1) * (inner_font_size + (0.25*self.line_height))
        for line in inner_lines:
            inner_text_width = canvas.stringWidth(line, inner_font_name, inner_font_size)
            inner_text_x = x + (width - inner_text_width) / 2.0
    
            canvas.setFillColor(HexColor(inner_label_color))
            canvas.setFont(inner_font_name, inner_font_size)
            canvas.drawString(inner_text_x, inner_text_y, line)
            inner_text_y -= inner_font_size + self.line_height*0.25
    
    
    def draw_labeled_rectangle(self, x, y, width, height, label_text, inner_text=None, **kwargs):
        """
        Draws a labeled rectangle with optional inner text.
    
        This method combines the functionalities of drawing a rectangle, a label on top, and optional inner text.
    
        Args:
            x (float): The x-coordinate of the rectangle's lower-left corner.
            y (float): The y-coordinate of the rectangle's lower-left corner.
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            label_text (str): The text for the label of the rectangle.
            inner_text (str, optional): Text to be displayed inside the rectangle. Supports line breaks. Defaults to None.
            **kwargs: Arbitrary keyword arguments for additional styling (passed to `set_default_values`).
    
        """
        defaults = self.set_default_values(**kwargs)
        
        self.draw_rectangle(x, y, width, height, defaults['line_color'], defaults['corner_radius'])
        self.draw_label(x, y, width, height, label_text, defaults['label_color'], defaults['font_name'], defaults['font_size'])
    
        if inner_text:
            self.draw_inner_text(x, y, width, height, inner_text, defaults['inner_label_color'], defaults['inner_font_name'], defaults['inner_font_size'], defaults['line_height'])


    def draw_labeled_rectangle_with_checkboxes(self, x, y, width, height, label_text, checkbox_labels, **kwargs):
        """
        Draws a labeled rectangle with checkboxes and their labels inside.
    
        Args:
            x (float): The x-coordinate of the rectangle's lower-left corner.
            y (float): The y-coordinate of the rectangle's lower-left corner.
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            label_text (str): The text for the rectangle's label.
            checkbox_labels (list of str): Labels for each checkbox.
            **kwargs: Optional keyword arguments for customizing the block's appearance.

        """
        
        # Draw the labeled rectangle
        self.draw_labeled_rectangle(x, y, width, height, label_text, inner_text=None, **kwargs)
    
        # Calculate dimensions and positions for checkboxes and their labels
        if checkbox_labels:
            space_reserved = 0.75
            checkbox_area_width = width   # Reserve half the width for checkboxes and labels
            checkbox_x_start = x + width*(1-space_reserved)*0.5  # Start position
            checkbox_size = height * 0.5  # Checkbox size, smaller than the height
            checkbox_y = y + (height - checkbox_size) / 2  # Centered vertically
    
            # Draw checkboxes and labels
            self.draw_checkboxes_dynamic(x, checkbox_y, checkbox_area_width, checkbox_size, checkbox_labels, **kwargs)
    
    def draw_checkboxes_dynamic(self, x, y, width, height, checkbox_labels, space_reserved=0.75, **kwargs):
        """
        Draws a series of dynamically positioned checkboxes with labels, centered within a reserved space.
    
        Args:
            x (float): The x-coordinate for the rectangle's lower-left corner.
            y (float): The y-coordinate for the rectangle's lower-left corner.
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            checkbox_labels (list of str): Labels for each checkbox.
            space_reserved (float): Fraction of width reserved for checkboxes and labels.
            **kwargs: Optional keyword arguments for customizing the block's appearance.
        """
    
        # Setting default values if not provided
        defaults = self.set_default_values(**kwargs)
        
        # Accessing the default values for each optional argument
        label_color = defaults['label_color']
        font_name = defaults['font_name']
        font_size = defaults['font_size']
        line_color = defaults['line_color']
    
        canvas = self.canvas
    
        checkbox_size = height * 0.5  # Checkbox size, smaller than the height
        space_between = 5  # Space between checkbox and label
    
        # Calculate the total width required for all checkboxes and labels
        total_width = 0
        for label in checkbox_labels:
            label_width = canvas.stringWidth(label, font_name, font_size)
            total_width += checkbox_size + label_width + space_between
    
        # Calculate starting x-coordinate to center the checkboxes and labels in the reserved area
        reserved_width = width * space_reserved
        start_x = x + (width - reserved_width) / 2 + (reserved_width - total_width) / 2
    
        current_x = start_x
        for label in checkbox_labels:
            label_width = canvas.stringWidth(label, font_name, font_size)
    
            # Draw checkbox
            canvas.setFillColor(HexColor('#FFFFFF'))
            canvas.setStrokeColor(HexColor(line_color))
            canvas.rect(current_x, y + (height - checkbox_size) / 2, checkbox_size, checkbox_size, stroke=1, fill=1)
    
            # Draw label
            canvas.setFillColor(HexColor(label_color))
            canvas.setFont(font_name, font_size)
            canvas.drawString(current_x + checkbox_size + space_between, y + (height - font_size) / 2, label)
    
            # Update current_x for the next checkbox and label
            current_x += checkbox_size + label_width + space_between


    def create_form_block(self, x, y, field_blocks, block_name, **kwargs):
        """
        Creates a structured block of form fields in the PDF.
    
        Args:
            x (float): The starting x-coordinate for the block.
            y (float): The starting y-coordinate for the block.
            field_blocks (list of tuples): Each tuple contains the line number and a list of fields for that line.
            block_name (str): The name of the block.
            **kwargs: Optional keyword arguments for customizing the block's appearance.
        """

        defaults = self.set_default_values(**kwargs)
    
        positions = self._calculate_field_positions(x, y, field_blocks, self.cm_to_points, defaults['line_height'], defaults['field_height'])
        
        for position in positions:
            self._draw_form_field(*position, **kwargs)
    
        self._draw_block_label(x, y, field_blocks, block_name, **kwargs)

    def _calculate_field_positions(self, x, y, field_blocks, cm_to_points, line_height, field_height):
        """
        Calculate positions of each field in the form block, with support for an optional third element in each field.
        """
        positions = []
        for line, elements in field_blocks:
            current_x = x
            for field in elements:
                fwidth, field_label = field[:2]  # Always get first two elements
                optional_element = field[2] if len(field) > 2 else None  # Get third element if it exists
    
                pos_y = y - ((line - 1) * line_height)
                field_position = (current_x, pos_y, fwidth * cm_to_points, field_height, field_label)
    
                # If there's an optional element, include it
                if optional_element is not None:
                    field_position += (optional_element,)
    
                positions.append(field_position)
                current_x += fwidth * cm_to_points
        return positions


    def _draw_block_label(self, x, y, field_blocks, block_name, **kwargs):
        """
        Draw the label for the form block.
        """
        #print(label_color, font_name, font_size, field_height)
        defaults = self.set_default_values(**kwargs)
        
        # Now you can access the default values for each optional argument using defaults['key']
        
        label_color = defaults['label_color']
        font_name = defaults['font_name']
        font_size = defaults['font_size']
        line_color = defaults['line_color']
        line_height = defaults['line_height']
        field_height = defaults['field_height']

        height = (field_blocks[-1][0] - field_blocks[0][0]) * line_height
        width = field_height * 0.70
        xpos = x
        ypos = y - height
    
        self.canvas.setStrokeColor(line_color)
        self.canvas.setFillColor(HexColor('#FFFFFF'))
        self.canvas.roundRect(xpos, ypos, width, height + field_height, radius=2, stroke=1, fill=1)
    
        # Add vertical label
        self.canvas.setFillColor(label_color)
        self.canvas.setFont(font_name, font_size)
        self.canvas.saveState()
        self.canvas.translate(x + field_height * 0.5, (y + field_height + ypos) / 2)
        self.canvas.rotate(90)
        self.canvas.drawCentredString(0, 0, block_name)
        self.canvas.restoreState()

    def _draw_form_field(self, pos_x, pos_y, width, height, field_label, inner_text=None, **kwargs):
        """
        Draws a single form field, including its label and optional inner text.
    
        Args:
            pos_x (float): The x-coordinate of the field's position.
            pos_y (float): The y-coordinate of the field's position.
            width (float): The width of the field.
            height (float): The height of the field.
            field_label (str): The label text for the field.
            inner_text (str, optional): Text to be displayed inside the field. Defaults to None.
            **kwargs: Arbitrary keyword arguments for additional styling.
    
        """
        # Set default values for the field's styling
        defaults = self.set_default_values(**kwargs)
    
        # Draw the rectangle for the field
        self.draw_rectangle(pos_x, pos_y, width, height, defaults['line_color'], defaults['corner_radius'], fill=1)
    
        # Calculate label position and draw the label
        label_x = pos_x
        label_y = pos_y + height - defaults['line_height']  # Position label at the top of the field
        self.draw_label(label_x, label_y, width, defaults['line_height'], field_label, defaults['label_color'], defaults['font_name'], defaults['font_size'])
    
        # If inner text is provided, draw it inside the field
        if inner_text:
            inner_text_x = pos_x
            inner_text_y = pos_y + (height - defaults['field_height']) / 2  # Center inner text vertically
            self.draw_inner_text(inner_text_x, inner_text_y, width, defaults['field_height'], inner_text, defaults['inner_label_color'], defaults['inner_font_name'], defaults['inner_font_size'], defaults['line_height'])

    def insert_image(self, image_path, x, y, width, height):
        """
        Insere uma imagem no PDF.
    
        Args:
            image_path (str): O caminho para a imagem a ser inserida.
            x (float): A coordenada x no PDF onde a imagem será colocada.
            y (float): A coordenada y no PDF onde a imagem será colocada.
            width (float): A largura da imagem no PDF.
            height (float): A altura da imagem no PDF.
        """
        self.canvas.drawImage(image_path, x, y, width, height, preserveAspectRatio=True, anchor='c')
    
#        try:
#            self.canvas.drawImage(image_path, x, y, width, height, preserveAspectRatio=True, anchor='c')
#        except Exception as e:
#            raise Exception(f"Error inserting image at {image_path}: {e}"

    def insert_image_from_binary(self, image_data, x, y, width, height):
        """
        Insere uma imagem no PDF a partir de dados binários.
    
        Args:
            image_data (bytes): Dados binários da imagem.
            x (float): A coordenada x no PDF onde a imagem será colocada.
            y (float): A coordenada y no PDF onde a imagem será colocada.
            width (float): A largura da imagem no PDF.
            height (float): A altura da imagem no PDF.
        """
        # Convert PIL Image to bytes if it's not already in bytes format
        if isinstance(image_data, Image.Image):
            buffer = BytesIO()
            image_data.save(buffer, format="JPEG")  # Adjust format if necessary
            image_data = buffer.getvalue()
    
        # Now image_data is in bytes format, use it directly
        self.canvas.drawImage(ImageReader(BytesIO(image_data)), x, y, width, height, preserveAspectRatio=True, anchor='c')

        
    def draw_gender_field(self, field_x, field_y, field_width, field_height, selected_option=None, options=("M", "F"), **kwargs):
        """
        Draws gender selection checkboxes ('F' and 'M') centered within a predefined field and marks an 'X' in the selected checkbox.
    
        Args:
            field_x (float): The x-coordinate of the field's starting point.
            field_y (float): The y-coordinate of the field's starting point.
            field_width (float): The width of the entire field.
            field_height (float): The height of the entire field.
            selected_option (str): The option ('F' or 'M') that should be marked as selected.
            options (tuple): A tuple containing the options for the field ('F', 'M').
            checkbox_size (int): The size of the checkboxes.
            font_size (int): The font size for the labels next to the checkboxes.
            checkmark_font_size (int): The font size for the checkmark 'X'.
        """    
        # Setting default values if not provided
        defaults = self.set_default_values(**kwargs)
        
        # Now you can access the default values for each optional argument using defaults['key']
        
        label_color = defaults['label_color']
        font_name = defaults['font_name']
        font_size = defaults['font_size']
        line_color = defaults['line_color']
        line_height = defaults['line_height']
        checkbox_size = defaults['checkbox_size']
        checkmark_label_color = defaults['checkmark_label_color']
        checkmark_font_name = defaults['checkmark_font_name']
        checkmark_font_size = defaults['checkmark_font_size']

        # Calcular a largura total necessária para as caixas de seleção e texto
        total_width = 0
        spacing = 5  # Espaço entre elementos
        for option in options:
            total_width += checkbox_size + spacing + self.canvas.stringWidth(option, font_name, font_size)
    
        # Reduzir o espaçamento final após a última opção
        total_width -= spacing
    
        # Calcular o ponto inicial X para centralizar os elementos dentro do campo
        option_x = field_x + (field_width - total_width) / 2
    
        # Calcular o ponto inicial Y para centralizar verticalmente
        option_y = field_y + (field_height*0.75 - checkbox_size) / 2
    
        # Desenhar as caixas de seleção e os rótulos
        for option in options:
            self.canvas.setFillColor(HexColor(label_color))
            self.canvas.setFont(font_name, font_size)
            self.canvas.setStrokeColor(HexColor(line_color))
            self.canvas.rect(option_x, option_y, checkbox_size, checkbox_size, stroke=1, fill=0)
            self.canvas.drawString(option_x + checkbox_size + 2, option_y, option)
            #option_x += checkbox_size + self.canvas.stringWidth(option, "Helvetica", font_size) + spacing

            if selected_option: 
                # Verificar se a opção atual é a selecionada e, em caso afirmativo, marcar um 'X'
                if option == selected_option:
                    # Centralizar o 'X' na caixa
                    checkmark_x = option_x + (checkbox_size - self.canvas.stringWidth("X", checkmark_font_name, checkmark_font_size)) / 2
                    checkmark_y = option_y + (checkbox_size - font_size) / 2
                    self.canvas.setFillColor(HexColor(checkmark_label_color))
                    self.canvas.setFont(checkmark_font_name, checkmark_font_size)
                    self.canvas.drawString(checkmark_x, checkmark_y, "X")
        
                # Atualizar option_x para a próxima caixa de seleção
            option_x += checkbox_size + self.canvas.stringWidth(option, font_name, font_size) + spacing

    def insert_header_image(self, image_path, x, y, width_percentage=None):
        """
        Inserts an image into the header of the PDF form at a specified width percentage of its original size.

        The method places an image at the specified coordinates on the PDF canvas.
        If a width percentage is provided, the image is resized to that percentage of its original width,
        maintaining its aspect ratio.

        Args:
            image_path (str): The path to the image file.
            x (float): The x-coordinate on the PDF canvas where the image will be placed.
            y (float): The y-coordinate on the PDF canvas where the image will be placed.
            width_percentage (float, optional): The desired width of the image as a percentage of 
                its original width. For example, 0.25 for 25% of the original width. If not provided, 
                the image's original size is used.

        Returns:
            None
        """
        image_reader = ImageReader(image_path)
        original_width, original_height = image_reader.getSize()

        # Calculate new size if a width percentage is provided
        if width_percentage:
            new_width = original_width * width_percentage
            new_height = original_height * width_percentage  # maintain aspect ratio
        else:
            new_width, new_height = original_width, original_height

        self.canvas.drawImage(image_reader, x, y, width=new_width, height=new_height)


    def create_pdf_header(self, logo_path, header_text, **kwargs):
        """
        Creates a formatted header in the PDF with a logo and header text aligned with the top of the logo.
        
        Args:
            logo_path (str): The path to the logo image file.
            header_text (str): The text to display in the header.
            **kwargs: Optional keyword arguments for customizing the header appearance.
        
        Returns:
            float: The Y-position in points marking the end of the header.
        """
        # Setting default values if not provided
        defaults = self.set_default_values(**kwargs)
    
        # Access the default values for each optional argument
        font_size = defaults['font_size']
        line_height = defaults['line_height']
    
        styles = getSampleStyleSheet()
        custom_header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=font_size,
            leading=line_height,
            spaceAfter=6
        )
    
        # Calculate the height of the header based on text lines
        num_lines = header_text.count('<br/>') + 1
        min_lines = 4
        header_height = max(min_lines, num_lines) * line_height
    
        # Error handling for logo file
        try:
            logo = ImageReader(logo_path)
        except Exception as e:
            raise FileNotFoundError(f"Unable to find or open the logo file: {e}")
    
        original_logo_width, original_logo_height = logo.getSize()
        logo_height = header_height
        logo_width = original_logo_width * (logo_height / original_logo_height)
        margin = 1.00 * self.cm_to_points  # Left margin
    
        # Draw the logo image, adjusting its height to the header height
        self.canvas.drawImage(logo, margin, self.height - logo_height - margin, width=logo_width, height=logo_height, mask='auto')
    
        # Create the header text using Paragraph to handle HTML-style formatting
        header_paragraph = Paragraph(header_text, custom_header_style)
        text_width, text_height = header_paragraph.wrapOn(self.canvas, self.width - logo_width - margin * 2, header_height)
    
        # Align the top of the text with the top of the image
        text_y_position = self.height - max(logo_height, text_height) - margin/2
        header_paragraph.drawOn(self.canvas, logo_width + margin*1.25, text_y_position)
    
        # Return the Y-position marking the end of the header
        return margin, self.height - header_height - margin * 2


    def create_text(self, text, x, y, alignment='center', **kwargs):
        """
        Creates centered text on the PDF.

        Args:
            text (str): The text to be centered.
            x (float): The x-coordinate for the center of the text.
            y (float): The y-coordinate for the center of the text.
            **kwargs: Optional keyword arguments for customizing the header appearance.
        
        Returns:
            None
        """
        # Setting default values if not provided
        defaults = self.set_default_values(**kwargs)
        
        # Access the default values for each optional argument
        font_name = defaults['font_name']
        font_size = defaults['font_size']
        line_height = defaults['line_height']


        text_width = self.canvas.stringWidth(text, font_name, font_size)

        # Calculating text position based on alignment
        if alignment == 'center':
            text_x = x - (text_width / 2)
        elif alignment == 'right':
            text_x = x - text_width
        else:  # default to left alignment
            text_x = x

        self.canvas.drawString(text_x, y, text)

    @staticmethod
    def read_yaml_configuration(file_name):
        """
        Reads a YAML configuration file and returns its content as a Python dictionary.
    
        Args:
            file_name (str): The name of the YAML file to be read.
    
        Returns:
            dict or None: A dictionary containing the YAML configuration if successful, 
            or None if there was an error or the file was not found.
        """
        try:
            with open(file_name, 'r') as file:
                configuration = yaml.load(file, Loader=yaml.FullLoader)
                return configuration
        except FileNotFoundError:
            print(f"The file '{file_name}' was not found.")
            return None
        except Exception as e:
            print(f"Error while reading the file '{file_name}': {str(e)}")
            return None
    
    @staticmethod
    def build_field_info(configuration,athlete_data):
        """
        Converts a YAML configuration into a list of tuples in the specified format.
    
        Args:
            configuration (dict): The YAML configuration represented as a dictionary.
            athlete_data (dict): Data of the athlete to populate the form.

        Returns:
            list: A list of tuples where each tuple represents a block with its label 
            and a list of tuples for the fields within that block.
        """
        field_info_list = []
        
        for block in configuration:
            block_name = block['block_name']
            lines      = block['lines']
            block_info = (block_name, [])
            
            field_inf = []
            for line_info in lines:
                line   = line_info['line']
                fields = line_info['fields']
                line_fields = []
                for field in fields:
                    width = field['width']
                    label = field['label']
                    key   = field.get('key', None)  # Get the 'key' or set it to an empty string if not present
                    #value = athlete_data.get(key, '') if key else None
                    value = str(athlete_data.get(key, '')) if key else ''

                    field_tuple = (width, label) if value is None else (width, label, value)                    
                    line_fields.append(field_tuple)
                
                block_info[1].append((line,line_fields))
            
            field_info_list.append(block_info)
        
        return field_info_list

    @staticmethod
    def build_field_info_from_yaml(yaml_file, athlete_data):
        """Builds field information for the form from a YAML file.

        Args:
            yaml_file (str): Path to the YAML file containing form structure.
            athlete_data (dict): Data of the athlete to populate the form.

        Returns:
            list: A list containing field information.
        """
        with open(yaml_file, 'r') as file:
            form_structure = yaml.safe_load(file)

        field_info = []
        for line_info in form_structure:
            line = line_info['line']
            fields = line_info['fields']
            line_fields = []
            for field in fields:
                width = field['width']
                label = field['label']
                key = field.get('key')
                value = athlete_data.get(key, '') if key else None
                field_tuple = (width, label) if value is None else (width, label, value)
                line_fields.append(field_tuple)
            field_info.append((line, line_fields))
        return field_info

