import os
import sqlite3
from .paths import path

class ConnectDB:
    """
    A class for connecting to and interacting with an SQLite database.

    Parameters:
        db_name (str): The name of the database file.

    Example:
    >>> db = ConnectDB('my_database.db')
    >>> db.createTable('my_table', 'sql/table_body.sql')
    >>> db.commit_db()
    >>> data = db.readByColumn('nome')
    >>> record = db.readById(1)
    >>> db.close_db()
    """

    def __init__(self, db_name):
        """
        Initialize the ConnectDB instance and connect to the database.

        Parameters:
            db_name (str): The name of the database file.

        Returns:
            ConnectDB: An instance of the ConnectDB class.

        Example:
        >>> db = ConnectDB('my_database.db')
        """
        try:
            # Connecting to the database
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            # Printing the database name
            print("Database:", db_name)
            # Reading the SQLite version
            self.cursor.execute('SELECT SQLITE_VERSION()')
            self.data = self.cursor.fetchone()
            # Printing the SQLite version
            print("SQLite version: %s" % self.data)
        except sqlite3.Error:
            print("Error opening the database.")
            return False

    def commit_db(self):
        """
        Commit changes to the database.

        Usage:
        >>> db.commit_db()
        """
        if self.conn:
            self.conn.commit()

    def close_db(self):
        """
        Close the database connection.

        Usage:
        >>> db.close_db()
        """
        if self.conn:
            self.conn.close()
            print("Connection closed.")

    def createTable(self, tbName, schema_name=os.path.join(path.sql,'tableScheme.sql')):
        """
        Create a table in the database based on a schema file.

        Parameters:
            tbName (str): The name of the table to create.
            schema_name (str, optional): The name of the schema file. Defaults to 'sql/table_body'.

        Usage:
        >>> db.createTable('my_table', 'sql/table_body.sql')
        """
        self.tbName = tbName
        self.tbScheme = schema_name

        # Get keys used in SQL form and UI
        with open(self.tbScheme, 'r') as f:
            self.keys = [line.split(" ")[0] for line in f]
        f.close()

        print("Creating table %s ..." % self.tbName)

        try:
            with open(self.tbScheme, 'rt') as f:
                tableBody = f.read()
            f.close()

            sqliteTable = f''' CREATE TABLE {self.tbName} (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                           '''  
            sqliteTable += '\t\t\t'.join((tableBody.rstrip()).splitlines(True))
            sqliteTable += ');'

            self.cursor.executescript(sqliteTable)

        except sqlite3.Error:
            print("Warning: Table %s already exists." % self.tbName)
            return False

        print("Table %s created successfully." % self.tbName)

    def readByColumn(self, Column='nome'):
        """
        Retrieve data from the table ordered by a specified column.

        Parameters:
            Column (str, optional): The column by which to order the data. Defaults to 'nome'.

        Returns:
            list: A list of rows from the table.

        Usage:
        >>> data = db.readByColumn('nome')
        """
        sql = f"SELECT * FROM {self.tbName} ORDER BY {Column}"
        r = self.cursor.execute(sql)
        return r.fetchall()

    def readById(self, id_value):
        """
        Retrieve a record from the table by its ID.

        Parameters:
            id_value (int): The ID of the record to retrieve.

        Returns:
            tuple: A tuple representing the record.

        Usage:
        >>> record = db.readById(1)
        """
        # Query the database based on the ID
        sql = f"SELECT * FROM {self.tbName} WHERE id=?"
        r = self.cursor.execute(sql, (id_value,))
        return r.fetchone()

