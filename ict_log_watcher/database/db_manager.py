import pyodbc
import pandas as pd
from utils.logger import get_logger
import platform

class DbManager:
    def __init__(self, server, database, user, password):
        """ initialize the Database Manager with the database details."""
        self.server = server
        self.database = database
        self.user = user
        self.password = password

        # Detect operating system
        os_type = platform.system()

        # Select the appropriate driver
        if os_type == 'Linux':
            driver = 'FreeTDS'
        elif os_type == 'Windows':
            driver = 'SQL Server'
        else:
            self.logger.error("Unsupported Operating System")
            return

        # Create the connection string
        self.conn_str = f'DRIVER={{{driver}}};SERVER={self.server};PORT=1433;DATABASE={self.database};UID={self.user};PWD={self.password};TDS_Version=7.3'
        
        self.conn = None
        self.logger = get_logger(__name__)

    
    @property
    def connected(self):
        """ Checks if the database connection is still valid. """
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")  # A simple query
            return True
        except Exception as e:
            self.logger.error(f"The database connection has been lost: {e}")
            return False


    def connect(self):
        try:
            self.conn = pyodbc.connect(self.conn_str)
        except Exception as e:
            self.logger.error(f"Couldn't connect. connection string: {self.conn_str}, error: {e}")
        
    def disconnect(self):
        """ close the database connection """
        if self.conn:
            self.conn.close()
            self.conn = None

    def _get_column_names(self, table):
        """ retrieve the column names of a table """
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'")
            columns = cursor.fetchall()
            return [col[0] for col in columns]
        except Exception as e:
            self.logger.error(f"{e}")
            return None

            
    def insert(self, table_name:str, data:list):
        """
        Insert data into table.
        `data` is a list containing the values to be inserted.
        The order of the values should correspond to the table's column order.
        """
        try:
            if not self.conn:
                self.logger.warn("There is no database connection.")
                return None
            
            # Replace 'nan' with 'None'
            data = [None if pd.isna(val) else val for val in data]
            
            column_names = self._get_column_names(table_name)
            if column_names != None:
                placeholders = ', '.join('?' * len(column_names))
                sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
                
                self.logger.debug(f"insert sql query: {sql}")
                
                cursor = self.conn.cursor()
                cursor.execute(sql, tuple(data))
                self.conn.commit()
            else:
                self.logger.warning(f"couldn't fetch column names")
        except Exception as e:
            self.logger.error(e)
            return None

    def get_data(self, table, condition=None):
        """
        Fetch data from a table. 
        `condition` is a string that describes the condition for selection. 
        For example, "id=1" or "name='John'".
        If condition is None, then all rows will be selected.
        """
        if not self.conn:
            self.logger.warn("There is no database connection.")
            return None

        cursor = self.conn.cursor()

        if condition:
            sql = f'SELECT * FROM {table} WHERE {condition}'
        else:
            sql = f'SELECT * FROM {table}'

        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.logger.info(f"Fetched data: '{rows}' from {self.server}:{self.database}:{table}")
            return rows
        except Exception as e:
            self.logger.error(f"Couldn't fetch data. Error: {str(e)}")
            return None
    
    def get_column_values(self, table, column, condition=None):
        """
        Fetch a column data from a table. 
        `column` is the name of the column to fetch. 
        `condition` is a string that describes the condition for selection. 
        For example, "id=1" or "name='John'".
        If condition is None, then all rows will be selected.
        """
        if not self.conn:
            self.logger.warn("There is no database connection.")
            return

        cursor = self.conn.cursor()

        if condition:
            sql = f'SELECT {column} FROM {table} WHERE {condition}'
        else:
            sql = f'SELECT {column} FROM {table}'
        
        self.logger.info(f"sql query for get values: {sql}")
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.logger.info(f"Fetched data: '{rows}' from {self.server}:{self.database}:{table}")
            return [row[0] for row in rows]
        except Exception as e:
            self.logger.error(f"Couldn't fetch data. Error: {str(e)}")
            return None

    def get_table_names(self):
        """ Retrieve the table names of the database """
        if not self.conn:
            self.logger.warn("There is no database connection.")
            return

        cursor = self.conn.cursor()

        try:
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        except Exception as e:
            self.logger.error(f"Couldn't fetch table names. Error: {str(e)}")
            return None
    
    def row_exists_by(self, table, column_name, value):
        """
        Check if a row exists in the table that matches the given column name and value.
        
        :param table: The name of the table to query
        :param column_name: The name of the column to check
        :param value: The value to match in the column
        :return: True if a matching row exists, False otherwise
        """
        if not self.conn:
            self.logger.warn("There is no database connection.")
            return False

        cursor = self.conn.cursor()
        
        # Using parameterized query to prevent SQL injection
        sql = f"SELECT COUNT(*) FROM {table} WHERE {column_name} = ?"
        
        self.logger.debug(f"row_exists_by sql query: {sql}")

        try:
            cursor.execute(sql, (value,))
            count = cursor.fetchone()[0]
            exists = count > 0
            return exists
        except Exception as e:
            self.logger.error(f"Couldn't execute query. Error: {str(e)}")
            return None