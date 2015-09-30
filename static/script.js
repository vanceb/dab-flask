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
    // Change Channel
    $('#tab-favorites').on('click', '.channel', function(event) {
        var x = $( this ).text();
        $.post('/channel/' + x);
    });
    // Manage favorites
    $("#favorite").on("click", function(event) {
        $.post('favorite/toggle')
    });
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
            // Channel List
            var clist=""
            for (i in data.channels){
                clist = clist + '<p class="channel lead">' + i + '</p>';
            }
            $("#tab-channels").html(clist);
            // Favorites
            clist=""
            for (i in data.favorites){
                clist = clist + '<p class="channel lead">' + data.favorites[i] + '</p>';
            }
            $("#tab-favorites").html(clist);
            if(data.favorites.indexOf(data.channel) >= 0){
                    $("#favorite").html('<p class="lead"><span class="glyphicon glyphicon-star"></span></p>');
            } else {
                    $("#favorite").html('<p class="lead"><span class="glyphicon glyphicon-star-empty"></span></p>');
            }
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
