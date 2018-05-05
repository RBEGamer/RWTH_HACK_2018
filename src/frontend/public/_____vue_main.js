
  // your code goes here
var loaded_view = "none";
var refreshIntervalId = null;
function load_dashboard_view(){
  loaded_view = "dashboard";

  $.get( "http://127.0.0.1:5000/tmpl_dashboard.html", function( data ) {

    if(data == undefined || data == null || data == ""){
      $('#single_page_view_area').html("<h1> CANT DISPLAY THE PAGE </h1>");
      return;
    }
    $('#single_page_view_area').html(data);
    app = new Vue({
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
    app.$forceUpdate();    
    update_recent_table();
    create_chart();
    refreshIntervalId = setInterval(function(){ update_recent_table(); }, 500);
  });



}


function load_ticket_view(_id){
  loaded_view = "ticket";
  clearInterval(refreshIntervalId); //clear prev interval
  console.log("loading ticket " + _id);


  $.get( "http://127.0.0.1:5000/tmpl_ticket.html", function( data ) {

    if(data == undefined || data == null || data == ""){
      $('#single_page_view_area').html("<h1> CANT DISPLAY THE PAGE </h1>");
      return;
    }
    $('#single_page_view_area').html(data);




    $.getJSON( "http://127.0.0.1:5000/api/tickets/"+_id+"/show", function( data ) {
if(data == undefined){console.log("data empty"); return;}

app = new Vue({
  el: '#app',
  data:{
    single_ticket:data
  } 
});
app.$forceUpdate();  



  });


  

  });


  
  //refresh view


}


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
    
    //generate ticket id loading funtkion call
    data[i].link_id = "load_ticket_view(" + data[i].id + ")";
   // $('#'+ data[i].link_id).click(function(){ load_ticket_view(); return false; });


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






//setInterval(function(){ update_recent_table(); }, 500);



  //alert( "Load was performed." );


