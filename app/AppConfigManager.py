import os
import sys
import configparser

from .AppConfig import AppConfig
from .paths import path

class AppConfigManager:
    """A class for managing application configurations.

    This class provides methods to load and save application configuration settings
    using the configparser library. Configuration settings are stored in a file named
    'config.ini' within the user's home directory.

    Attributes:
        config_dir (str): The directory where the configuration file is stored.
        config_file (str): The path to the configuration file.

    Methods:
        loadConfig(): Load and retrieve application configuration settings.
        saveConfig(config: AppConfig): Save application configuration settings.

    Example:
        # Create an instance of AppConfigManager
        config_manager = AppConfigManager()

        # Load existing configuration settings or create a default one
        app_config = config_manager.load_config()

        # Update app_config attributes
        app_config.database_file = "new_database.db"
        app_config.nome = "My App Name"

        # Save the updated configuration settings
        config_manager.saveConfig(app_config)
    """

    def __init__(self):

        """Initialize an instance of AppConfigManager.

        The `config_dir` is set to the user's home directory, and `config_file`
        points to the "config.ini" file within this directory.
        """

        self.config_dir = os.path.expanduser("~/.futsal_team_manager")
        self.config_file = os.path.join(self.config_dir, "config.ini")

    def loadConfig(self):
        """Load and retrieve application configuration settings.

        Reads the 'config.ini' file and returns an AppConfig object containing
        the configuration settings if the file exists. If the file doesn't exist,
        a default AppConfig object is created with a default database file.

        Returns:
            AppConfig: An AppConfig object containing configuration settings.
        """
        config = configparser.ConfigParser()
        config_exists = os.path.exists(self.config_file)  # Check if the config file exists

        if config_exists:
            config.read(self.config_file)
            app_config = AppConfig()
            app_config.database_file       = config.get("AppConfig", "database_file", fallback="")
            app_config.database_table_file = config.get("AppConfig", "database_table_file", fallback="")
            app_config.database_table_name = config.get("AppConfig", "database_table_name", fallback="")
            app_config.logo_file           = config.get("AppConfig", "logo_file", fallback="")
            app_config.nome                = config.get("AppConfig", "nome", fallback="")
            app_config.rua                 = config.get("AppConfig", "rua", fallback="")
            app_config.numero              = config.get("AppConfig", "numero", fallback="")
            app_config.cidade              = config.get("AppConfig", "cidade", fallback="")
            app_config.uf                  = config.get("AppConfig", "uf", fallback="")
            app_config.cep                 = config.get("AppConfig", "cep", fallback="")
            app_config.dt_fundacao         = config.get("AppConfig", "dt_fundacao", fallback="")
            app_config.cnpj                = config.get("AppConfig", "cnpj", fallback="")
            app_config.fone_contato        = config.get("AppConfig", "fone_contato", fallback="")
            app_config.email_contato       = config.get("AppConfig", "email_contato", fallback="")
            app_config.email_contato       = config.get("AppConfig", "email_contato", fallback="")
            app_config.categoria_par       = config.get("AppConfig", "categoria_par", fallback="False")

            return app_config, config_exists
        else:
            db_file = os.path.join(self.config_dir, "athlete.db")
            tb_file = os.path.join(path.sql,'tableScheme.sql')
            return AppConfig(db_file,tb_file, 'athletes'), config_exists

    def saveConfig(self, config):
        """Save application configuration settings.

        Saves the provided AppConfig object's configuration settings to the
        'config.ini' file. If the configuration directory doesn't exist, it
        creates the directory.

        Args:
            config (AppConfig): An AppConfig object containing configuration settings.
        """
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        config_parser = configparser.ConfigParser()
        config_parser["AppConfig"] = {
            "database_file": config.database_file,
            "database_table_file": config.database_table_file,
            "database_table_name": config.database_table_name,
            "logo_file": config.logo_file,
            "nome": config.nome,
            "rua": config.rua,
            "numero": config.numero,
            "cidade": config.cidade,
            "uf": config.uf,
            "cep": config.cep,
            "dt_nascimento": config.dt_fundacao,
            "doc_cpf": config.cnpj,
            "fone_contato": config.fone_contato,
            "email_contato": config.email_contato,
            "categoria_par": config.categoria_par,
        }

        with open(self.config_file, "w") as cfgfile:
            config_parser.write(cfgfile)
