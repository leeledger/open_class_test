$(document).ready(function() {
  $('#lessonForm').on('keydown', function(event) {
    if (event.keyCode === 13 && !event.target.matches('button[type="submit"]') && event.target.tagName !== 'TEXTAREA') {
      event.preventDefault();
    }
  });

  // Fetch students data from the server
  fetch('/api/students')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch students data');
      }
      return response.json();
    })
    .then(data => {
      // Process and display student data
      data.forEach(function(student) {
        $('#students').append(`<option value="${student.name}" data-id="${student.id}" data-grade="${student.grade_level}">`);
      });
      
      // Update grade level when a different student is selected
      $('#studentId').on('input', function() {
        let selectedOption = $(`#students option[value='${$(this).val()}']`);
        var gradeValue = selectedOption.data('grade');
        var gradeText;
        switch (gradeValue) {
          case 1:
              gradeText = "초1";
              break;
          case 2:
              gradeText = "초2";
              break;
          case 3:
              gradeText = "초3";
              break;
          case 4:
              gradeText = "초4";
              break;
          case 5:
              gradeText = "초5";
              break  
          case 6:
              gradeText = "초6";
              break  
          case 7:
              gradeText = "중1";
              break  
          case 8:
              gradeText = "중2";
              break  
          case 9:
              gradeText = "중3";
              break  
          case 10:
              gradeText = "고1";
              break  
          case 11:
              gradeText = "고2";
              break  
          case 12:
              gradeText = "고3";
              break  
          // ... 중1, 중2, ... 고1, 고2 등등 나머지 학년에 대한 코드를 여기에 추가하세요.
          default:
              gradeText = "";
      }
      $('#gradeLevel').text(gradeText);
      });
    })
    .catch(error => console.error('Error:', error));
  
  // Fetch subject details from the server
  fetch('/api/subjects')
     .then(response => {
       if (!response.ok) {
         throw new Error('Failed to fetch subject details');
       }
       return response.json();
     })
     .then(data => {
       // Process and display subject detail data
       data.forEach(function(subject) {
         $('#subjects').append(`<option value="${subject.name} ${subject.detail_script} ${subject.level}" 
                                data-id="${subject.id}"
                                data-name="${subject.name}"
                                >`);
       });

       // Update subject name and level when a different detail script is selected
       $('#subjectDetailId').on('input', function(event) { 
        let inputValue = $(this).val();
        let selectedOption = $("#subjects option").filter(function() { 
          return this.value.indexOf(inputValue) === 0;
        }).first();
      
        if (selectedOption.length > 0) {
          const subjectId = selectedOption.data('id');
        
          fetch(`/api/tooltip?subjectId=${subjectId}`)
            .then(response => {
              if (!response.ok) {
                throw new Error('Failed to fetch tooltip content');
              }
              return response.text();
            })
            .then(tooltipContent => {
              tooltipContent = decodeUnicode(tooltipContent);
              data = JSON.parse(tooltipContent)
              tooltipContent = data.tooltipContent;
              const hiddenTooltip = document.getElementById('hiddenTooltip');
              hiddenTooltip.innerText = tooltipContent;
              
              // 마우스 위치에 표시
              hiddenTooltip.style.top = event.clientY + 10 + 'px';
              hiddenTooltip.style.left = event.clientX + 10 + 'px';
              hiddenTooltip.style.display = 'block';
            })
            .catch(error => console.error('Error:', error));
        } else {
          // 선택된 옵션이 없을 때 툴팁 숨김
          const hiddenTooltip = document.getElementById('hiddenTooltip');
          hiddenTooltip.style.display = 'none';
        }
        $('#subjectName').text(selectedOption.data('name'));
      });
    });
  // Handle form submission
  document.querySelector('#lessonForm')
          .addEventListener("submit", function(e) {
            var lessonDate  = $("#lessonDatePicker").val().trim();
            // 2. Get the current time
            var currentTime = new Date();
            var hours = String(currentTime.getHours()).padStart(2, '0');
            var minutes = String(currentTime.getMinutes()).padStart(2, '0');
            var seconds = String(currentTime.getSeconds()).padStart(2, '0');

            // 3. Combine the date and time
            var combinedDateTime = `${lessonDate} ${hours}:${minutes}:${seconds}`;
            var studentInputValue = $("#studentId").val().trim();
            var subjectDetailInputValue = $("#subjectDetailId").val().trim();
            if (!isValidOption(studentInputValue, 'students') || !isValidOption(subjectDetailInputValue, 'subjects')) { 
              e.preventDefault(); 
              alert("올바른 학생 또는 과목을 선택해주세요.");
              return;
            }
            e.preventDefault();
            let formData = new FormData(this);
            formData.set("date_time", combinedDateTime);
            formData.set("student_id", $(`#students option[value='${$('#studentId').val()}']`).data("id"));
            formData.set("subject_detail_id", $(`#subjects option[value='${$('#subjectDetailId').val()}']`).data("id"));

            // Submit the form using AJAX.
            fetch('/api/add_lessons', { method: 'POST', body: formData })
              .then(response => {
                if (!response.ok) {
                  throw new Error('Failed to add lessons');
                }
                return response.json();
              })
              .then(data => { 
                if (data.message === 'Lesson and attendance added successfully!') { 
                  alert("수업내용 기록에 성공하였습니다!");
                  window.location.href = "/lesson_list.html";
                } else { 
                  throw new Error(data.message);
                }
              })
              .catch(error => console.error("Error:", error));
          });

});
function decodeUnicode(text) {
  return text.replace(/\\u[\dA-Fa-f]{4}/g, match => {
    return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
  });
}
function isValidOption(value, datalistId) {
  var datalistOptions = document.getElementById(datalistId).options;
  
  for (var i = 0; i < datalistOptions.length; i++) {
    if (datalistOptions[i].value === value) {
      return true; // 유효한 옵션이 존재하는 경우 true 반환
    }
  }

  return false; // 유효한 옵션이 없는 경우 false 반환
}
