$(document).ready(function() {
	/*
	$.ajax({
	  url: "http://localhost/transactions/",
	  success: function(d) {
	  	a = []
	  	for (let next of d["data"]) {
		  	a.push([next["amount"], next["currency"], next["payee"], next["beneficiary"], next["date"]]);
	  	}
	  	console.log(a);
		$('#data').DataTable( {
		    data: a,
		} );
	  	
	  },
	  dataType: "json"
	});
	*/
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
