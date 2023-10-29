// Create Form에서 Submit 버튼 클릭 시 호출되는 함수
function submitForm() {
  console.log("submitForm() called");
  
  var subjectNameInput = document.getElementById("subject-name");
  var subjectName = subjectNameInput.value;
  
  // 사용자가 아무런 값도 입력하지 않았다면, placeholder로부터 기존의 값을 가져옴
  if (subjectName === '') {
    subjectName = subjectNameInput.placeholder;
    subjectNameInput.value = subjectName;
  }
  // 서버로 전송할 데이터 객체 생성
  var data = {
    'subject-name': subjectName
  };

  // 현재 페이지 URL에서 학생 ID 추출 (수정 모드일 때만 존재)
  var urlParts = window.location.pathname.split('/');
  var subjectId = urlParts[urlParts.length -1];
  
  if (isNaN(subjectId)) { // 학생 ID가 없으면 등록 모드로 간주
    // AJAX 요청 보내기 (POST)
    fetch('/create-subject', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
	.then(response => response.text())
	.then(result => handleResponse(result, false))
	.catch(error => handleError(error));
    
} else { // 과목 ID가 있으면 수정 모드로 간주

    data.subject_id = subjectId; // 데이터 객체에 과목 ID 추가

    // AJAX 요청 보내기 (PUT)
	fetch('/update-subject/' + subjectId, {
	    method: 'PUT',
	    headers: {
	        'Content-Type': 'application/json'
	    },
	    body: JSON.stringify(data)
	})
	.then(response => response.text())
	.then(result => handleResponse(result, true))
	.catch(error => handleError(error));
}
}

// 응답 처리 함수
function handleResponse(result, isUpdate) {
	console.log(result); 

	if (result === "Success") { 
	  alert(isUpdate ? "과목 정보가 성공적으로 수정되었습니다." : "과목 정보가 성공적으로 저장되었습니다.");
	  window.location.href = "/subject_list.html"; 
	} else { 
	  alert(isUpdate ? "수정 실패" : "저장 실패"); 
}
}

// 오류 처리 함수
function handleError(error) {
	console.error('Error:', error);
	alert("오류 발생"); 
}


// 삭제 버튼 클릭 시 호출되는 함수
function deleteSubject(subjectId) {
  var urlParts = window.location.pathname.split('/');
  var subjectId = urlParts[urlParts.length -1];
  
  if (!confirm("정말로 이 과정을 삭제하시겠습니까?")) return;

  fetch('/delete-subject/' + subjectId, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(result => handleDeleteResponse(result))
    .catch(error => handleError(error));
}

// 삭제 응답 처리 함수
function handleDeleteResponse(result) {
  console.log(result);
asdasdsad
  if (result === "Success") { 
    alert("과정 정보가 성공적으로 삭제되었습니다.");
    window.location.href = "/subject_list.html"; 
  } else { 
    alert("삭제 실패"); 
  }
}