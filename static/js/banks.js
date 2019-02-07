$(document).ready(function() {
    var table = $('#data').DataTable( {
        ajax: "../datatables/banks",
     //    columnDefs: [
     //    	{targets: [1, 3], render: renderOrgAndAcc},
	    //     {targets: [2, 4], visible: false}
	    // ],
	    order: [[ 1, "asc" ]],
        serverSide: true,
        stateSave: true,
    } );

});
