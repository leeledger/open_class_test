// Update Form에서 Submit 버튼 클릭 시 호출되는 함수
function submitForm(mode) {
  console.log("submitForm() called");

  var lesson_detail = document.getElementById("lesson_detail").value;
  var teach_comment = document.getElementById("teach_comment").value;
  var etc = document.getElementById("etc").value;

  var selectedOption = studentId.options[studentId.selectedIndex];
  var studentId = selectedOption.value;

  var selectedOption = subjectDetailId.options[subjectDetailId.selectedIndex];
  var subjectDetailId = selectedOption.value;

   // 디테일 아이디 url로부터 가지고오기
   var urlParts = window.location.pathname.split('/');
   var lessonId = urlParts[urlParts.length -1];

   // 서버로 전송할 데이터 객체 생성
   var data = {
     'lesson_id': parseInt(lessonId),
     'lesson_detail': lesson_detail,
     'teach_comment': teach_comment,
     'etc': etc
   };

   if (mode === 'update') { // 수정 모드

       // 현재 페이지 URL에서 과목 상세 ID 추출 
       var urlParts = window.location.pathname.split('/');
       var lessonId = urlParts[urlParts.length -1];

       fetch('/lesson_update/' + lessonId, {
           method: 'PUT',
           headers: {'Content-Type': 'application/json'},
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
        alert("수업 정보가 성공적으로 수정되었습니다.");
        window.location.href = "/lesson_list.html"; 
    } else { 
        alert("수정 실패"); 
    }
}

// 오류 처리 함수
function handleError(error) {
    console.error('Error:', error);
    alert("오류 발생"); 
}

function deleteSubject(subjectDetailId) {
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
