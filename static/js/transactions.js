$(document).ready(function() {
    var table = $('#data').DataTable( {
        ajax: "../datatables/transactions",
        columnDefs: [
        	{targets: [1, 3], render: renderOrgAndAcc},
	        {targets: [2, 4], visible: false}
	    ],
	    order: [[ 0, "desc" ]],
        serverSide: true,
        stateSave: true,
    } );

});
