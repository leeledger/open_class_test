$(document).ready(function() {
    var table = $('#lessonTable').DataTable({
        "ordering": false,
        "processing": true,
        "serverSide": true,
        "fixedHeader": true,
        "ajax": {
            url: "/api/lessons",
            type: 'POST',
            contentType:"application/json; charset=utf-8",
            data: function (d) {
                return JSON.stringify({ 
                    draw: d.draw,  // Add this line
                    studentName: $('#studentNameSearch').val(), 
                    lesson: $('#lessonSearch').val(), 
                    subjectDetail: $('#lessonDetailSearch').val(),
                    start: d.start,
                    length: d.length,
                    startDate: $('#startDatePicker').val(),  // Add this line
                    endDate: $('#endDatePicker').val(),  // And this line                    
                    teachId: $('#teach_id').val(),  // And this line                    
                });
            },
        },
        "columns": [
            { "data": 0 }, // 날짜
            { "data": 1 }, // 학생이름
            { "data": 2 }, // 대분류 과목명
            { 
                "data": 3, 
                "render": function(data, type, row) {
                    var lessonId;
                    if (row.length > 0) {
                        lessonId = row[row.length - 1];
                    } else {
                        // 예외 처리: row 배열이 비어있을 때 필요한 동작 수행
                        lessonId = ''; // 또는 다른 값으로 설정
                    }
                    var url = '/lesson_update_move/' + encodeURIComponent(lessonId);
                    return '<a href="' + url + '">' + data + '</a>';
                }
               }, // 과정 상세명 (링크 추가)
            { "data": 4 }, // 레벨
            { "data": 5 }, // 담당교사
            { "data": 6 }, // 수업 내용
            { "data": 7 }, // 교사지도사항 
        ],
        createdRow: function(row, data) {
          $('td', row).each(function(i) {
              $(this).attr('title', data[i]);
          });
       },
       initComplete: function() {
           var searchButton = $('<button type="button">검색</button>');
           searchButton.on('click', function() {
               table.ajax.reload();
           });

           $("#lessonTable_filter").html(searchButton);

           $("#studentNameSearch, #lessonSearch, #lessonDetailSearch").on('keypress',function(e) {
               if(e.which == 13) {
                   table.ajax.reload();
               }
           });
       }
    });
});

