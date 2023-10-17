$(document).ready(function() {
    var table = $('#lessonTable').DataTable({
        "processing": true,
        "serverSide": true,
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
                });
            },
        },
        "columns": [
            { "data": 0 }, // 날짜
            { "data": 1 }, // 학년
            { "data": 2 }, // 학생 이름
            { 
                "data": 3, 
                "render": function(data, type, row) {
                  var lessonId = row[row.length - 1];
                  return '<a href="/lesson_update.html?lesson_id=' + lessonId + '">' + data + '</a>';
                }
               }, // 과정 상세명 (링크 추가)
            { "data": 4 }, // 단계
            { "data": 5 }, // 수업 내용
            { "data": 6 }, // 교사지도사항 

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

