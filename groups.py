from flask import Blueprint, request, redirect, render_template, session
from db import get_db_connection

groups_bp = Blueprint("groups", __name__)

# ----------------------------------
# Add a new group
# ----------------------------------
@groups_bp.route("/add-group", methods=["POST"])
def add_group():
    if "user_id" not in session:
        return redirect("/login")

    group_name = request.form["group_name"]
    members = request.form.getlist("members")  # user_ids
    creator_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create group
    cursor.execute(
        "INSERT INTO user_groups (name) VALUES (%s)",
        (group_name,)
    )
    group_id = cursor.lastrowid

    # Add creator to group
    cursor.execute(
        "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
        (group_id, creator_id)
    )

    # Add selected members
    for user_id in members:
        if int(user_id) != creator_id:
            cursor.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, user_id)
            )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/")


# ----------------------------------
# Group detail page
# ----------------------------------
@groups_bp.route("/group/<int:group_id>")
def group_detail(group_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # -------------------------------
    # Group info
    # -------------------------------
    cursor.execute(
        "SELECT * FROM user_groups WHERE id = %s",
        (group_id,)
    )
    group = cursor.fetchone()

    # -------------------------------
    # Group members
    # -------------------------------
    cursor.execute("""
        SELECT u.id, u.name
        FROM group_members gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = %s
    """, (group_id,))
    members = cursor.fetchall()

    # -------------------------------
    # Expenses
    # -------------------------------
    cursor.execute("""
        SELECT 
            e.description,
            e.amount,
            e.paid_by AS paid_by_id,
            u.name AS paid_by
        FROM expenses e
        JOIN users u ON e.paid_by = u.id
        WHERE e.group_id = %s
        ORDER BY e.created_at DESC
    """, (group_id,))
    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    # -------------------------------
    # Settlement logic
    # -------------------------------
    member_count = len(members)
    balances = {m["id"]: 0 for m in members}

    for e in expenses:
        share = e["amount"] / member_count

        for m in members:
            balances[m["id"]] -= share

        balances[e["paid_by_id"]] += e["amount"]

    settlements = []
    for m in members:
        settlements.append({
            "name": m["name"],
            "balance": round(balances[m["id"]], 2)
        })

    # -------------------------------
    # Per-friend balances (for logged-in user)
    # -------------------------------
    current_user_id = session["user_id"]
    my_balance = balances.get(current_user_id, 0)
    per_friend = []

    for m in members:
        if m["id"] == current_user_id:
            continue

        friend_balance = balances[m["id"]]

        # I owe friend
        if my_balance < 0 and friend_balance > 0:
            amount = min(abs(my_balance), friend_balance)
            if amount > 0:
                per_friend.append({
                    "name": m["name"],
                    "type": "you_owe",
                    "amount": round(amount, 2)
                })

        # Friend owes me
        elif my_balance > 0 and friend_balance < 0:
            amount = min(my_balance, abs(friend_balance))
            if amount > 0:
                per_friend.append({
                    "name": m["name"],
                    "type": "owes_you",
                    "amount": round(amount, 2)
                })

    return render_template(
        "group_detail.html",
        group=group,
        members=members,
        expenses=expenses,
        settlements=settlements,
        per_friend=per_friend
    )


# ----------------------------------
# Add expense to group
# ----------------------------------
@groups_bp.route("/group/<int:group_id>/add-expense", methods=["POST"])
def add_group_expense(group_id):
    if "user_id" not in session:
        return redirect("/login")

    description = request.form["description"]
    amount = float(request.form["amount"])
    paid_by = request.form["paid_by"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (group_id, paid_by, amount, description)
        VALUES (%s, %s, %s, %s)
    """, (group_id, paid_by, amount, description))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(f"/group/{group_id}")
