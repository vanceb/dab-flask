$(document).ready( function () {
    // Volume
    $("#volume").slider({
        orientation: "horizontal",
        max: 16,
        min: 0,
        value: 7,
        tooltip: 'hide'
    });
    $volume = $("#volume").on('slideStop', function (ev) {
        $.post('/volume/' + ev.value);
    });
    // Channel
    // Change Channel
    $('#tab-channels').on('click', '.channel', function(event) {
        var x = $( this ).text();
        $.post('/channel/' + x);
    });
    //
    // Regularly update the signal parameters
    setInterval(function() {
        $.get("info", function(data) {
            data = data.info
            $("#current-channel").html('<p class="h1">' + data.channel + '</p>')
            $("#tab-signal").html("<p> Signal Strength: " + data.signal_strength +"</p>" +
                            "<p> Signal Quality: " + data.dab_quality + "</p>" +
                            "<p> Data Rate: " + data.datarate + "</p>" +
                            "<p> Stereo: " + data.stereo + "</p>"
                           );
            $volume.slider('setValue', data.volume);
            $cl = $("#tab-channel");
            $cl.empty();
            var clist=""
            for (i in data.channels){
                clist = clist + '<p><a class="channel" href="#">' + i + '</a></p>';
            }
            $("#tab-channels").html(clist)
        });
    }, 5000);


    // Regularly update the text
    setInterval(function() {
        $.get("nowplaying", function(data) {
            text = data.text;
            np = "";
            for(i = 0; i < text.length; i++){
                if(i == 0){
                    np += '<p class="lead">' + text[i] + '</p>';
                    $("#current-track").html('<p class="lead"><span class="glyphicon glyphicon-music"> </span>' + ' ' +  text[i] + '</p>')
                } else {
                    np += '<p>' + text[i] + '</p>';
                }
            }
            $("#tab-playlist").html(np);
        });
        $.get("text", function(data) {
            text = data.text;
            txt = "";
            for(i = 0; i < text.length; i++){
                if(i ==0){
                    txt += '<p class="lead">' + text[i] + '</p>';
                    $("#current-info").html('<p class="lead"><span class="glyphicon glyphicon-info-sign"></span>' + ' ' + text[i] + '</p>')
                } else {
                    txt += '<p>' + text[i] + '</p>';
                }
            }
            $("#tab-info").html(txt);
        });
    }, 5000);

});
