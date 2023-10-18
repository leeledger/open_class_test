from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import logging
app = Flask(__name__)
# db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'students.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://luxual:!Dltndk12512@robotncoding.synology.me:3306/class_history'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@127.0.0.1:3306/class_history'
db = SQLAlchemy(app)

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
@app.route('/')
def index():
     return render_template('index.html')
@app.route('/student.html')
def student():
    return render_template('student.html')
@app.route('/student_list.html')
def student_list():
    # 데이터베이스에서 모든 학생 정보를 가져옴
    students = Student.query.all()

    # 'student_list.html' 템플릿으로 결과를 전달하며 렌더링
    return render_template('student_list.html', students=students)

# 과정정보
@app.route('/subject.html')
def subject():
    return render_template('subject.html')
# 과정정보 리스트
@app.route('/subject_list.html')
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
       Student.grade_level,
       Student.name,
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

    records_total = query.count()

    lessons=query.limit(length).offset(start).all()

    data_result= []

    for lesson in lessons:
            data_result.append([lesson.date.strftime('%Y-%m-%d'), 
                                lesson.grade_level, 
                                lesson.name, 
                                lesson.detail_script, 
                                lesson.level if lesson.level else '', 
                                lesson.lesson_detail if lesson.lesson_detail else '', 
                                lesson.teach_comment if lesson.teach_comment else '',
                                lesson.lesson_id] )
    return jsonify({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total - len(data_result),
        'data': data_result
})




# 과정상세 리스트
@app.route('/subject_list_detail.html')
def subject_list_detail():
    # 데이터베이스에서 모든 과정상세 정보를 가져옴
    subject_details = SubjectDetail.query.all()

    # 'subject_list_detail.html' 템플릿으로 결과를 전달하며 렌더링
    return render_template('subject_list_detail.html', 
                           subjectdetails=subject_details, 
                           get_subject_by_id=get_subject_by_id)



# 과정상세정보
@app.route('/subject_detail.html')
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
def edit_subject(subject_id):
    # 데이터베이스에서 해당 ID의 학생 정보를 가져옴
    subject = Subject.query.get(subject_id)

    # 가져온 학생 정보를 가지고 'subject.html' 템플릿으로 이동
    return render_template('subject.html', subject=subject)

    # 브랜치 테스트

@app.route('/subject-detail-update-move/<int:subject_detail_id>')
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
def lesson_update_move(lessonId):
    lesson_detail = Lesson.query.get(lessonId)
    subject_detail = SubjectDetail.query.all()
    attendance = Attendance.query.filter_by(lesson_id=lessonId).first()

    if not attendance:
        return "Attendance not found", 404
    student = Student.query.get(attendance.student_id)

    if not student:
        return "Student not found", 404

    if not lesson_detail:
        return "SubjectDetail not found", 404  # 적절한 에러 메시지와 함께 404 상태 코드 반환
    # return redirect(url_for('lesson_update', lesson_id=lessonId))
    return render_template('lesson_update.html', lesson_detail=lesson_detail, subject_detail=subject_detail, student_name=student.name)

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
@app.route('/lesson_update.html/<int:lesson_id>', methods=['PUT'])
def update_lesson(lesson_id):
    # 요청에서 전달된 데이터 가져오기
    data = request.get_json()
    
    # 데이터베이스에서 해당 수업 조회
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404
    
    # 전달받은 데이터로 수업 정보 업데이트
    lesson.subject_detail_id = data['subject_detail_id']
    lesson.lesson_detail = data['lesson_detail']
    lesson.teach_comment= data['teach_comment']
    lesson.etc= data['etc']

    # 변경 사항 커밋
    db.session.commit()

    # 성공적으로 수정되었다고 가정하고 응답 생성
    response = {'message': 'Success'}
    
    return jsonify(response), 200


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://luxual:!Dltndk12512@robotncoding.synology.me:3306/class_history'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050)
