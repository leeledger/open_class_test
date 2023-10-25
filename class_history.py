from flask import Flask, render_template, request,jsonify,redirect,url_for,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import logging
import os
import shutil
from flask_login import LoginManager,UserMixin, login_user, logout_user, login_required, current_user


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://luxual:!Dltndk12512@robotncoding.synology.me:3306/class_history'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@127.0.0.1:3306/class_history'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '12345'
app.config['UPLOAD_FOLDER'] = 'photos'  # Flask 서버의 photos 폴더

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# 미리 정의된 사용자 아이디 목록
users = {
    'user1': User('user1'),
    'user2': User('user2'),
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username in users:
            user = users[username]
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')

# user_loader 함수
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def start():
    if current_user.is_authenticated:  # 이미 로그인한 사용자인 경우
        return redirect(url_for('index'))  # 대시보드로 리디렉션

    return render_template('login.html')  # 로그인 페이지 표시

# @app.route('/')
# def home():
#     # '/' 경로로 들어오는 요청을 'index.html'로 리디렉션
#     return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return 'Welcome to the dashboard!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'
  
# 학생 모델 정의
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    grade_level = db.Column(db.Integer, nullable=False)
    attendances=db.relationship("Attendance",back_populates="student")

# 과정 모델 정의 
class Subject(db.Model):
    __tablename__ = 'subjects'
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    # lessons=db.relationship("Lesson",back_populates="subject")
# 과정 상세 정의
class SubjectDetail(db.Model):
    __tablename__ = 'subject_detail'
    subject_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    detail_script = db.Column(db.Text)
    level = db.Column(db.Integer)
    

    # Optional: Relationship for easier navigation from Subject to its details
    lessons=db.relationship("Lesson",back_populates="subject_detail")
    subject = db.relationship('Subject', backref=db.backref('details', lazy=True))
    @property
    def subject_name(self):
        return self.subject.name if self.subject else None

# 레슨정의
class Attendance(db.Model):
    __tablename__ = 'attendance'

    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id'))

    student = db.relationship('Student', back_populates='attendances')
    lesson = db.relationship('Lesson', back_populates='attendances')
class Lesson(db.Model):
    __tablename__ = 'lessons'

    lesson_id = db.Column(db.Integer, primary_key=True)
    # subject_detail_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    # subject_detail_id = db.Column(db.Integer, db.ForeignKey('subject_details.subject_detail_id'))  # 수정된 부분
    subject_detail_id = db.Column(db.Integer, db.ForeignKey('subject_detail.subject_detail_id'))  # 수정된 부분
    date = db.Column(db.Date)
    lesson_detail = db.Column(db.Text)
    teach_comment=db.Column(db.Text)
    etc=db.Column(db.Text)
    # student_id = db.Column(db.Integer, db.ForeignKey('attendance.student_id'))
    attendances=db.relationship("Attendance",back_populates="lesson")
    # subject=db.relationship("Subject",back_populates="lessons")
    subject_detail=db.relationship("SubjectDetail",back_populates="lessons")



@app.route('/index.html')
@login_required
def index():
    return render_template('/index.html')
 
@app.route('/student.html')
@login_required
def student():
    return render_template('student.html')
@app.route('/student_list.html')
@login_required
def student_list():
    # 데이터베이스에서 모든 학생 정보를 가져옴
    students = Student.query.all()

    # 'student_list.html' 템플릿으로 결과를 전달하며 렌더링
    return render_template('student_list.html', students=students)

# 과정정보
@app.route('/subject.html')
@login_required
def subject():
    return render_template('subject.html')
# 과정정보 리스트
@app.route('/subject_list.html')
@login_required
def subject_list():
    # 데이터베이스에서 모든 학생 정보를 가져옴
    subjects = Subject.query.all()

    # 'student_list.html' 템플릿으로 결과를 전달하며 렌더링
    return render_template('subject_list.html', subjects=subjects)
def get_subject_by_id(subject_id):
    # Retrieve subject information from the database based on subject_id
    # Implement your logic here
    return Subject.query.get(subject_id)  # Replace with the retrieved subject object or None if not found
# 레슨 리스트
@app.route('/lesson_list.html')
@login_required
def lessons():
    return render_template('lesson_list.html')

@app.route('/api/lessons', methods=['POST'])  # 수정부분
def api_lessons():
    data = request.get_json()

    draw = int(data.get('draw', 1))
    start = int(data.get('start', 0))
    length = int(data.get('length', 10))

    student_name = data.get('studentName')
    lesson_name = data.get('lesson')
    lesson_detail_name = data.get('subjectDetail')
    
    start_date_str = data.get('startDate')  
    end_date_str = data.get('endDate')  
    start_date_obj = datetime.strptime(start_date_str + "T00:00:00", '%Y-%m-%dT%H:%M:%S') if start_date_str else None
    end_date_obj = datetime.strptime(end_date_str + "T23:59:59", '%Y-%m-%dT%H:%M:%S') if end_date_str else None
   # Query all lessons
    
    query = db.session.query(
       Lesson.date,
    #    Student.grade_level,
       Student.name,
       Subject.name.label("subject_name"),
       SubjectDetail.detail_script,
       SubjectDetail.level,
       Lesson.lesson_detail,
       Lesson.teach_comment,
       Lesson.lesson_id,

   ).join(Attendance, Attendance.lesson_id == Lesson.lesson_id)\
     .join(Student, Student.student_id == Attendance.student_id)\
     .join(SubjectDetail, SubjectDetail.subject_detail_id == Lesson.subject_detail_id)\
     .join(Subject, Subject.subject_id == SubjectDetail.subject_id)\
     .order_by(Lesson.date.desc())

   # Apply search filter if search value is provided
    if student_name:
            query = query.filter(Student.name.ilike(f'%{student_name}%'))

    if lesson_name:
            query = query.filter(Subject.name.ilike(f'%{lesson_name}%'))

    if lesson_detail_name:
            query = query.filter(SubjectDetail.detail_script.ilike(f'%{lesson_detail_name}%'))
    if start_date_obj and end_date_obj:
        query=query.filter(Lesson.date.between(start_date_obj,end_date_obj))

    try:
        records_total = query.count()
    except Exception as e:
    # 예외 처리: 데이터베이스 조회 중 에러 발생 시 0으로 설정하거나 다른 동작 수행
        records_total = 0

    lessons=query.limit(length).offset(start).all()

    data_result= []

    for lesson in lessons:
            data_result.append([lesson.date.strftime('%Y-%m-%d'), 
                                lesson.name, 
                                lesson.subject_name, 
                                lesson.detail_script, 
                                lesson.level if lesson.level else '', 
                                lesson.lesson_detail if lesson.lesson_detail else '', 
                                lesson.teach_comment if lesson.teach_comment else '',
                                lesson.lesson_id] )
    return jsonify({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total,
        'data': data_result
})




# 과정상세 리스트
@app.route('/subject_list_detail.html')
@login_required
def subject_list_detail():
    # 데이터베이스에서 모든 과정상세 정보를 가져옴
    subject_details = SubjectDetail.query.all()

    # 'subject_list_detail.html' 템플릿으로 결과를 전달하며 렌더링
    return render_template('subject_list_detail.html', 
                           subjectdetails=subject_details, 
                           get_subject_by_id=get_subject_by_id)



# 과정상세정보
@app.route('/subject_detail.html')
@login_required
def subject_detail():
    subjects = Subject.query.all()  # 모든 과목 정보 가져오기

    return render_template('subject_detail.html', subjects=subjects)

# 과정 상세 생성 API
@app.route('/create-subject-detail', methods=['POST'])
def create_subject_detail():
    # POST 요청으로부터 과정 정보 추출
    data = request.get_json()  # JSON 데이터 추출
    detail_subject_id = data.get('subject_id')  # 수정된 부분
    detail_script = data.get('detail_script')  # 수정된 부분
    detail_level = data.get('level')
    
    # 데이터베이스에 새로운 과정 정보 삽입
    new_subject_detail = SubjectDetail(detail_script=detail_script, subject_id=detail_subject_id, level=detail_level)
    
    try:
        db.session.add(new_subject_detail)
        db.session.commit()
        return "Success"
        
    except Exception as e:
        return str(e)
# 과정 생성 API
@app.route('/create-subject', methods=['POST'])
def create_subject():
    # POST 요청으로부터 과정 정보 추출
    data = request.get_json()  # JSON 데이터 추출
    subject_name = data.get('subject-name')
    
    # 데이터베이스에 새로운 과정 정보 삽입
    new_subject = Subject(name=subject_name)
    
    try:
        db.session.add(new_subject)
        db.session.commit()
        return "Success"
        
    except Exception as e:
        return str(e)

# 과정 정보 수정 API
@app.route('/update-subject/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    # PUT 요청으로부터 학생 정보 추출
    data = request.get_json()  # JSON 데이터 추출
    subject_name = data.get('subject-name')
    # 데이터베이스에서 해당 ID의 학생 정보 가져옴
    subject = Subject.query.get(subject_id)

    if subject is None:
        return "Subject not found", 404

    # 가져온 학생 정보 업데이트
    subject.name = subject_name
    
    try:
        db.session.commit()
        return "Success"

        
    except Exception as e:
        return str(e)
    
@app.route('/edit-subject/<int:subject_id>')
@login_required
def edit_subject(subject_id):
    # 데이터베이스에서 해당 ID의 학생 정보를 가져옴
    subject = Subject.query.get(subject_id)

    # 가져온 학생 정보를 가지고 'subject.html' 템플릿으로 이동
    return render_template('subject.html', subject=subject)

    # 브랜치 테스트

@app.route('/subject-detail-update-move/<int:subject_detail_id>')
@login_required
def subject_detail_update_move(subject_detail_id):
    # 데이터베이스에서 해당 ID의 과목 상세 정보 찾기
    subject_detail = SubjectDetail.query.get(subject_detail_id)

    # 데이터베이스에서 모든 과목 목록 가져오기
    subjects = Subject.query.all()

    if not subject_detail:
        return "SubjectDetail not found", 404  # 적절한 에러 메시지와 함께 404 상태 코드 반환

    return render_template('subject_detail_update.html', subjects=subjects, subject_detail=subject_detail)

@app.route('/subject-detail-delete/<int:subject_detail_id>', methods=['POST'])
def subject_detail_delete(subject_detail_id): 
    subject_detail = SubjectDetail.query.get(subject_detail_id)

    if not subject_detail:
        return "SubjectDetail not found", 404

    db.session.delete(subject_detail)
    db.session.commit()

    return "Success"  # 삭제 완료 후 리다이렉션할 페이지로 이동 (예: 학생 목록 페이지)
# 과정상세 디테일 업데이트



# 과정상세 디테일 수정
@app.route('/edit_subject_detail/<int:subject_detail_id>')
def edit_subject_detail(subject_detail_id):
    # 데이터베이스에서 해당 ID의 과정 디테일 정보를 가져옴
    subject_detail = SubjectDetail.query.get(subject_detail_id)

    if subject_detail is None:
        return "Subject detail not found", 404

    subjects = Subject.query.all()  # 모든 과목 정보 가져오기

    return render_template('subject_detail.html', subjects=subjects, subjectdetail=subject_detail)


@app.route('/edit-student/<int:student_id>')
def edit_student(student_id):
    # 데이터베이스에서 해당 ID의 학생 정보를 가져옴
    student = Student.query.get(student_id)
    
    # 가져온 학생 정보를 가지고 'student.html' 템플릿으로 이동
    return render_template('student.html', student=student)
# 학생 정보 수정 API
@app.route('/update-student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    # PUT 요청으로부터 학생 정보 추출
    data = request.get_json()  # JSON 데이터 추출
    student_name = data.get('student-name')
    grade_level = data.get('grade-level')

    # 데이터베이스에서 해당 ID의 학생 정보 가져옴
    student = Student.query.get(student_id)

    if student is None:
        return "Student not found", 404

    # 가져온 학생 정보 업데이트
    student.name = student_name
    student.grade_level = grade_level

    try:
        db.session.commit()
        return "Success"

        
    except Exception as e:
        return str(e)
    
# 학생 정보 삭제 라우트
@app.route('/delete-student/<int:student_id>', methods=['DELETE'])
def deleteStudent(student_id):
    student = Student.query.get(student_id)  # 학생 객체 조회

    if student:
        db.session.delete(student)  # 학생 객체 삭제
        db.session.commit()  # 변경 사항 커밋

        return "Success"  # 삭제 완료 후 리다이렉션할 페이지로 이동 (예: 학생 목록 페이지)
    
    return "해당하는 학생을 찾을 수 없습니다."  # 예외 처리 등 필요한 로직 추가

# 과정 정보 삭제 라우트
@app.route('/delete-subject/<int:subject_id>', methods=['DELETE'])
def deleteSubject(subject_id):
    subject = Subject.query.get(subject_id)  # 학생 객체 조회

    if subject:
        db.session.delete(subject)  # 학생 객체 삭제
        db.session.commit()  # 변경 사항 커밋

        return "Success"  # 삭제 완료 후 리다이렉션할 페이지로 이동 (예: 학생 목록 페이지)
    
    return "해당하는 과정을 찾을 수 없습니다."  # 예외 처리 등 필요한 로직 추가
    
# 학생 생성 API
@app.route('/create-student', methods=['POST'])
def create_student():
    # POST 요청으로부터 학생 정보 추출
    data = request.get_json()  # JSON 데이터 추출
    student_name = data.get('student-name')
    grade_level = data.get('grade-level')

    # 데이터베이스에 새로운 학생 정보 삽입
    new_student = Student(name=student_name, grade_level=grade_level)
    
    try:
        db.session.add(new_student)
        db.session.commit()
        return "Success"

        
    except Exception as e:
        return str(e)

@app.route('/lesson.html')
@login_required
def lesson():
    return render_template('lesson.html')
@app.route('/subject-detail-update/<int:subject_detail_id>', methods=['PUT'])
def subject_detail_update(subject_detail_id):
    # POST 요청으로부터 과정 정보 추출
    data = request.get_json()  # JSON 데이터 추출
    detail_subject_id = data.get('subject_id') 
    detail_script = data.get('detail_script')
    detail_level = data.get('level')
    
    # 데이터베이스에서 해당 ID의 과정 상세 정보 찾기
    subject_detail = SubjectDetail.query.filter_by(subject_detail_id=subject_detail_id).first()
    
    if subject_detail:
        try:
            # 데이터베이스의 해당 레코드 수정
            subject_detail.subject_id = detail_subject_id
            subject_detail.detail_script = detail_script
            subject_detail.level = detail_level

            db.session.commit()
            
            return "Success"
        
        except Exception as e:
            return str(e)
            
    else:
        return "SubjectDetail not found", 404  # 적절한 에러 메시지와 함께 404 상태 코드 반환
@app.route('/lesson_update_move/<int:lessonId>') # 수정 부분
@login_required
def lesson_update_move(lessonId):
    lesson_detail = Lesson.query.get(lessonId)
    subject_detail = SubjectDetail.query.all()
    attendance = Attendance.query.filter_by(lesson_id=lessonId).first()
    subject_name = Subject.name
    if not attendance:
        return "Attendance not found", 404
    student = Student.query.get(attendance.student_id)

    if not student:
        return "Student not found", 404

    if not lesson_detail:
        return "SubjectDetail not found", 404  # 적절한 에러 메시지와 함께 404 상태 코드 반환
    
    return render_template('lesson_update.html', lesson_detail=lesson_detail, subject_detail=subject_detail, student_name=student.name, subject_name = subject_name) #정상작동
    

@app.route('/api/add_lessons', methods=['POST'])
def add_lesson():
    # Get data from the form
    subject_detail_id = request.form.get('subject_detail_id')
    lesson_detail = request.form.get('lesson_detail')
    teach_comment = request.form.get('teach_comment')
    etc = request.form.get('etc')

    # Get the current server time
    date = datetime.now()

    # Create a new lesson object and add it to the database
    lesson = Lesson(subject_detail_id=subject_detail_id, date=date, 
                    lesson_detail=lesson_detail, teach_comment=teach_comment,
                    etc=etc)
    
    db.session.add(lesson)
    db.session.commit()

   # Retrieve the generated lesson_id after committing to the database
    generated_lesson_id = lesson.lesson_id

   # Get data for attendance from the form or elsewhere as needed
    student_id = request.form.get('student_id')

   # Create a new attendance object with the retrieved lesson id and add it to the database
    attendance = Attendance(student_id=student_id, lesson_id=generated_lesson_id)
   
    db.session.add(attendance)
    db.session.commit()

    return jsonify({'message': 'Lesson and attendance added successfully!'}), 201
@app.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.order_by(Student.name).all()
    student_list = []
    
    for student in students:
        student_list.append({
            'id': student.student_id,
            'name': student.name,
            'grade_level': student.grade_level
        })

    return jsonify(student_list)

@app.route('/api/subjects/update', methods=['GET'])
def get_subjects_update():
    subjects = SubjectDetail.query.join(Subject, Subject.subject_id == SubjectDetail.subject_id).order_by(Subject.name).all()
    subject_list = []

    for subject in subjects:
        subject_list.append({
            'id': subject.subject_detail_id, # 문제부분
            'detail_script': subject.detail_script,
            'name': subject.subject_name,  # assuming there is a name field in the Subject model
            'level': subject.level
        })

    return jsonify(subject_list)

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = SubjectDetail.query.join(Subject, Subject.subject_id == SubjectDetail.subject_id).order_by(Subject.name).all()
    subject_list = []

    for subject in subjects:
        subject_list.append({
            'id': subject.subject_detail_id, # 문제부분
            'detail_script': subject.detail_script,
            'name': subject.subject_name,  # assuming there is a name field in the Subject model
            'level': subject.level
        })

    return jsonify(subject_list)

@app.route('/api/lessonSearch', methods=['POST'])
def lesson_search():
    data = request.get_json()

    student_name = data.get('studentName')
    lesson_name = data.get('lesson')
    lesson_detail_name = data.get('lessonDetail')

    Session = sessionmaker(bind=db.engine)
    session = Session()

    query = """
        SELECT lessons.date, students.grade_level, students.name AS student_name,
            subject_detail.detail_script AS detail_script,
            subject_detail.level AS level,
            lessons.lesson_detail,
            lessons.teach_comment
        FROM lessons
        JOIN attendance ON lessons.lesson_id = attendance.lesson_id
        JOIN students ON attendance.student_id = students.student_id
        JOIN subject_detail ON lessons.subject_detail_id = subject_detail.subject_detail_id
        JOIN subjects ON subject_detail.subject_id = subjects.subject_id"""

    # WHERE 절을 추가하기 위한 리스트 초기화 
    where_clause_list = []

    if student_name:
        where_clause_list.append("students.name LIKE :student_name")

    if lesson_name:
        where_clause_list.append("subjects.name LIKE :lesson_name")

    if lesson_detail_name:
        where_clause_list.append("subject_detail.detail_script LIKE :lesson_detail_name")

    # WHERE 절이 있으면 쿼리에 추가 
    if where_clause_list:
        query += " WHERE " + " AND ".join(where_clause_list)

    query_result= session.execute(text(query), {
        'student_name': f"%{student_name}%" if student_name else None,
        'lesson_name': f"%{lesson_name}%" if lesson_name else None,
        'lesson_detail_name': f"%{lesson_detail_name}%" if lesson_detail_name else None,
    })

    result_list = []
        
    for row in query_result:
        result_list.append([
            row.date,
            row.grade_level,
            row.student_name,
            row.detail_script if row.detail_script else None,
            row.level if row.level else None,
            row.lesson_detail,
            row.teach_comment
        ])
        
# 수업정보 업데이트
@app.route('/lesson-update/<int:lessonId>', methods=['PUT'])
def lesson_update(lessonId):
    # 요청에서 전달된 데이터 가져오기
    data = request.get_json()
    
    # 데이터베이스에서 해당 수업 조회
    lesson = Lesson.query.get(lessonId)

    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404
    
    try:
        # 전달받은 데이터로 수업 정보 업데이트
        # lesson.lesson_id = data['lesson_id']
        lesson.subject_detail_id = data['subject_detail_id']
        lesson.lesson_detail = data['lesson_detail']
        lesson.teach_comment = data['teach_comment']
        lesson.etc = data['etc']
        print(data)
        # 변경 사항 커밋
        db.session.commit()

        # 성공적으로 수정되었다고 가정하고 응답 생성
        return "Success"
    except Exception as e:
        # 커밋 중에 오류 발생 시 오류 메시지 반환
        return jsonify({'message': str(e)}), 500

    # 성공적으로 수정되었다고 가정하고 응답 생성
    
# /lesson-delete/
@app.route('/lesson-delete/<int:lessonId>', methods=['POST'])
def lesson_delete(lessonId): 
    lesson = Lesson.query.get(lessonId)
        
    if not lesson:
        return "Lesson not found", 404
    try:
        # 동일 lesson_id를 가진 Attendance 항목 삭제
        attendance_entries = Attendance.query.filter_by(lesson_id=lessonId).all()
        for attendance_entry in attendance_entries:
            db.session.delete(attendance_entry)

        db.session.delete(lesson)
        db.session.commit()
        return "Success"  
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
# 레포트 자료 만들기 라우팅함수
@app.route('/lesson_report.html')
@login_required
def lesson_report():
    return render_template('lesson_report.html')


@app.route('/api/report', methods=['GET', 'POST'])
@login_required
def report():
   if request.method == 'POST':
       data = request.get_json()
       
       # 전달받은 데이터를 변수에 담아서 처리
       selectedRowsData = data['data']
       start_date = data['startDate']
       end_date = data['endDate']

       # Store data in session
       session['data'] = selectedRowsData
       session['startDate'] = start_date
       session['endDate'] = end_date

       return jsonify(success=True)  # Return JSON response

   else:
      return render_template('lesson_report.html')
# @app.route('/report_sample')
# def report_sample():
#     # Get data from session
#     selectedRowsData = session.get('data')

#     # Extract the actual list data from the dictionary
#     if selectedRowsData and 'data' in selectedRowsData:
#         selectedRowsData = selectedRowsData['data']

#     start_date = session.get('startDate')
#     end_date = session.get('endDate')

#      # Check if the data is in the correct format (list of lists)
#     if isinstance(selectedRowsData, list) and all(isinstance(row, list) for row in selectedRowsData):
#         pass  # If the data is already in the correct format, no need to change anything
#     else:
#         selectedRowsData = [[item] for item in selectedRowsData]  # If not convert it into a list of lists

#     return render_template('report_sample.html', data=selectedRowsData,
#                         startDate=start_date,
#                         endDate=end_date)
@app.route('/report_sample')
def report_sample():
    # Get data from session
    selectedRowsData = session.get('data')

    # Extract the actual list data from the dictionary
    if selectedRowsData and 'data' in selectedRowsData:
        selectedRowsData = selectedRowsData['data']

    start_date = session.get('startDate')
    end_date = session.get('endDate')

     # Check if the data is in the correct format (list of lists)
    if isinstance(selectedRowsData, list) and all(isinstance(row, list) for row in selectedRowsData):
        pass  # If the data is already in the correct format, no need to change anything
    else:
        selectedRowsData = [[item] for item in selectedRowsData]  # If not convert it into a list of lists

    # photo_directory = r"\\192.168.0.225\학원공유"  # 파일 경로 설정 윈도우 기준
    photo_directory = '/volume1/학원공유'  # 리눅스 환경

    filtered_photos = []

    for row_data in selectedRowsData:
        student_name = row_data[1]  # 학생 이름은 첫 번째 열로 가정합니다.
        student_folder_path = os.path.join(photo_directory, student_name)

        if not os.path.exists(student_folder_path):  # 학생 폴더가 존재하지 않으면 생성합니다.
            os.makedirs(student_folder_path)

        count = 0
        for filename in os.listdir(student_folder_path):
            if filename.endswith(".jpg") and student_name in filename:
                _, name, _ = filename.split("_")  # creation_date 부분은 사용하지 않음
                if name == student_name and start_date <= end_date:
                    photo_source_path = os.path.join(student_folder_path, filename)
                    photo_dest_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    shutil.copy2(photo_source_path, photo_dest_path)  # 파일 복사
                    
                    filtered_photos.append(filename)  # 복사된 파일명 추가
                    
                    count += 1
                    if count >= 6:  # 최대 사진 개수인 6개까지만 가져옵니다.
                        break

    return render_template('report_sample.html', data=selectedRowsData,
                           startDate=start_date,
                           endDate=end_date,
                           photos=filtered_photos)

@app.route('/photos/<path:filename>')
def photos(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_all_photos')
def delete_all_photos():
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'])  # 폴더를 다시 생성합니다
    return redirect(url_for('report_sample'))

# @app.route('/api/report', methods=['GET', 'POST'])
# def report():
#     if request.method == 'POST':
#         selectedRowsData = request.get_json()
#         # 전달받은 데이터를 변수에 담아서 처리
#         print(selectedRowsData)
#         return redirect(url_for('report_sample', data=selectedRowsData))
#     else:
#         return render_template('lesson_report.html')
@app.route('/api/tooltip', methods = ['GET'])
def tooltip():
    
    subject_id = request.args.get('subjectId')

    # SQLAlchemy를 사용하여 데이터베이스에서 데이터 조회
    result = Lesson.query.filter_by(subject_detail_id=subject_id).order_by(Lesson.date.desc()).limit(5).all()

    if result:
        # 결과가 있으면 tooltip_content를 생성
        tooltip_content = "\n".join(lesson.lesson_detail for lesson in result)
        return jsonify({'tooltipContent': tooltip_content})
    else:
        return jsonify({'tooltipContent': '이전 수업 내용이 없습니다'})  # 레코드가 없을 때 빈 문자열 반환

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging 
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
if __name__ == '__main__':
    app.run('0.0.0.0',debug=True, port=5050)

