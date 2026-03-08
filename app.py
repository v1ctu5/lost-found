from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date

app = Flask(__name__)

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="password",
    database="lostfound",
    ssl_disabled=True
)

cursor = db.cursor()


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            return redirect("/dashboard")

        else:
            return "Invalid Login"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if request.method == "POST":

        college_id = request.form["college_id"]
        item_name = request.form["item_name"]
        location = request.form["location"]
        type = request.form["type"]

        sql = """
        INSERT INTO items
        (college_id,item_name,location,type,status,date_reported)
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        values = (college_id,item_name,location,type,"Not Returned",date.today())

        cursor.execute(sql,values)
        db.commit()


    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type='lost'")
    lost = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type='found'")
    found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status='Returned'")
    returned = cursor.fetchone()[0]

    return render_template("dashboard.html",
        total=total,
        lost=lost,
        found=found,
        returned=returned
    )


# ---------------- VIEW ITEMS ----------------

@app.route("/items")
def items():

    cursor.execute("SELECT * FROM items ORDER BY date_reported DESC")
    data = cursor.fetchall()

    return render_template("view.html",items=data)


# ---------------- SEARCH ----------------

@app.route("/search", methods=["POST"])
def search():

    keyword = request.form["keyword"]

    sql = """
    SELECT * FROM items
    WHERE item_name LIKE %s OR college_id LIKE %s
    """

    val = ("%"+keyword+"%","%"+keyword+"%")

    cursor.execute(sql,val)
    data = cursor.fetchall()

    return render_template("view.html",items=data)


# ---------------- RETURN ITEM ----------------

@app.route("/return/<int:id>")
def mark_returned(id):

    cursor.execute("UPDATE items SET status='Returned' WHERE id=%s",(id,))
    db.commit()

    return redirect("/items")


app.run(debug=True)