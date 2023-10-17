// Create Form에서 Submit 버튼 클릭 시 호출되는 함수
function submitForm() {
  console.log("submitForm() called");
  
  var subjectIdSelect = document.getElementById("subject-name");
  var detailScriptInput = document.getElementById("detail_script");
  var detailScript = detailScriptInput.value;

  var selectedOption = subjectIdSelect.options[subjectIdSelect.selectedIndex];
  var subjectId = selectedOption.value;

   // level 정보 처리 추가 
   var levelInput = document.getElementById('level');
   var level= levelInput.value;
  
// 서버로 전송할 데이터 객체 생성
var data = {
  'subject_id': parseInt(subjectId),
  'detail_script': detailScript,
  'level': parseInt(level)   // assuming that the level is an integer
};

fetch('/create-subject-detail', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
})
.then(response => response.text())
.then(result => handleResponse(result))
.catch(error => handleError(error));
}

// 응답 처리 함수
function handleResponse(result) {
console.log(result); 

if (result === "Success") { 
alert("과목 상세 정보가 성공적으로 저장되었습니다.");
window.location.href = "/subject_list_detail.html"; 
} else { 
alert("저장 실패"); 
}
}

// 오류 처리 함수
function handleError(error) {
console.error('Error:', error);
alert("오류 발생"); 
}
