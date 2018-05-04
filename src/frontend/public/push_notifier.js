var socket = null;

function guid() {
    function s4() {
      return Math.floor((1 + Math.random()) * 0x10000)
        .toString(16)
        .substring(1);
    }
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
      s4() + '-' + s4() + s4() + s4();
  }

  function reps_guid() {
    function s4() {
      return Math.floor((1 + Math.random()) * 0x10000)
        .toString(8)
        .substring(1);
    }
    return s4() + s4()  + s4()  + s4();
  }
function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes;
    return strTime;
}            




$(function () {
    socket = io();
    
    //send register message with device timestamp
    new Fingerprint2().get(function(fp_result, components) {
        //console.log(fp_result) // a hash, representing your device fingerprint
        console.log(components) // an array of FP components
        socket.emit('client_register_event', {
            uuid:reps_guid(),
            timestamp:Math.floor(Date.now() / 1000),
            fingerprint:fp_result
        });
      })
    //request push permission
    Push.Permission.request(function (){console.log("push permission ok")}, function (){alert("For live status updates. Please allow browser notifications.")});


    socket.on('message', function (data) {
       console.log(data);


       if(data.event_type == "push"){
           if(data.payload.header == undefined){
               data.payload.header = "-- T2Ticket --";
           }

           if(data.payload.message == undefined){
               data.payload.message = "You got a new Message";
           }
        Push.create(data.payload.header.toString() , {
            body: data.payload.message.toString(),
            icon: '/img/icons/ticket_256.png',
            timeout: 4000,
            onClick: function () {
                window.focus();
                

                if(data.payload.jump_location != undefined && data.payload.jump_location != null && window.location.pathname != data.payload.jump_location){
                    window.location.pathname = data.payload.jump_location;
                }


                this.close();
            }
        });
        
       }
      });
});