class AppConfig:
    """Represents the configuration settings of the application.

    This class is used to store various configuration settings such as the database file path,
    logo file path, contact information, and address details for the application.

    Attributes:
        database_file (str, optional): The path to the database file. Defaults to None.
        database_table_file (str, optional): The path to the database table file. Defaults to None.
        database_table_name (str, optional): The name of the database table. Defaults to None.
        logo_file (str): The path to the logo image file.
        nome (str): The configured name.
        rua (str): The configured street address.
        numero (str): The configured street number.
        cidade (str): The configured city.
        uf (str): The configured state or province.
        cep (str): The configured postal code.
        fone_contato (str): The configured contact phone number.
        dt_nascimento (str): The configured date of birth.
        doc_cpf (str): The configured CPF (Brazilian tax ID).
        email_responsavel (str): The configured responsible person's email address.

    Methods:
        __init__(self, db_file=None): Initializes an instance of AppConfig with optional database file path.
    """
    def __init__(self, db_file=None, table_file=None, table_name=None):
        """Initialize an instance of AppConfig.

        Args:
            db_file (str, optional): The path to the database file. Defaults to None.
            table_file (str, optional): The path to the database table file. Defaults to None.
            table_name (str, optional): The name of the database table. Defaults to None.
        """
        self.database_file = db_file
        self.database_table_file = table_file
        self.database_table_name = table_name
        self.logo_file = ""
        self.nome = ""
        self.rua = ""
        self.numero = ""
        self.cidade = ""
        self.uf = ""
        self.cep = ""
        self.dt_fundacao = ""
        self.cnpj = ""
        self.fone_contato = ""
        self.email_contato = ""
        self.categoria_par = ""


