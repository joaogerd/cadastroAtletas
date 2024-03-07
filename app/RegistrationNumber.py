import sqlite3
class RegistrationNumber:
    """
    A class to generate sequential registration numbers for athletes based on their birth year.

    Attributes:
        db (object): Database connection object.
        config (object): Configuration object containing database settings.
        birth_year (int): The birth year of the athlete.
        current_year (int): The current year.
        registration_number (str): The next sequential registration number.
    """
    columnName = 'matricula'
    def __init__(self, db, config, birth_year, current_year):
        """
        The constructor for RegistrationGenerator class.

        Args:
            db (object): Database connection object.
            config (object): Configuration object containing database settings.
            birth_year (int): The birth year of the athlete.
            current_year (int): The current year.

        Raises:
            ValueError: If the birth year or current year is not logical or valid.
        """
        if birth_year > current_year or birth_year < 1900:
            raise ValueError("Invalid birth year or current year.")
        self.db = db
        self.config = config
        self.birth_year = birth_year
        self.current_year = current_year
        self.registration_number = self.generate_registration_number()

    def get_next_index(self):
        """
        Retrieves the next sequential index (MMMM) based on the athlete's category.

        Returns:
            int: The next index number.

        Raises:
            ConnectionError: If there is an issue connecting to the database.
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            table_name = self.config.app_config.database_table_name
            category = self.current_year - self.birth_year
            query = f"SELECT MAX(CAST(SUBSTR({self.columnName}, 7, 4) AS INTEGER)) FROM {table_name} WHERE CAST(SUBSTR({self.columnName}, 5, 2) AS INTEGER) = ?"
            cursor = self.db.conn.cursor()
            cursor.execute(query, (category,))
            result = cursor.fetchone()

            if result[0] is not None:
                next_index = result[0] + 1
            else:
                next_index = 1

            return next_index
        except sqlite3.OperationalError as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Database operation failed: {e}")

    def generate_registration_number(self):
        """
        Generates the next registration number in the format AAAACCMMMM.

        Returns:
            str: The next registration number.
        """
        next_index = self.get_next_index()
        category = self.current_year - self.birth_year
        return f"{self.current_year:04d}{category:02d}{next_index:04d}"



