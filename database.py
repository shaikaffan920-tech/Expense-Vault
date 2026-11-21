from pathlib import Path
import sqlite3

BASE_DIR=Path(__file__).resolve().parent
DB_PATH=BASE_DIR/"database"/"expenses.db"

def get_connection(readonly=False):
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    if readonly:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database missing: {DB_PATH}. Copy your existing expenses.db into database folder.")
        con=sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro",uri=True)
    else:
        con=sqlite3.connect(str(DB_PATH))
    con.row_factory=sqlite3.Row
    return con

def type_column(cols):
    # Handles both spellings found in earlier versions of this project.
    if "transaction_type" in cols: return "transaction_type"
    if "transactions_type" in cols: return "transactions_type"
    return None

def initialize_database():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(str(DB_PATH))
    con.row_factory=sqlite3.Row
    try:
        exists=con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='transactions'").fetchone()
        if not exists:
            con.execute("""CREATE TABLE transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                date TEXT NOT NULL)""")
            con.commit()
        cols={r["name"] for r in con.execute("PRAGMA table_info(transactions)")}
        if not ({"transaction_type","transactions_type"} & cols):
            con.execute("ALTER TABLE transactions ADD COLUMN transaction_type TEXT")
            con.execute("UPDATE transactions SET transaction_type='expense' WHERE transaction_type IS NULL")
            con.commit()
    finally: con.close()
