$(document).ready(function() {
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
        $('#gradeLevel').text(selectedOption.data('grade'));
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
        $('#subjectDetailId').on('input', function() { 
          let inputValue = $(this).val();
          let selectedOption = $("#subjects option").filter(function() { 
              return this.value.indexOf(inputValue) === 0;
          }).first();
          
          $('#subjectName').text(selectedOption.data('name'));
        });
     })
     .catch(error => console.error('Error:', error));
  
  // Handle form submission
  document.querySelector('#lessonForm')
          .addEventListener("submit", function(e) {

            var studentInputValue = $("#studentId").val().trim();
            var subjectDetailInputValue = $("#subjectDetailId").val().trim();

            if (!isValidOption(studentInputValue, 'students') || !isValidOption(subjectDetailInputValue, 'subjects')) { 
              e.preventDefault(); 
              alert("올바른 학생 또는 과목을 선택해주세요.");
              return;
            }

            e.preventDefault();

            let formData = new FormData(this);

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

function isValidOption(value, datalistId) {
  var datalistOptions = document.getElementById(datalistId).options;
  
  for (var i = 0; i < datalistOptions.length; i++) {
    if (datalistOptions[i].value === value) {
      return true; // 유효한 옵션이 존재하는 경우 true 반환
    }
  }

  return false; // 유효한 옵션이 없는 경우 false 반환
}
