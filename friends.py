from flask import Blueprint, request, redirect, session
from db import get_db_connection

friends_bp = Blueprint("friends", __name__)

# ----------------------------------
# Add existing user as friend to group
# ----------------------------------
@friends_bp.route("/add-friend-to-group/<int:group_id>", methods=["POST"])
def add_friend_to_group(group_id):
    if "user_id" not in session:
        return redirect("/login")

    email = request.form["email"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # find user by email
    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return "User not found"

    # add user to group
    cursor.execute("""
        INSERT IGNORE INTO group_members (group_id, user_id)
        VALUES (%s, %s)
    """, (group_id, user["id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(f"/group/{group_id}")
