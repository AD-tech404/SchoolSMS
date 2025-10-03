from flask import Blueprint, render_template, request, redirect, url_for,flash
import sqlite3, os
from datetime import datetime


class1a_bp = Blueprint('class1a', __name__, url_prefix='/class1a')
folder_path = 'schooldb'
db_file_name = 'class1a.db'

# Create the folder if it doesn't exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Define the full path to the database file
db_path = os.path.join(folder_path, db_file_name)

# Create DB and table if not exists
def init_db():
    if not os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE students (
                    rollno INTEGER PRIMARY KEY,
                    student_name TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    rollno INTEGER,
                    student_name TEXT NOT NULL,
                    total_attendance INTEGER DEFAULT 0,
                    FOREIGN KEY (rollno) REFERENCES students(rollno)
                )
            ''')
            conn.execute(f'''
            CREATE TABLE IF NOT EXISTS pt1 (
                rollno INTEGER PRIMARY KEY,
                student_name TEXT,
                marks INT DEFAULT NULL
            )
        ''')
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS pt2 (
                    rollno INTEGER PRIMARY KEY,
                    student_name TEXT,
                    marks INT DEFAULT NULL
                )
            ''')
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS half_yearly (
                    rollno INTEGER PRIMARY KEY,
                    student_name TEXT,
                    marks INT DEFAULT NULL
                )
            ''')
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS annually (
                    rollno INTEGER PRIMARY KEY,
                    student_name TEXT,
                    marks INT DEFAULT NULL
                )
            ''')



init_db()
# when app.py start then this function is used to render user on teacher section of class1a html page
@class1a_bp.route('/')
def class1a_home():
    with sqlite3.connect(db_path) as conn:
        students = conn.execute('SELECT * FROM students').fetchall()
    return render_template('/class1/class1A/class1a.html', students=students)
# ---------------------------------- home.html page start ----------------------------------
# This function is to add student in class1a db and create student name folder in static folder
@class1a_bp.route('/add', methods=['POST'])
def add_student():
    rollno = request.form['rollno']
    name = request.form['student_name']
    if not rollno or not name:
        flash("Roll No and Name are required.", "danger")
        return redirect(url_for('class1a.class1a_home'))

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute('INSERT INTO students (rollno, student_name) VALUES (?, ?)', (rollno, name))
            conn.execute('INSERT INTO attendance (rollno, student_name, total_attendance) VALUES (?, ?, ?)', (rollno, name, 0))
            conn.execute('INSERT INTO pt1 (rollno, student_name, marks) VALUES (?, ?, ?)', (rollno, name,0))
            conn.execute('INSERT INTO pt2 (rollno, student_name, marks) VALUES (?, ?, ?)', (rollno, name,0))
            conn.execute('INSERT INTO half_yearly (rollno, student_name, marks) VALUES (?, ?, ?)', (rollno, name,0))
            conn.execute('INSERT INTO annually (rollno, student_name, marks) VALUES (?, ?, ?)', (rollno, name,0))
            student_file = f"{rollno}{name}"
            document_path = os.path.join('static', 'class1', 'class1a', student_file)
            os.makedirs(document_path, exist_ok=True)
        flash("Student added successfully.", "success")
    except sqlite3.IntegrityError:
        flash("Roll No already exists.", "warning")

    return redirect(url_for('class1a.class1a_home'))
# This function is to efit students name and if entered wrong then it will change in all tables
@class1a_bp.route('/edit/<int:rollno>', methods=['POST'])
def edit_student(rollno):
    name = request.form['student_name']
    if not name:
        flash("Name cannot be empty.", "danger")
        return redirect(url_for('class1a.class1a_home'))

    with sqlite3.connect(db_path) as conn:
        conn.execute('UPDATE students SET student_name = ? WHERE rollno = ?', (name, rollno))
        conn.execute('UPDATE attendance SET student_name = ? WHERE rollno = ?', (name, rollno))
        conn.execute('UPDATE pt1 SET student_name = ? WHERE rollno = ?', (name, rollno))
        conn.execute('UPDATE pt2 SET student_name = ? WHERE rollno = ?', (name, rollno))
        conn.execute('UPDATE half_yearly SET student_name = ? WHERE rollno = ?', (name, rollno))
        conn.execute('UPDATE annually SET student_name = ? WHERE rollno = ?', (name, rollno))      
    flash("Student updated successfully.", "success")
    return redirect(url_for('class1a.class1a_home'))
# This function is to delete students from all tables of data mean totally clear from db 
@class1a_bp.route('/delete/<int:rollno>')
def delete_student(rollno):
    with sqlite3.connect(db_path) as conn:
        conn.execute('DELETE FROM students WHERE rollno = ?', (rollno,))
        conn.execute('DELETE FROM attendance WHERE rollno = ?', (rollno,))
        conn.execute('DELETE FROM pt1 WHERE rollno = ?', (rollno,))
        conn.execute('DELETE FROM pt2 WHERE rollno = ?', (rollno,))
        conn.execute('DELETE FROM half_yearly WHERE rollno = ?', (rollno,))
        conn.execute('DELETE FROM annually WHERE rollno = ?', (rollno,))
    flash("Student deleted successfully.", "info")
    return redirect(url_for('class1a.class1a_home'))
# ---------------------------------- home.html page ends ----------------------------------

# ---------------------------------- attendance.html page start ----------------------------------
# This function is to mark attendance of student and save it according to date in db 
@class1a_bp.route('/attendance',methods=['GET','POST'])
def attendance():
    todays_date = datetime.now().strftime('%Y_%m_%d')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # fetch column names of table
    cursor.execute("PRAGMA table_info(attendance)")
    columns_info = cursor.fetchall()
    columns = [col[1] for col in columns_info]
    # Check if columns for today exixts in table if mark_attendance triggered 
    if 'mark_attendance' in request.form:
        if todays_date in columns:
            flash("Attendance already registered for today.","warning")
            return redirect(url_for('class1a.attendance'))

        # Add column for today
        cursor.execute(f"ALTER TABLE attendance ADD COLUMN '{todays_date}' TEXT DEFAULT 'Absent'")
        present_rollnos = request.form.getlist('present')
        for rollno in present_rollnos:
            cursor.execute(f"UPDATE attendance SET '{todays_date}' = 'Present', total_attendance = total_attendance + 1 WHERE rollno = ?", (rollno))
        conn.commit()
        flash("Attendance marked successfully.","success")
        return redirect(url_for('class1a.attendance'))
    # Fetch student list for form
    cursor.execute("SELECT rollno, student_name FROM attendance")
    students = cursor.fetchall()

    # Fetch full attendance table
    cursor.execute("SELECT * FROM attendance")
    table_data = cursor.fetchall()
    table_columns = [desc[0] for desc in cursor.description]
    if todays_date in columns:
        cursor.execute(f"SELECT COUNT(*) FROM attendance WHERE `{todays_date}` = 'Present'")
        todays_total = cursor.fetchone()[0]
    else:
        todays_total = 0
    conn.close()

    return render_template('class1/class1A/class1a_attendence.html', students=students,table_data=table_data,columns=table_columns,todays_total=todays_total)

# ---------------------------------- attendance.html page ends ---------------------------------- 

# ---------------------------------- academic.html page start ----------------------------------
# Defined exam types present in application 
exam_types = ['pt1', 'pt2', 'half_yearly', 'annually']

# this function is to create tables for choosen exam type by users if not created in starting 
def create_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for exam in exam_types:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {exam} (
                rollno INTEGER PRIMARY KEY,
                student_name TEXT,
                marks INT DEFAULT NULL
            )
        ''')
        cursor.execute(f"SELECT COUNT(*) FROM {exam}")
        cursor.fetchone()
            
# This function is to add column of subject in selected exam table
def add_column(exam, column_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(f"ALTER TABLE {exam} ADD COLUMN {column_name} TEXT DEFAULT 'null'")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()

# This function is to featch results of selected exam type
def get_results(exam):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {exam}")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return rows, columns

# This function is to enter/update marks of students which is by default null 
def update_row(exam, row_id, form_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    set_parts = []
    values = []
    for key, value in form_data.items():
        if key not in ['rollno', 'update_id', 'exam_type']:
            set_parts.append(f"{key}=?")
            values.append(value)

    values.append(row_id)
    sql = f"UPDATE {exam} SET {', '.join(set_parts)} WHERE rollno=?"
    cursor.execute(sql, values)

    conn.commit()
    conn.close()

# This function is to call above crate table function 
create_tables()

# This function is to render user on academic page when academic tab triggered 
@class1a_bp.route('/class1a_academic', methods=['GET', 'POST'])
def class1a_academic():
    selected_exam = None
    results = []
    columns = []

    if request.method == 'POST':
        selected_exam = request.form.get('exam_type')

        if 'view_results' in request.form:
            results, columns = get_results(selected_exam)

        elif 'add_column' in request.form:
            column_name = request.form.get('column_name')
            if selected_exam and column_name:
                add_column(selected_exam, column_name)
            results, columns = get_results(selected_exam)

        elif 'update_id' in request.form:
            row_id = request.form.get('update_id')
            if selected_exam and row_id:
                update_row(selected_exam, row_id, request.form)
            results, columns = get_results(selected_exam)

    return render_template('class1/class1A/class1a_academic.html',exam_types=exam_types,selected_exam=selected_exam,results=results,columns=columns)

# ---------------------------------- academic.html page ends ----------------------------------

    