from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import re

from model_engine import evaluate_answer
from database import register_user, login_user, get_all_students
from assignment_engine import auto_assign_questions

app = Flask(__name__)
app.secret_key = "AI_COMPETENCY_SYSTEM_2026"

results_store = []


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return redirect(url_for('login'))


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = login_user(username, password)

        if user:
            session['user'] = user[1]
            session['role'] = user[3]

            if user[3] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        success = register_user(username, password, role)

        if success:
            return redirect(url_for('login'))  # ✅ AUTO GO TO LOGIN
        else:
            return render_template("register.html", error="User already exists")

    return render_template("register.html")

# =========================
# NORMALIZER
# =========================
def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]", "", text)
    return text


# =========================
# EVALUATE
# =========================
@app.route('/evaluate', methods=['POST'])
def evaluate():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    question = request.form.get('question')
    answer = request.form.get('answer')
    student = session.get("user")

    # =========================
    # LOAD DATASET
    # =========================
    df = pd.read_excel("ALL_with_features.xlsx")
    df.columns = df.columns.str.strip()

    # =========================
    # FIND QUESTION IN DATASET
    # =========================
    question_norm = normalize_text(question)

    row = df[df["Item"].apply(lambda x: normalize_text(x)) == question_norm]

    if row.empty:
        row = df[df["Item"].astype(str).str.contains(question[:30], na=False)]

    if not row.empty:
        row = row.iloc[0]
        construct = row.get("Construct", "N/A")
        bloom = row.get("Bloom_Level", "N/A")
        dok = row.get("DoK_Level", "N/A")
    else:
        construct = "N/A"
        bloom = "N/A"
        dok = "N/A"

    # =========================
    # MODEL EVALUATION
    # =========================
    result = evaluate_answer(question, answer)

    results_store.append({
        "student": student,
        "question": question,

        "student_answer": result.get("student_answer"),
        "expected_answer": result.get("expected_answer"),
        "feedback": result.get("feedback", []),

        "score": result.get("score", 0),
        "competency": result.get("competency", "Low"),

        # dataset metadata
        "construct": construct,
        "bloom": bloom,
        "dok": dok,

        # analytics
        "readability": result.get("readability", 0),
        "lexical_diversity": result.get("lexical_diversity", 0),
        "avg_sentence_length": result.get("avg_sentence_length", 0)
    })

    return redirect(url_for('student_done'))


# =========================
# STUDENT DONE PAGE
# =========================
@app.route('/student_done')
def student_done():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    return render_template("submitted.html")


# =========================
# TEACHER DASHBOARD
# =========================
@app.route('/teacher')
def teacher_dashboard():

    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    df = pd.read_excel("ALL_with_features.xlsx")
    df.columns = df.columns.str.strip()

    search = request.args.get("search", "")

    # ONLY FILTER BY CONSTRUCT
    questions = []
    if search:
        questions = df[df["Construct"].str.contains(search, case=False, na=False)].to_dict(orient="records")

    students = get_all_students()

    return render_template(
        "teacher_dashboard.html",
        questions=questions,
        students=students,
        search=search
    )


# =========================
# RESULTS PAGE
# =========================
@app.route('/teacher/results')
def teacher_results():

    if session.get("role") != "teacher":
        return redirect(url_for("login"))

    return render_template("result.html", results=results_store)


# =========================
# ASSIGN QUESTION
# =========================
@app.route('/assign/<item_id>', methods=['GET'])
def assign_question(item_id):

    if session.get("role") != "teacher":
        return redirect(url_for("login"))

    student = request.args.get("student")

    df = pd.read_excel("ALL_with_features.xlsx")

    df.loc[df["Item_ID"].astype(str) == str(item_id), "Assigned_To"] = student

    df.to_excel("ALL_with_features.xlsx", index=False)

    return redirect(url_for('teacher_dashboard'))


# =========================
# STUDENT DASHBOARD
# =========================
@app.route('/student')
def student_dashboard():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    username = session.get("user")

    df = pd.read_excel("ALL_with_features.xlsx")
    df.columns = df.columns.str.strip()

    if "Assigned_To" not in df.columns:
        df["Assigned_To"] = ""

    df["Assigned_To"] = df["Assigned_To"].fillna("")

    student_questions = df[
        df["Assigned_To"].astype(str).str.strip() == str(username)
    ].to_dict(orient="records")

    return render_template(
        "student_dashboard.html",
        questions=student_questions,
        username=username
    )


# =========================
# AUTO ASSIGN
# =========================
@app.route("/auto_assign")
def auto_assign():

    if session.get("role") != "teacher":
        return redirect(url_for("login"))

    return auto_assign_questions()


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# =========================
# FORGOT PASSWORD PAGE
# =========================
@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template("forgot_password.html")


# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)