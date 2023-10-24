var table; // Define the table variable outside of the $(document).ready() function

$(document).ready(function() {
    
    table = $('#lessonTable').DataTable({
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
                });
            },
        },
        "columns": [
            { "data": null, "defaultContent": "<input type='checkbox' />", "className": "dt-center" }, // 체크박스
            { "data": 0 }, // 날짜
            { "data": 1 }, // 학생이름
            { "data": 2 }, // 대분류 과목명
            { "data": 3 }, // 과정 상세명 (링크 추가)
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

$('#createReportBtn').on('click', function() {
    var selectedRowsData = [];
    $('#lessonTable tbody input[type="checkbox"]:checked').each(function() {
        var row = $(this).closest('tr');
        var rowData = table.row(row).data();
        selectedRowsData.push(rowData);
    });
    
    // send the selectedRowsData to your endpoint using AJAX or other methods
    console.log(selectedRowsData); // for testing purposes only
    // Get the dates from the datepickers
    var startDate = $("#startDatePicker").val();
    var endDate = $("#endDatePicker").val();
    $.ajax({
        url: '/api/report',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ data: selectedRowsData, startDate: startDate, endDate:endDate  }),
        // dataType: 'json', // expect JSON response
        success: function(response) {
            console.log(response);
            
            // Redirect to report_sample.html page after AJAX request is successful
            window.location.href = '/report_sample';  // Change the URL as per your route configuration
        },
        error: function(error) {
            console.log(error);
        }
    });
});


