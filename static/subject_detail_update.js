// Update Form에서 Submit 버튼 클릭 시 호출되는 함수
function submitForm(mode) {
    console.log("submitForm() called");
    
    var subjectIdSelect = document.getElementById("subject-name");
    var detailScriptInput = document.getElementById("detail_script");
    var detailScript = detailScriptInput.value;
  
    var selectedOption = subjectIdSelect.options[subjectIdSelect.selectedIndex];
    var subjectId = selectedOption.value;
  
     // level 정보 처리 추가 
     var levelInput = document.getElementById('level');
     var level= levelInput.value;
     var urlParts = window.location.pathname.split('/');
     var subjectDetailId = urlParts[urlParts.length -1];
  // 서버로 전송할 데이터 객체 생성
  var data = {
    'subject_id': parseInt(subjectId),
    'detail_script': detailScript,
    'level': parseInt(level)   // assuming that the level is an integer
  };
  
  if (mode === 'update') { // 수정 모드
  
       // 현재 페이지 URL에서 과목 상세 ID 추출 
       var urlParts = window.location.pathname.split('/');
       var subjectDetailId = urlParts[urlParts.length -1];
  
       fetch('/subject-detail-update/' + subjectDetailId, {
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
  alert("과목 상세 정보가 성공적으로 수정되었습니다.");
  window.location.href = "/subject_list_detail.html"; 
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
    var urlParts = window.location.pathname.split('/');
    var subjectId = urlParts[urlParts.length -1];
    
    if (!confirm("정말로 이 과정을 삭제하시겠습니까?")) return;
  
    fetch('/subject-detail-delete/' + subjectDetailId, {
      method: 'POST' // Flask에서는 DELETE 메소드를 직접 지원하지 않으므로 POST를 사용합니다.
    })
      .then(response => response.text())
      .then(result => handleDeleteResponse(result))
      .catch(error => console.error('Error:', error));
  }
  
  // 삭제 응답 처리 함수
  function handleDeleteResponse(result) {
    if (result === "Success") { 
      alert("과정 정보가 성공적으로 삭제되었습니다.");
      window.location.href = "/subject_list_detail.html"; // '.html' 확장자는 필요 없을 수 있습니다.
    } else { 
      alert("삭제 실패"); 
    }
  }