import sqlite3
from PIL import Image
from io import BytesIO
from datetime import datetime
import logging

class BusinessLogic:
    def __init__(self, db_connection):
        """
        Initialize the business logic layer with a database connection.

        Args:
            db_connection: A database connection object.
        """
        self.db = db_connection

    def fetch_athlete_data(self, athlete_id):
        """
        Fetches athlete data from the database given an athlete ID.

        Args:
            athlete_id (int): The ID of the athlete to fetch data for.

        Returns:
            dict: A dictionary containing the athlete's data, with images and dates processed.
        """
        try:
            data = self.db.readById(athlete_id)
        except Exception as e:
            logging.error(f"Error fetching data for athlete {athlete_id}: {e}")
            return {}

        if not data:
            return {}  # Return an empty dictionary if no data is found

        athlete_data = {}
        for k, value in zip(self.db.keys, data[1:]):  # Assuming self.db.keys are the column names
            if value is not None:
                if k == 'foto':
                    athlete_data[k] = self._process_image(value)
                elif isinstance(value, datetime):
                    athlete_data[k] = self._format_date(value)
                else:
                    athlete_data[k] = value
        return athlete_data

    def _process_image(self, image_data):
        """Processes binary image data into an Image object."""
        try:
            return Image.open(BytesIO(image_data))
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return None

    def _format_date(self, date_obj):
        """Formats a datetime object into a string."""
        return date_obj.strftime("%d/%m/%Y")

    def update_athlete_data(self, athlete_id, data):
        """
        Update data for a specific athlete in the database.

        Args:
            athlete_id: The ID of the athlete.
            data: A dictionary containing the data to update.
        """
        if not data:
            logging.warning("No data provided to update.")
            return False

        columns = data.keys()
        values = list(data.values())
        set_clause = ', '.join([f"{col} = ?" for col in columns])

        update_query = f"UPDATE athletes SET {set_clause} WHERE id = ?"
        values.append(athlete_id)

        try:
            self.db.cursor().execute(update_query, values)
            self.db.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating athlete data: {e}")
            self.db.rollback()
            return False

    def insert_row(self, **kwargs):
        """
        Insert a new row into the database with the provided values.
        """
        columns = ','.join(kwargs.keys())
        values = tuple(kwargs.values())
        placeholders = ','.join(['?' for _ in kwargs])
        query = f"INSERT INTO {self.db.tbName} ({columns}) VALUES ({placeholders})"
        try:
            self.db.cursor.execute(query, values)
            self.db.commit_db()
            logging.info("Data inserted successfully.")
            return True
        except sqlite3.IntegrityError as e:
            logging.error(f"Insertion Error: {e}")
            return False

    def update_row(self, row_id, **kwargs):
        """
        Update a row in the database with the provided values.
        """
        columns = ','.join([f"{col} = ?" for col in kwargs.keys() if kwargs[col] is not None])
        values = [kwargs[col] for col in kwargs.keys() if kwargs[col] is not None]
        values.append(row_id)
    
        if not columns:
            logging.error("No columns provided for update.")
            return False
    
        query = f"UPDATE {self.db.tbName} SET {columns} WHERE id = ?"
    
        try:
            self.db.cursor.execute(query, values)
            self.db.commit_db()
            logging.info("Data updated successfully.")
            return True
        except sqlite3.IntegrityError as e:
            logging.error(f"Update Error: {e}")
            return False
