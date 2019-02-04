$(document).ready(function() {
    var table = $('#data').DataTable( {
        ajax: "../datatables/cashflows",
        columnDefs: [
        	{targets: [3, 5, 7], render: renderOrgAndAcc},
	        {targets: [4, 6, 8], visible: false}
	    ],
	    order: [[ 0, "desc" ]],
        serverSide: true,
        stateSave: true
    } );
});
