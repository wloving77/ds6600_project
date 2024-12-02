import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


class MySQLHelper:
    def __init__(self):
        """
        Initialize the helper class with connection parameters.
        """
        load_dotenv("../../.env")
        self.host = os.getenv("MYSQL_EXTERNAL_HOST")
        self.database = os.getenv("MYSQL_DATABASE")
        self.user = os.getenv("MYSQL_ROOT_USER")
        self.password = os.getenv("MYSQL_ROOT_PASSWORD")
        self.port = 3306
        self.connection = None

    def connect(self):
        """
        Establish a new connection to the MySQL database.
        """
        if self.connection and self.connection.is_connected():
            print("Connection is already open.")
            return
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
            )
            if self.connection.is_connected():
                print("Connected to MySQL database.")
        except Error as e:
            print(f"Failed to connect: {e}")
            self.connection = None

    def close(self):
        """
        Close the existing connection.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connection closed.")
        else:
            print("No connection to close.")
        self.connection = None

    def execute_query(self, query, params=None):
        """
        Execute a query and return the result.
        """
        if not self.connection or not self.connection.is_connected():
            print("No active connection. Call connect() first.")
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            if cursor.description:
                # If the query returns results, fetch them
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                # If the query doesn't return results, commit the transaction
                self.connection.commit()
                cursor.close()
                print("Query executed successfully.")
        except Error as e:
            print(f"Failed to execute query: {e}")
            return None

    def __del__(self):
        """
        Destructor to ensure the connection is closed when the object is deleted.
        """
        self.close()
