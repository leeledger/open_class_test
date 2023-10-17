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
        $('#studentId').append(`<option value="${student.id}" data-grade="${student.grade_level}">${student.name}</option>`);
      });
      
      // Display grade level of selected student
      $('#gradeLevel').text($('#studentId option:selected').data('grade'));
      
      // Update grade level when a different student is selected
      $('#studentId').change(function() {
        $('#gradeLevel').text($('#studentId option:selected').data('grade'));
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
         $('#subjectDetailId').append(`<option value="${subject.id}" data-name="${subject.name}" data-level="${subject.level}">${subject.name} ${subject.detail_script} ${subject.level}</option>`);
         
       });

       // Display subject name and level of selected subject detail script 
       $('#subjectName').text($('#subjectDetailId option:selected').data('name'));
       $('#level').text($('#subjectDetailId option:selected ').data('level'));

       // Update subject name and level when a different detail script is selected
       $('#subjectDetailId').change(function() {
           $('#subjectName').text($('#subjectDetailId option:selected').data('name'));
         });
     })
     .catch(error => console.error('Error:', error));
  
  // Handle form submission
  document.querySelector('#lessonForm')
          .addEventListener("submit", function(e) {

            e.preventDefault();
            let formData = new FormData(this);

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
