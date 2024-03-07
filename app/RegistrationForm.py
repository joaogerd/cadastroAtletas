import os
from reportlab.lib.pagesizes import A4

from .formularioPDF import FormularioPDF
from .paths import path

class RegistrationForm:
    """A class to create a registration form PDF for athletes."""

    def __init__(self, header_text, form_filename="registration_form.pdf", papersize=A4, title='REGISTRATION FORM', logo=None):
        """
        Initializes a RegistrationForm object.

        Args:
            header_text (str): Text to be displayed in the form header.
            form_filename (str, optional): Name of the generated PDF form file. Defaults to 'registration_form.pdf'.
            papersize: (optional): Size of the PDF page, defaults to A4.
            title (str, optional): Title of the form. Defaults to 'REGISTRATION FORM'.
            logo (str, optional): Path to a logo file to be included in the form. Can be None if no logo is provided.

        Example usage:
            form = RegistrationForm("Registration Information", logo="logo.png")
        """
        
        self.form_filename = form_filename
        self.papersize = papersize
        self.title = title
        self.logo = logo
        self.header_text = header_text

        self.formulario_pdf = FormularioPDF(self.form_filename, papersize=self.papersize)

    def create_form(self, athlete_data):
        """Creates the registration form with athlete data and optional photo.

        Args:
            athlete_data (dict): Data of the athlete.

        Returns:
            None
        """

        self.formulario_pdf.set_styles(font_size=10)
        width, height = self.papersize
        cm_to_points = self.formulario_pdf.cm_to_points

        #x, y = 1.00 * cm_to_points, height - 6.90 * cm_to_points


        x, y = self.formulario_pdf.create_pdf_header(self.logo, self.header_text, font_size=14, line_height=0.8)

        # Title of the Form
        pos_x = self.formulario_pdf.width / 2
        pos_y = y
        self.formulario_pdf.create_text(self.title, pos_x, pos_y,alignment='center')

        # include photo field    
        photo_width = 3 * cm_to_points
        photo_height = (4/3) * photo_width
        photo_x = x + 16 * cm_to_points
        photo_y = y - photo_height

        if athlete_data.get('foto',None):
            self.formulario_pdf.insert_image_from_binary(athlete_data['foto'], photo_x, photo_y, photo_width, photo_height)
            self.formulario_pdf.draw_labeled_rectangle(photo_x, photo_y, photo_width, photo_height, '', line_color='#FFFFFF', line_width=5, fill=0)
            self.formulario_pdf.draw_labeled_rectangle(photo_x, photo_y, photo_width, photo_height, '', fill=0)
        else:
            self.formulario_pdf.draw_labeled_rectangle(photo_x, photo_y, photo_width, photo_height, '', 'FOTO\\n3x4')

       # all other fields
        pos_y = y - photo_height + 2*self.formulario_pdf.line_height
        configuration = self.formulario_pdf.read_yaml_configuration(os.path.join(path.yaml,'form.yaml'))
        field_info_list = self.formulario_pdf.build_field_info(configuration, athlete_data)
        for block_name, field_info in field_info_list:
            self.formulario_pdf.create_form_block(x, pos_y, field_info, block_name=block_name)
            pos_y = pos_y - 5.5 * 0.9 * cm_to_points


        # include gender option
        gender_x = x + 13.30 * cm_to_points
        gender_y = y - photo_height + 2*self.formulario_pdf.line_height
        gender_width = 2.60 * cm_to_points
        gender_height = self.formulario_pdf.line_height
        selected_gender = self.get_selected_gender(athlete_data)
        self.formulario_pdf.draw_gender_field(gender_x, gender_y, gender_width, gender_height, selected_gender)



        self.formulario_pdf.canvas.showPage()
        

    def save_pdf(self):
        """Saves the current form in PDF format.

        Returns:
            None
        """
        self.formulario_pdf.canvas.save()


    @staticmethod
    def get_selected_gender(athlete_data):
        """Determines which gender radio button is checked.

        Args:
            athlete_data (dict): Data of the athlete.

        Returns:
            str: 'M' if the 'masculino' radio button is checked,
                 'F' if the 'feminino' radio button is checked,
                 an empty string if neither is checked.
        """
        return 'M' if athlete_data.get('masculino') else 'F' if athlete_data.get('feminino') else ''

