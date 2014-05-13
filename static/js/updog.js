
if (window.location.hash == '#_=_'){
history.replaceState 
? history.replaceState(null, null, window.location.href.split('#')[0])
: window.location.hash = '';
}

$.fn.modal.Constructor.prototype.enforceFocus = function () {};
  $(document).ready(function() {

    if ($( '.navbar-header' ).is( ':visible' )) {
     $('.navbar-toggle').on('click', function() {
       $(".collapse").toggle('in');
     });
   }
 });

  function addTextAreaCallback(textArea, callback, delay) {
    var timer = null;
    textArea.onkeyup = function() {
      if (timer) {
        window.clearTimeout(timer);
      }
      timer = window.setTimeout( function() {
        timer = null;
        callback();
      }, delay );
    };
    textArea = null;
  }

 
  function resolve_event_downtime_conflicts(downtimes) {
    if (downtimes.length > 0) {
    // downtimes is a list of downtimes and moved_event_or_downtime is an event
    if (downtimes[0].model == "udCalendar.downtime") {
      var new_downtimes = [];

      for (var i = 0; i < downtimes.length; i++) {
        if (downtimes[i].fields.start_time == downtimes[i].fields.end_time) {
          $('#calendar').fullCalendar('removeEvents', -downtimes[i].pk);
        }
        else new_downtimes.push(downtimes[i]);
      }
      var updated_downtimes = make_events(new_downtimes, green, "{{ username }}", false, false);

      for (var i = 0; i < new_downtimes.length; i++) {
        $('#calendar').fullCalendar('removeEvents', -new_downtimes[i].pk);
        $('#calendar').fullCalendar('rerenderEvents');
        $('#calendar').fullCalendar('renderEvent', updated_downtimes[i], stick=true);
      }
    }
    else alert("can't pass events to function resolve_event_downtime_conflicts!");
  }
}

function display_friend_requests() {
  var ret = 0;
  $.ajax({
    type: "GET",
    url: "/calendar/display_friend_requests/",
    data: {"username": '{{ user.username }}'},
    async: false,
      //},
      success: function(data) {
        userhtml = '<div id="scroll-able-nots1"><div id="list-group">';
        if (data == "No new notifications") {

          userhtml =  userhtml +'<li style="display:inline-block; vertical-align:middle;"><pre style="background-color:transparent; border:0px solid">' + "No New Friend Requests" + '</pre></li><li class="divider"></li>';
        }
        else {
          mydata = JSON.parse(data);
          var dlength = mydata.length;
          users = mydata;

          ret = users.length;
          if (users.length != 0) {
            for (var i = 0; i < users.length; i++) {
              fixed_length = 24;
              var name =users[i].fields.first_name + ' ' + users[i].fields.last_name;
              namelength = name.length;
              for (var j = 0; j < (fixed_length - namelength); j++) {
                name = name + ' ';
              }
              userhtml = userhtml + '<li style="display: inline-block; vertical-align: middle; "><img style="float:left" class="img-rounded" src="http://updog-assets.s3.amazonaws.com/media/profile_pictures/' + users[i].fields.username + '-social.jpg" alt="profpic" width="50" height="50"><button type="button" style="float:right" class="btn btn-primary" onclick="accept_friend_request(\''+ users[i].fields.username +'\')">Add</button><button style="float:right" class="btn btn-primary" type="button" onclick="reject_friend_request(\''+ users[i].fields.username + '\')">Not Now</button><div style="margin-left:65px; margin-right:120px"><pre style="background-color:transparent; border:0px solid">' + name + '</pre></div></li><li class="divider"></li>';
            }
          }
        }

        userhtml = userhtml + "</div></div>";
        $(".friend_requests").html(userhtml);
        $(".fr_text").html('<div style = "pointer-events:none"><span class="glyphicon glyphicon-user"></span><b class="caret"></b></div>');
      }
    });
return ret;
}

function get_num_new_friend_requests() {
  var ret = 0;
  $.ajax({
    type: "GET",
    url: "/calendar/get_num_new_friend_requests/",
    data: {"username": '{{ user.username }}'},
    async: false,
        //},
        success: function(data) {
          if (data == "No new notifications") return;
          ret = data;
        }
      });
  return ret;
}


function display_notifications() {
  var ret = 0;
  $.ajax({
    type: "GET",
    url: "/calendar/get_notifications/",
    data: {"username": '{{ user.username }}'},
    async: false,
    success: function(data) {
      userhtml = ''
      if (data == 'No Notifications') {
        userhtml = '<div id="scroll-able-nots"><div id="list-group"><li style="display: inline-block; vertical-align: middle; "><pre style="background-color:transparent; border:0px solid">' + "No New Notifications" + '</pre></li><li class="divider"></li></div></div>';
      }
      else if (!data || !data[0] || !data[1] || !data[2]) {
        return;
      }
      else {
        event_noteys = JSON.parse(data[0]);
        el = event_noteys.length;
        from_users = JSON.parse(data[1]);
        fl = from_users.length;
        items = JSON.parse(data[2]);
        il = items.length;

        userhtml = '<div id="scroll-able-nots"><div id="list-group">';
        if (el != 0 && fl != 0 && il != 0) {
          for (var i = 0; i < items.length; i++) {
            if (!event_noteys[i].fields.is_reply) {
              // we may not need to get the backend event
              var info_string = from_users[i].fields.first_name + ' ' + from_users[i].fields.last_name + ' wants to ';
            }
            else {
              //  "___ ___ accepted your invite to ___ at ____ on ___ from ____"
              var info_string = from_users[i].fields.first_name + ' ' + from_users[i].fields.last_name + ' accepted your invite to ';
            }
            var start_d = new Date(items[i].fields.start_time);
            var end_d = new Date(items[i].fields.end_time);


            var time_string =get_UTC_time(start_d) + '-' + get_UTC_time(end_d);
            var date_string = start_d.toUTCString().substring(0, 16);

            var act = "";
            if (items[i].fields.activity) {
              act = items[i].fields.activity;
            }
            else {
              act = "hang out";
            }
            info_string = info_string + act;

            if (items[i].fields.location) {
              info_string = info_string + " at " + items[i].fields.location;
            }                

            if (!event_noteys[i].fields.is_reply) {
              info_string = info_string + " on " + date_string + " from " + time_string;
              userhtml = userhtml + '<div id=invite_notey' + event_noteys[i].pk + '><li style="display: inline-block;"><img style="float:left" class="img-rounded" src="http://updog-assets.s3.amazonaws.com/media/profile_pictures/' + from_users[i].fields.username + '-social.jpg" alt="profpic" width="50" height="50"><button style="float:right" class="btn btn-primary" type="button" onclick="respond_yes_to_event_notification('+ event_noteys[i].pk + ')">Accept</button><button style="float:right" class="btn btn-primary" type="button" onclick="respond_no_to_event_notification(' + event_noteys[i].pk + ')">Decline</button><div style="margin-left:65px; margin-right:160px"> ' + info_string + '</div></li><li class="divider"></li></div>';
            }
            else {
              info_string = info_string + " for " + date_string + " from " + time_string;
              userhtml = userhtml + '<div id=reply_notey' + event_noteys[i].pk + '><li style="display: inline-block"><img style="float:left" class="img-rounded" src="http://updog-assets.s3.amazonaws.com/media/profile_pictures/' + from_users[i].fields.username + '-social.jpg" alt="profpic" width="50" height="50"><button style="float:right" class="btn btn-xs btn-danger" type="button"onclick="remove_reply_notification(' + event_noteys[i].pk + ')">x</button><div style="margin-left:65px; margin-right:160px"> ' + info_string + '</div></li><li class="divider"></li></div>';
            }
          }
        }         

        userhtml = userhtml + "</div></div>";
      }
      $(".notifications").html(userhtml);
      $(".notif_text").html('<div style = "pointer-events:none"><span class="glyphicon glyphicon-envelope" ></span><b class="caret"></b></div>');
    }
  });
return ret;
}

function remove_reply_notification(notification_pk) {
  $.ajax({
    type: "POST",
    url: "/calendar/remove_reply_notification/",
    data: {"notification_pk": notification_pk},
    success: function(data){
      $("#reply_notey" + notification_pk).remove();
    }
  });
}

function get_num_new_notifications() {
  var ret = 0;
  $.ajax({
    type: "GET",
    url: "/calendar/get_num_new_notifications/",
    data: {"username": '{{ user.username }}'},
    async: false,
        //},
        success: function(data) {
          if (data == "No new notifications") return;
          ret = data;
        }
      });
  return ret;
}

function respond_yes_to_event_notification(notification_pk) {

  $.ajax({
    type: "POST",
    url: "/calendar/respond_to_event_notification/",
    data: {'notification': notification_pk,
    'response': 'accept'
  },
  success: function(data) {
        // add the event to the front end right away
        var new_event = make_events(JSON.parse(data), blue, '{{ username }}', false, true);
        $("#calendar").fullCalendar('renderEvent', new_event[0], stick=true);
        // get rid of notification in navbar
        $("#invite_notey" + notification_pk).remove();

        // call change_event to resolve any conflicts with downtimes that might now exist with added_event now that it's been added
        $.ajax({
          type: "POST",
          url: "/calendar/resolve_repeating_conflicts/",
          data: {"pk": new_event[0].id,
              //"notification_pk": notification_pk,
              // day_delta and minute_delta are 0 because we are not actually changing the added event
              "day_delta": 0,
              "minute_delta": 0,
              "resize": "false",
            },
            success: function(data) {

              var parsed = JSON.parse(data);


              resolve_event_downtime_conflicts(parsed);
            }
          });
      }
    });
}

function respond_no_to_event_notification(notification_pk) {
  $.ajax({
    type: "POST",
    url: "/calendar/respond_to_event_notification/",
    data: {'notification': notification_pk,
    'response': 'decline'
  },
  success: function(data) {
    $("#invite_notey" + notification_pk).remove();
  }
})
}

function accept_friend_request(new_friend) {
  $.ajax({
    type: "POST",
    url: "/calendar/accept_friend_request/",
    data: {'new_friend': new_friend},
    success: function(data){
      get_friends('{{ user }}');
      display_friend_requests();
    }
  });
}

function reject_friend_request(new_friend) {
  $.ajax({
    type: "POST",
    url: "/calendar/reject_friend_request/",
    data: {'new_friend': new_friend},
    success: function(data){
      display_friend_requests();
    }
  });
}