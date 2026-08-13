from flask import Flask, flash, render_template, request, redirect, session, url_for
from db import get_connection
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = "focus123"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)


@app.route("/")
def home():
    return render_template("index.html")


# @app.route('/')
# def home():
#     if 'student_id' not in session:
#         flash("Please register first to access....!")
#         return redirect(url_for('student_register'))
#     return render_template('index.html')

# STUDENT
@app.route("/student_register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        course = request.form["course"]
        password = request.form["password"]

        con = get_connection()
        cursor = con.cursor()

        sql = """
        INSERT INTO student
        (name, mobile, email, course, password)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (name, mobile, email, course, password))

        con.commit()

        cursor.close()
        con.close()

        # Redirect to payment page
        return redirect(url_for("buy", course=course))

    # GET request
    course = request.args.get("course", "")

    return render_template(
        "student_register.html",
        course=course
    )

@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM student WHERE email=%s AND password=%s",
            (email, password)
        )

        student = cursor.fetchone()

        cursor.close()
        con.close()

        if student:
            session["student"] = student["email"]

            return redirect("/student_dashboard")

        else:
            flash("❌ Invalid Email or Password")
            return redirect(url_for("student_login"))

    return render_template("student_login.html")

@app.route("/student_dashboard")
def student_dashboard():

    if "student" not in session:
        return redirect("/student_login")

    return render_template("student_dashboard.html")

@app.route("/student_profile")
def student_profile():

    if "student" not in session:
        return redirect("/student_login")

    email = session["student"]

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM student WHERE email=%s",
        (email,)
    )

    student = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template(
        "student_profile.html",
        student=student
    )


@app.route("/my_courses")
def my_courses():

    if "student" not in session:
        return redirect("/student_login")

    email = session["student"]

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute(
        "SELECT course FROM student WHERE email=%s",
        (email,)
    )

    courses = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("my_courses.html", courses=courses)


@app.route("/logout")
def logout():

    session.pop("student", None)

    return redirect("/student_login")

# ADMIN MODULE

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM admin WHERE email=%s AND password=%s",
            (email, password)
        )

        admin = cursor.fetchone()

        cursor.close()
        con.close()

        if admin:
            session["admin"] = admin["email"]
            return redirect("/admin_dashboard")
        else:
            flash("❌ Invalid Email or Password")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin_login")

    return render_template("admin_dashboard.html")

@app.route("/view_students")
def view_students():

    if "admin" not in session:
        return redirect("/admin_login")

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("view_students.html", students=students)

@app.route("/update_student/<int:id>", methods=["GET", "POST"])
def update_student(id):

    if "admin" not in session:
        return redirect("/admin_login")

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        course = request.form["course"]

        cursor.execute("""
            UPDATE student
            SET name=%s, mobile=%s, email=%s, course=%s
            WHERE id=%s
        """, (name, mobile, email, course, id))

        con.commit()

        cursor.close()
        con.close()

        return redirect("/view_students")

    cursor.execute("SELECT * FROM student WHERE id=%s", (id,))
    student = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template("update_student.html", student=student)

@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "admin" not in session:
        return redirect("/admin_login")

    con = get_connection()
    cursor = con.cursor()

    cursor.execute("DELETE FROM student WHERE id=%s", (id,))
    con.commit()

    cursor.close()
    con.close()

    return redirect("/view_students")

@app.route("/admin_add_staff", methods=["GET", "POST"])
def admin_add_staff():

    if "admin" not in session:
        return redirect("/admin_login")

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO staff(name, email, password)
            VALUES(%s, %s, %s)
        """, (name, email, password))

        con.commit()

        cursor.close()
        con.close()

        return redirect("/admin_dashboard")

    return render_template("admin_add_staff.html")

@app.route("/view_staff")
def view_staff():

    if "admin" not in session:
        return redirect("/admin_login")

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM staff")
    staffs = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("view_staff.html", staffs=staffs)

@app.route("/admin_update_staff/<int:id>", methods=["GET", "POST"])
def admin_update_staff(id):

    if "admin" not in session:
        return redirect("/admin_login")

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("""
            UPDATE staff
            SET name=%s,
                email=%s,
                password=%s
            WHERE id=%s
        """,(name,email,password,id))

        con.commit()

        cursor.close()
        con.close()

        return redirect("/view_staff")

    cursor.execute("SELECT * FROM staff WHERE id=%s",(id,))
    staff = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template(
        "admin_update_staff.html",
        staff=staff
    )
    
@app.route("/admin_delete_staff/<int:id>")
def admin_delete_staff(id):

    if "admin" not in session:
        return redirect("/admin_login")

    con = get_connection()
    cursor = con.cursor()

    cursor.execute(
        "DELETE FROM staff WHERE id=%s",
        (id,)
    )

    con.commit()

    cursor.close()
    con.close()

    return redirect("/view_staff")

    # STAFF

@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM staff WHERE email=%s AND password=%s",
            (email, password)
        )

        staff = cursor.fetchone()

        cursor.close()
        con.close()

        if staff:
            session["staff"] = staff["email"]
            return redirect("/staff_dashboard")

        flash("Invalid Email or Password")
        return redirect("/staff_login")
    
    return render_template("staff_login.html")

@app.route("/staff_dashboard")
def staff_dashboard():

    if "staff" not in session:
        return redirect("/staff_login")

    return render_template("staff_dashboard.html")

@app.route("/staff_view_students")
def staff_view_students():

    if "staff" not in session:
        return redirect("/staff_login")

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("staff_view_students.html", students=students)

@app.route("/staff_add_student", methods=["GET", "POST"])
def staff_add_student():

    if "staff" not in session:
        return redirect("/staff_login")

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        course = request.form["course"]
        password = request.form["password"]

        con = get_connection()
        cursor = con.cursor()

        cursor.execute(
            "INSERT INTO student(name,mobile,email,course,password) VALUES(%s,%s,%s,%s,%s)",
            (name, mobile, email, course, password)
        )

        con.commit()

        cursor.close()
        con.close()

        return redirect("/staff_view_students")

    return render_template("staff_add_student.html")

@app.route("/staff_update_student/<int:id>", methods=["GET", "POST"])
def staff_update_student(id):

    if "staff" not in session:
        return redirect("/staff_login")

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        course = request.form["course"]

        cursor.execute("""
        UPDATE student
        SET name=%s, mobile=%s, email=%s, course=%s
        WHERE id=%s
        """, (name, mobile, email, course, id))

        con.commit()

        cursor.close()
        con.close()

        return redirect("/staff_view_students")

    cursor.execute("SELECT * FROM student WHERE id=%s", (id,))
    student = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template("staff_update_student.html", student=student)

@app.route("/staff_delete_student/<int:id>")
def staff_delete_student(id):

    if "staff" not in session:
        return redirect("/staff_login")

    con = get_connection()
    cursor = con.cursor()

    cursor.execute("DELETE FROM student WHERE id=%s", (id,))
    con.commit()

    cursor.close()
    con.close()

    return redirect("/staff_view_students")

@app.route("/staff_logout")
def staff_logout():

    session.pop("staff", None)

    return redirect("/staff_login")

#nav bar routes

@app.route("/about")
def about():
    return render_template("aboutus.html")

@app.route("/courses")
def courses():
    return render_template("courses.html")

# @app.route('/courses')
# def courses():
#     if 'student_id' not in session:
#         flash("Please register first to access courses.")
#         return redirect(url_for('student_register'))
#     return render_template('courses.html')

@app.route("/contactus", methods=["GET", "POST"])
def contactus():
  
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        msg = Message(
            subject="New Contact Form Message",
            sender=app.config['MAIL_USERNAME'],
            recipients=['rushikeshkale509@gmail.com']
        )

        msg.body = f"""
Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
"""

        mail.send(msg)

        flash("Message sent successfully!")

        return redirect("/contactus")

    return render_template("contactus.html")

@app.route("/login")
def login():
    return render_template("student_login.html")

@app.route("/course/<course>")
def course_details(course):
    return render_template("course_details.html", course=course)

@app.route("/buy/<course>")
def buy(course):

    prices = {
        "Python Programming": "4999",
        "Java Programming": "5499",
        "Web Development": "6999",
        "C Programming": "3999",
        "C++ Programming": "4499",
        "MS Office": "2999",
        "Tally Prime": "3499",
        "MySQL Database": "3999"
    }

    amount = prices.get(course, "0")

    return render_template(
        "payment.html",
        course=course,
        amount=amount
    )

@app.route("/payment_success", methods=["POST"])
def payment_success():

    name = request.form["name"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    course = request.form["course"]
    amount = request.form["amount"]
    payment_method = request.form["payment_method"]

    return render_template(
        "payment_success.html",
        name=name,
        email=email,
        mobile=mobile,
        course=course,
        amount=amount,
        payment_method=payment_method
    )


        #send message




if __name__ == "__main__":
    app.run(debug=True)
