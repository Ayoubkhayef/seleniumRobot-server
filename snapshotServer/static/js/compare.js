
$(document).ready(function () {
    $("#browsers").ultraselect({autoListSelected: true, maxWidth: "90px"});
    $("#environments").ultraselect({autoListSelected: true, maxWidth: "90px"});
    $("#testCases").ultraselect({autoListSelected: true, maxWidth: "90px"});
    
    $('#sessionFrom').datepicker({
    	format: 'dd-mm-yyyy',
        todayBtn: 'linked',
        endDate: 'today',
        autoclose: true
        
    })
    $('#sessionTo').datepicker({
    	format: 'dd-mm-yyyy',
    	todayBtn: 'linked',
    	endDate: 'today',
    	autoclose: true
    	
    })
    
});
