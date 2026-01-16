from flask import Flask, render_template, redirect, session
from db import get_db_connection

from expenses import expenses_bp
from groups import groups_bp
from auth import auth_bp

app = Flask(__name__)
app.secret_key = "super-secret-key"  # move to env later

# -------------------------------
# Register blueprints
# -------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(expenses_bp)

# -------------------------------
# Dashboard
# -------------------------------
@app.route("/")
def index():
    # 🔒 Auth protection
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # -------------------------------
    # Fetch groups user is part of
    # -------------------------------
    cursor.execute("""
        SELECT ug.id, ug.name
        FROM user_groups ug
        JOIN group_members gm ON ug.id = gm.group_id
        WHERE gm.user_id = %s
    """, (user_id,))
    groups = cursor.fetchall()

    # -------------------------------
    # Fetch recent expenses (only from user's groups)
    # -------------------------------
    cursor.execute("""
        SELECT e.description, e.amount, ug.name AS group_name
        FROM expenses e
        JOIN user_groups ug ON e.group_id = ug.id
        JOIN group_members gm ON gm.group_id = ug.id
        WHERE gm.user_id = %s
        ORDER BY e.created_at DESC
        LIMIT 10
    """, (user_id,))
    expenses = cursor.fetchall()

    # -------------------------------
    # 🔥 Fetch friends (users who share groups with me)
    # -------------------------------
    cursor.execute("""
        SELECT DISTINCT u.id, u.name
        FROM users u
        JOIN group_members gm ON u.id = gm.user_id
        WHERE gm.group_id IN (
            SELECT group_id
            FROM group_members
            WHERE user_id = %s
        )
        AND u.id != %s
    """, (user_id, user_id))
    friends = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        groups=groups,
        expenses=expenses,
        friends=friends,              # ✅ added
        user_name=session.get("user_name")
    )


# -------------------------------
# Logout
# -------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
