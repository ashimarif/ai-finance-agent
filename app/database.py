import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/finance_db")

def get_db_connection():
    """Returns a direct connection to PostgreSQL with dictionary-like row access."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    """Initializes PostgreSQL tables for expenses, group bills, and IOUs."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Personal Expenses Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personal_expenses (
                    id SERIAL PRIMARY KEY,
                    description TEXT NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Group Outings / Split Bills Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_bills (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    total_amount NUMERIC(10, 2) NOT NULL,
                    payer VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Individual IOUs / Debts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iou_records (
                    id SERIAL PRIMARY KEY,
                    bill_id INTEGER REFERENCES group_bills(id) ON DELETE CASCADE,
                    debtor_name VARCHAR(100) NOT NULL,
                    amount_owed NUMERIC(10, 2) NOT NULL,
                    is_settled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    print("PostgreSQL tables successfully initialized.")

if __name__ == "__main__":
    init_db()