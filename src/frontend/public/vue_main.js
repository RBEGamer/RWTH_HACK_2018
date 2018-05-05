
  // your code goes here

function update_recent_table(){
  $.getJSON( "http://127.0.0.1:5000/api/tickets/list", function( data ) {
    if(data == null || data == undefined){console.log("data empty");return;}
    if(data.length <= 0){return;}


  
    
  var sv = 0;
  
    for (var i = 0; i < data.length; i++) { 

//1 -> eye blue
//2 -> pencil yellow
//3 -> avatar green
data[i].collab_action = [ ];
var tmp = [];

for (var j = 0; j < data[i].total_users_looking; j++) {
  tmp.push({action:1,desc:data[i].users_looking[j].toString()});
  console.log(data[i].users_looking[j]);
}
for (var j = 0; j < data[i].total_users_editing; j++) { 
  tmp.push({action:2,desc:data[i].users_editing[j].toString()});
}    


//SET STATE IDS
data[i].state_id = 0;
if(data[i].state != undefined && data[i].state == "Progress"){
  data[i].state_id = 1;
}

    if(data[i].state != undefined && data[i].state == "Done"){
      sv++;
      data[i].state_id = 2;
    }
    



    data[i].collab_action = tmp;

  }
    app.recent_ticket_tems = data;
    app.all_ticket_count = data.length;
    app.solved_ticket_count = sv;
    app.pending_ticket_count = data.length - sv;
});
}




var app = new Vue({
  el: '#app',
  data: {
    all_ticket_count: 1,
    solved_ticket_count:2,
    pending_ticket_count:3,
    recent_ticket_tems: [
      { id: '0',title: 'title1', created_by: 'IT', created_at: '01-04-2018', last_update: 'AAA', state: 'answered', tag: 'OPEN'},
    
    ],
    stuff: [
      { STUFF_ID: 'Stuff0',TICKET_ID: 'ticket#0', STATUS: 'OPEN'},
      { STUFF_ID: 'Stuff1',TICKET_ID: 'ticket#1', STATUS: 'CLOSED'}
    ]
  }
});



update_recent_table();
setInterval(function(){ update_recent_table(); }, 500);




  //alert( "Load was performed." );


