# VAULT — Professional Expense Tracker

Flask + SQLite + HTML/CSS/JavaScript dashboard. The interface uses a midnight navy palette, violet/blue gradients, responsive cards, charts, transaction search, editing, deletion and CSV export.

## IMPORTANT: connect your original records
Your personal `expenses.db` was not uploaded in this chat, so it cannot be bundled into this ZIP. To keep your records:
1. Make a backup of your original `expenses.db`.
2. Extract this ZIP.
3. Copy your original `expenses.db` into the extracted `database` folder, replacing only the empty placeholder text file (not an existing DB).
4. The final path must be `Professional_Expense_Tracker/database/expenses.db`.

The app supports the earlier `transaction_type` and `transactions_type` column spellings, including databases that contain both. It does not drop or recreate an existing transactions table. If no DB is copied, it creates a new empty database.

## Run on Windows
Open PowerShell in this extracted folder:
```powershell
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Stop with Ctrl+C.

Charts and Google Fonts use internet-hosted assets. Core transactions and database operations run locally.

## API
GET /api/health (app status)
GET /api/transactions
POST /api/transactions
PUT /api/transactions/<id>
DELETE /api/transactions/<id>
GET /api/dashboard
GET /api/export

Make another database backup before testing edit/delete operations.
