
sound = new Audio();
sound.src = '/sites/_rem-mastera/imgs/chimes.mp3';
//sound.src = './imgs/chimes.mp3';
//sound.play();

$(function(){

});

$(window).on('wUserLogin', function(ev, uid){
  ws_start(uid);
});

function ws_start(IdUser){
  //console.log('ws_start', IdUser);
  
  if (! "WebSocket" in window) {
    console.log('браузер не поддерживает WebSocket');
    return;
  }
  var ws = new WebSocket("ws://"+$('#SysInfo').data('websocket_ip')+":8787/websocket");
  ws.onopen = function() {
    console.log('open', IdUser);
    ws.send( JSON.stringify({sess_cookie:sess_cookie(), iduser:IdUser}) );
  };
  ws.onmessage = function (evt) {
    var cmd = JSON.parse(evt.data);
    //console.log(cmd);
    if(typeof cmd.MessStats === 'object'){
      var agr = AgregateMess(cmd.MessStats);
      $("#UnreadMessCount").html(agr.InUnread>0 ? agr.InUnread : '');
      
      $(window).trigger('wMessStats', [cmd.MessStats]);

      // ищем ChatUpdate во фреймах и в основном окне
      for (var i=0; i< window.frames.length; i++) {
	if(typeof window.frames[i].ChatUpdate=="function"){
	  window.frames[i].ChatUpdate(cmd.MessStats);
	  break;
	}
      }
      if (typeof ChatUpdate=="function"){
	ChatUpdate(cmd.MessStats);
      }

    }
    
    if (cmd.sound)
      sound.play();
  };
  ws.onclose = function() {
    setTimeout(function(){
      console.log("try connect again");
      ws_start(IdUser);
    }, 7000);
  };
  ws.onerror = function(ev) {
    console.log('Error detected:');
    console.log(ev.target);
  }
}


function AgregateMess(MessStats){
  var a = {InUnread:0, OutUnread:0, TotalPartners:0};
  for(m in MessStats){
    var ms = MessStats[m];
    //console.log(ms);
    a.InUnread 	+= ms.InTotal - ms.InRead || 0;
    a.OutUnread	+= ms.OutTotal - ms.OutRead || 0;
    a.TotalPartners += 1;
  }
  //console.log(a);
  return a;
}

function sess_cookie(){
  var c = document.cookie.split(';');
  for (var i=0; i<c.length; i++){
    var cookie = c[i].trim();
    if (cookie.indexOf("SessId")==0)
      return cookie;
  }
}

(function($){
  $.fn.setVisible = function(visible){
    if(visible) 
      this.show();
    else  
      this.hide();
  };
}(jQuery));
