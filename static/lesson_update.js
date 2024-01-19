

function submitForm(mode) {
    // var studentName = document.getElementById("student_name").value;
    var subjectDetailId = document.getElementById('subjectDetailId');
    var lesson_detail = document.getElementById("lesson_detail").value;
    var teach_comment = document.getElementById("teach_comment").value;
    var etc = document.getElementById("etc").value;
    var teach_id = document.getElementById("teach_id").value;
    var lesson_date = document.getElementById("lessonDatePicker").value;

    var selectedOption = subjectDetailId.options[subjectDetailId.selectedIndex];
    var subjectDetailIdValue = selectedOption.value;

    if (mode === 'update') {
        var urlParts = window.location.pathname.split('/');
        var lessonId = urlParts[urlParts.length - 1];
        var data = {
            'lesson_detail': lesson_detail,
            'teach_comment': teach_comment,
            'etc': etc,
            'subject_detail_id': subjectDetailIdValue,  // 수정
            'teach_id': teach_id,  // And this line
            'lesson_date':lesson_date
        };

        fetch('/lesson-update/' + lessonId, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.text())
        .then(result => handleResponse(result))
        .catch(error => handleError(error));
    }
}
  // 응답 처리 함수
function handleResponse(result) {
console.log(result);

    if (result === "Success") {
        alert("수업 내용 정보가 성공적으로 수정되었습니다.");
        window.location.href = "/lesson_list.html";
    } else {
        alert("수정 실패: " + result); // 실패한 이유를 표시
    }
}
    
    // 오류 처리 함수
function handleError(error) {
    console.error('Error:', error);
    alert("오류 발생"); 
}
    

function deleteLesson() {
    var urlParts = window.location.pathname.split('/');
    var lessonId = urlParts[urlParts.length -1];
    
    if (!confirm("정말로 이 수업을 삭제하시겠습니까?")) return;
  
    fetch('/lesson-delete/' + lessonId, {
      method: 'POST' // Flask에서는 DELETE 메소드를 직접 지원하지 않으므로 POST를 사용합니다.
    })
      .then(response => response.text())
      .then(result => handleDeleteResponse(result))
      .catch(error => console.error('Error:', error));
  }
  
  // 삭제 응답 처리 함수
  function handleDeleteResponse(result) {
    if (result === "Success") { 
      alert("수업 정보가 성공적으로 삭제되었습니다.");
      window.location.href = "/lesson_list.html"; // '.html' 확장자는 필요 없을 수 있습니다.
    } else { 
      alert("삭제 실패"); 
    }
  }