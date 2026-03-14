from flask import Flask, render_template, request, redirect, g
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    if 'db' not in g:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        if DATABASE_URL:
            g.db = psycopg2.connect(DATABASE_URL)
        else:
            # For Vercel deployment, DATABASE_URL must be set
            raise RuntimeError("DATABASE_URL environment variable is not set. Please configure your Neon Postgres database URL in Vercel environment variables.")
    return g.db

def get_cursor():
    return get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# ---------------- TEARDOWN DATABASE CONNECTION ----------------
@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    return render_template("index.html")


# ---------------- STUDENT REGISTER ----------------
@app.route('/student_register', methods=['GET', 'POST'])
def student_register():

    if request.method == 'POST':

        name = request.form['name']
        reg_no = request.form['reg_no']
        department = request.form['department']
        semester = request.form['semester']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO students (reg_no, name, department, semester, password) VALUES (%s, %s, %s, %s, %s)",
            (reg_no, name, department, semester, password)
        )
        get_db().commit()

        return redirect('/student_login')

    return render_template("student_register.html")


# ---------------- STUDENT LOGIN ----------------
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':

        reg = request.form['reg_no']
        pwd = request.form['password']

        cursor = get_cursor()
        cursor.execute(
            "SELECT * FROM students WHERE reg_no=%s AND password=%s",
            (reg, pwd)
        )

        student = cursor.fetchone()

        if student:
            return redirect('/student_dashboard/' + reg)

    return render_template("student_login.html")


# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student_dashboard/<reg>')
def student_dashboard(reg):

    cursor = get_cursor()
    cursor.execute(
        "SELECT * FROM students WHERE reg_no=%s",
        (reg,)
    )
    student = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM applications WHERE reg_no=%s",
        (reg,)
    )
    apps = cursor.fetchall()

    # Remove duplicate applications for the same subject (if any)
    unique_apps = {}
    for app_row in apps:
        key = (app_row.get("subject_code"), app_row.get("subject_name"))
        if key not in unique_apps:
            unique_apps[key] = app_row
    apps = list(unique_apps.values())

    return render_template(
        "student_dashboard.html",
        student=student,
        applications=apps
    )


# ---------------- APPLY NO DUE ----------------
@app.route('/apply_nodue', methods=['POST'])
def apply():

    reg = request.form['reg_no']

    codes = request.form.getlist('subject_code[]')
    names = request.form.getlist('subject_name[]')
    facs = request.form.getlist('faculty_name[]')

    cursor = get_cursor()
    for i in range(len(codes)):

        cursor.execute(
            "INSERT INTO applications (reg_no,subject_code,subject_name,faculty_name) VALUES (%s,%s,%s,%s)",
            (reg, codes[i], names[i], facs[i])
        )
    
    get_db().commit()

    return redirect('/student_dashboard/' + reg)


# ---------------- STUDENT DELETE APPLICATION ----------------
@app.route('/student_delete_application/<int:id>/<reg>', methods=['GET', 'POST'])
def student_delete_application(id, reg):

    # Delete only this student's application row
    cursor = get_cursor()
    cursor.execute(
        "DELETE FROM applications WHERE id=%s AND reg_no=%s",
        (id, reg)
    )
    get_db().commit()

    return redirect('/student_dashboard/' + reg)


# ---------------- FACULTY REGISTER ----------------
@app.route('/faculty_register', methods=['GET', 'POST'])
def faculty_register():

    if request.method == 'POST':

        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO faculty (name, username, password) VALUES (%s, %s, %s)",
            (name, username, password)
        )
        get_db().commit()

        return redirect('/faculty_login')

    return render_template("faculty_register.html")


# ---------------- FACULTY LOGIN ----------------
@app.route('/faculty_login', methods=['GET', 'POST'])
def faculty_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute(
            "SELECT * FROM faculty WHERE username=%s AND password=%s",
            (username, password)
        )

        faculty = cursor.fetchone()

        if faculty:
            return redirect('/faculty_dashboard')

    return render_template("faculty_login.html")


# ---------------- FACULTY DASHBOARD ----------------
@app.route('/faculty_dashboard')
def faculty_dashboard():

    cursor = get_cursor()
    cursor.execute("SELECT * FROM applications")
    apps = cursor.fetchall()

    # Remove duplicate applications per student & subject
    unique_apps = {}
    for app_row in apps:
        key = (app_row.get("reg_no"), app_row.get("subject_code"))
        if key not in unique_apps:
            unique_apps[key] = app_row
    apps = list(unique_apps.values())

    return render_template(
        "faculty_dashboard.html",
        applications=apps
    )


# ---------------- FACULTY APPROVE ----------------
@app.route('/faculty_approve/<int:id>')
def faculty_approve(id):

    cursor = get_cursor()
    cursor.execute(
        "UPDATE applications SET faculty_status='Approved' WHERE id=%s",
        (id,)
    )
    get_db().commit()

    return redirect('/faculty_dashboard')


# ---------------- FACULTY REJECT ----------------
@app.route('/faculty_reject/<int:id>')
def faculty_reject(id):

    cursor = get_cursor()
    cursor.execute(
        "UPDATE applications SET faculty_status='Rejected' WHERE id=%s",
        (id,)
    )
    get_db().commit()

    return redirect('/faculty_dashboard')


# ---------------- FACULTY DELETE APPLICATION ----------------
@app.route('/faculty_delete_application/<int:id>', methods=['GET', 'POST'])
def faculty_delete_application(id):

    cursor = get_cursor()
    cursor.execute("DELETE FROM applications WHERE id=%s", (id,))
    get_db().commit()

    return redirect('/faculty_dashboard')


# ---------------- HOD REGISTER ----------------
@app.route('/hod_register', methods=['GET', 'POST'])
def hod_register():

    if request.method == 'POST':

        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO hod (name, username, password) VALUES (%s, %s, %s)",
            (name, username, password)
        )
        get_db().commit()

        return redirect('/hod_login')

    return render_template("hod_register.html")


# ---------------- HOD LOGIN ----------------
@app.route('/hod_login', methods=['GET', 'POST'])
def hod_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute(
            "SELECT * FROM hod WHERE username=%s AND password=%s",
            (username, password)
        )

        hod = cursor.fetchone()

        if hod:
            return redirect('/hod_dashboard')

    return render_template("hod_login.html")


# ---------------- HOD DASHBOARD ----------------
@app.route('/hod_dashboard')
def hod_dashboard():

    cursor = get_cursor()
    cursor.execute(
        "SELECT * FROM applications WHERE faculty_status='Approved'"
    )

    apps = cursor.fetchall()

    # Remove duplicate applications per student & subject
    unique_apps = {}
    for app_row in apps:
        key = (app_row.get("reg_no"), app_row.get("subject_code"))
        if key not in unique_apps:
            unique_apps[key] = app_row
    apps = list(unique_apps.values())

    return render_template(
        "hod_dashboard.html",
        applications=apps
    )


# ---------------- HOD APPROVE ----------------
@app.route('/hod_approve/<int:id>')
def hod_approve(id):

    cursor = get_cursor()
    cursor.execute(
        "UPDATE applications SET hod_status='Approved' WHERE id=%s",
        (id,)
    )
    get_db().commit()

    return redirect('/hod_dashboard')


# ---------------- HOD REJECT ----------------
@app.route('/hod_reject/<int:id>')
def hod_reject(id):

    cursor = get_cursor()
    cursor.execute(
        "UPDATE applications SET hod_status='Rejected' WHERE id=%s",
        (id,)
    )
    get_db().commit()

    return redirect('/hod_dashboard')


# ---------------- RUN FLASK APP ----------------
if __name__ == "__main__":
    app.run(debug=True)

# For Vercel deployment
app = app