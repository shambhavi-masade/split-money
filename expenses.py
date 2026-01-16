from flask import Flask, request, Blueprint, redirect
from db import get_db_connection

expenses_bp=Blueprint("expenses",__name__)

@expenses_bp.route("/add_expense",methods=["POST"])
def add_expense():
    description=request.form["description"]
    amount=request.form["amount"]

    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (description, amount) VALUES (%s, %s)",
        (description, amount)
    )
    conn.commit()

    cursor.close()
    conn.close()
    return redirect("/")