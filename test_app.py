import unittest
import sqlite3
from datetime import datetime, timedelta

class TestJWKS(unittest.TestCase):
    def setUp(self):
        # Setup the database before each test
        self.conn = sqlite3.connect(':memory:')  # In-memory DB for testing
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                kid INTEGER PRIMARY KEY AUTOINCREMENT,
                key BLOB NOT NULL,
                exp INTEGER NOT NULL
            );
        ''')

    def tearDown(self):
        # Close the database after each test
        self.conn.close()

    def test_insert_key(self):
        # Insert a key and verify it's stored
        expiration_time = int((datetime.now() + timedelta(hours=1)).timestamp())
        self.cursor.execute("INSERT INTO keys (key, exp) VALUES (?, ?)", ('test_key', expiration_time))
        self.conn.commit()

        self.cursor.execute("SELECT * FROM keys")
        rows = self.cursor.fetchall()
        self.assertEqual(len(rows), 1)

if __name__ == '__main__':
    unittest.main()
