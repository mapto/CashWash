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
    var table = $('#alias').DataTable( {
        //"processing": true,
        searching: false,
        paging: false,
        info: false,
        serverSide: true,
        stateSave: true,
        ajax: "../datatables/aliases/2"
    } );
});
