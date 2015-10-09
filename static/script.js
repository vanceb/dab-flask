$(document).ready( function () {
    // Initialise the UI
        update_info();
        update_nowplaying();
        update_text();
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
    $("#current-channel").on("click", function(event) {
        $.post('favorite/toggle')
    });


    // Regularly update the main UI elements
    setInterval(function() {
        update_info();
        update_nowplaying();
        update_text();
    }, 5000);

    // Update the channels list
    setInterval(update_channels(), 60000);
});

update_channels = function() {
    $.get("channels", function(data) {
        // Channel List
        var clist=""
        for (i in data.channels){
            clist = clist + '<p class="channel lead">' + i + '</p>';
        }
        $("#tab-channels").html(clist);
    });
    $.get("favorites", function(data) {
        // Favorites
        clist=""
        for (i in data.favorites){
            clist = clist + '<p class="channel lead">' + data.favorites[i] + '</p>';
        }
        $("#tab-favorites").html(clist);
    });
}

update_nowplaying = function() {
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
}

update_text = function () {
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
}

update_info = function() {
    $.get("info", function(data) {
        data = data.info
        if(data.favorites.indexOf(data.channel) >= 0){
                $("#current-channel").html('<p class="h1" id="favorite"><span class="glyphicon glyphicon-star"></span> ' + data.channel + '</p>');
        } else {
                $("#current-channel").html('<p class="h1" id="favorite"><span class="glyphicon glyphicon-star-empty"></span> ' + data.channel + '</p>');
        }
        $("#signal").html("<p class='lead'><span class='glyphicon glyphicon-signal'></span> " + data.signal_strength + "dB</p>")
        s= "<p class='lead'>";
        if (data.stereo) {
            s += "Stereo";
        } else {
            s += "Mono";
        }
        $("#stereo").html(s)
        $("#tab-signal").html("<p class='lead'> Signal Strength: " + data.signal_strength +" dB</p>" +
                        "<p class='lead'> Signal Quality: " + data.dab_quality + " %</p>" +
                        "<p class='lead'> Data Rate: " + data.datarate + " kbps</p>" +
                        "<p class='lead'> Stereo: " + data.stereo + "</p>"
                       );
        $volume.slider('setValue', data.volume);
    });
}
