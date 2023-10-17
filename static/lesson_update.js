// lesson_update.js

$(document).ready(function() {
  // 학생 정보 가져오기
  $.ajax({
    url: '/api/students',
    type: 'GET',
    success: function(response) {
      var studentSelect = $('#studentId');
      response.forEach(function(student) {
        studentSelect.append('<option value="' + student.id + '">' + student.name + '</option>');
      });
    },
    error: function(xhr, status, error) {
      console.error('Error fetching students:', error);
    }
  });

  // 상세 과정 정보 가져오기
  $.ajax({
    url: '/lesson_update', // 엔드포인트 변경
    type: 'GET',
    success: function(response) {
      var subjectDetailSelect = $('#subjectDetailId');
      response.forEach(function(subjectDetail) {
        subjectDetailSelect.append('<option value="' + subjectDetail.id + '">' + subjectDetail.name + '</option>');
      });
    },
    error: function(xhr, status, error) {
      console.error('Error fetching update lessons:', error);
    }
  });

  // 수업 기록 등록 폼 제출 처리
  $('#lessonForm').submit(function(event) {
    event.preventDefault();

     var form = $(this);

     // 수업 기록 등록 API 호출
     $.ajax({
       url: '/api/lessons',
       type: 'POST',
       data: form.serialize(),
       success: function(response) {
         alert('수업 기록이 성공적으로 등록되었습니다.');
         form.trigger('reset'); // 폼 초기화
       },
       error: function(xhr, status, error) {
         console.error('Error submitting lesson:', error);
         alert('수업 기록 등록에 실패했습니다. 다시 시도해주세요.');
       }
     });
   });
});
