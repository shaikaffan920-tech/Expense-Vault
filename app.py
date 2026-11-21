from flask import Flask, jsonify, request, render_template, Response
from database import get_connection, initialize_database, type_column
from datetime import date
import csv, io, sqlite3

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify(status="success", message="Expense Tracker API is running")

@app.get("/api/transactions")
def transactions():
    con = get_connection(readonly=True)
    try:
        cols = {r["name"] for r in con.execute("PRAGMA table_info(transactions)")}
        tc = type_column(cols)
        expr = f'"{tc}"' if tc else "'expense'"
        rows = con.execute(f"SELECT id,title,amount,category,{expr} AS transaction_type,date FROM transactions ORDER BY date DESC,id DESC").fetchall()
        return jsonify(status="success", transactions=[dict(r) for r in rows])
    finally:
        con.close()

@app.post("/api/transactions")
def add_transaction():
    d = request.get_json(silent=True) or {}
    try:
        amount = float(d.get("amount", 0))
        date.fromisoformat(str(d.get("date", "")))
    except (ValueError, TypeError):
        return jsonify(status="error", message="Enter a valid amount and date (YYYY-MM-DD)."), 400
    title, category = str(d.get("title","")).strip(), str(d.get("category","")).strip()
    kind = str(d.get("transaction_type","expense")).lower()
    if not title or not category or amount <= 0 or kind not in ("income","expense"):
        return jsonify(status="error", message="Enter a title, category, positive amount and valid type."), 400
    con = get_connection()
    try:
        cols = {r["name"] for r in con.execute("PRAGMA table_info(transactions)")}
        aliases = [c for c in ("transaction_type","transactions_type") if c in cols]
        names = ["title","amount","category","date"] + aliases
        vals = [title,amount,category,d["date"]] + [kind]*len(aliases)
        con.execute(f"INSERT INTO transactions ({','.join(chr(34)+n+chr(34) for n in names)}) VALUES ({','.join('?' for _ in vals)})", vals)
        con.commit()
        return jsonify(status="success", message="Transaction added"), 201
    except sqlite3.Error as e:
        return jsonify(status="error", message=str(e)), 500
    finally:
        con.close()

@app.route("/api/transactions/<int:tid>", methods=["PUT","DELETE"])
def transaction_item(tid):
    con = get_connection()
    try:
        if request.method == "DELETE":
            cur = con.execute("DELETE FROM transactions WHERE id=?", (tid,))
        else:
            d = request.get_json(silent=True) or {}
            try:
                amount = float(d.get("amount",0)); date.fromisoformat(str(d.get("date","")))
            except (ValueError,TypeError):
                return jsonify(status="error",message="Enter a valid amount and date."),400
            title,cat=str(d.get("title","")).strip(),str(d.get("category","")).strip()
            kind=str(d.get("transaction_type","expense")).lower()
            if not title or not cat or amount<=0 or kind not in ("income","expense"):
                return jsonify(status="error",message="Check all transaction fields."),400
            cols={r["name"] for r in con.execute("PRAGMA table_info(transactions)")}
            aliases=[c for c in ("transaction_type","transactions_type") if c in cols]
            sets=["title=?","amount=?","category=?","date=?"]+[f'"{c}"=?' for c in aliases]
            vals=[title,amount,cat,d["date"]]+[kind]*len(aliases)+[tid]
            cur=con.execute(f"UPDATE transactions SET {','.join(sets)} WHERE id=?",vals)
        con.commit()
        if cur.rowcount==0: return jsonify(status="error",message="Transaction not found"),404
        return jsonify(status="success",message="Transaction saved")
    finally:
        con.close()

@app.get("/api/dashboard")
def dashboard():
    con=get_connection(readonly=True)
    try:
        cols={r["name"] for r in con.execute("PRAGMA table_info(transactions)")}
        tc=type_column(cols); expr=f'"{tc}"' if tc else "'expense'"
        rows=con.execute(f"SELECT amount,{expr} AS kind,category,date FROM transactions").fetchall()
        inc=sum(float(r["amount"]) for r in rows if str(r["kind"]).lower()=="income")
        exp=sum(float(r["amount"]) for r in rows if str(r["kind"]).lower()=="expense")
        month=date.today().strftime("%Y-%m")
        mi=sum(float(r["amount"]) for r in rows if str(r["kind"]).lower()=="income" and str(r["date"]).startswith(month))
        me=sum(float(r["amount"]) for r in rows if str(r["kind"]).lower()=="expense" and str(r["date"]).startswith(month))
        cats={}
        for r in rows:
            if str(r["kind"]).lower()=="expense": cats[r["category"]]=cats.get(r["category"],0)+float(r["amount"])
        return jsonify(status="success",income=inc,expenses=exp,balance=inc-exp,month_income=mi,month_expenses=me,category_totals=[{"category":k,"amount":v} for k,v in cats.items()])
    finally: con.close()

@app.get("/api/export")
def export():
    con=get_connection(readonly=True)
    try:
        cols={r["name"] for r in con.execute("PRAGMA table_info(transactions)")}
        tc=type_column(cols); expr=f'"{tc}"' if tc else "'expense'"
        rows=con.execute(f"SELECT id,title,amount,category,{expr},date FROM transactions ORDER BY date DESC").fetchall()
        out=io.StringIO(); w=csv.writer(out); w.writerow(["ID","Title","Amount","Category","Type","Date"])
        w.writerows([tuple(r) for r in rows])
        return Response("\\ufeff"+out.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=expense-tracker.csv"})
    finally: con.close()

if __name__=="__main__":
    initialize_database()
    app.run(host="127.0.0.1",port=5000,debug=True)
