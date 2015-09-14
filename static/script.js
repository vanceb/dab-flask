$(document).ready( function () {
    var now_playing = [];
    var prog_info = [];
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
    $("#channel").click( function () {
        $.post('channel/25', function (data) {
            $("#channel").html("<h1>" + data.channel + "</h1>")
        });
    });
    // Regularly update the signal parameters
    setInterval(function() {
        $.get("info", function(data) {
            $("#channel").html("<h1>" + data.channel + "</h1>")
            $("#signal").html("<p> Signal Strength: " + data.signal_strength +"</p>" +
                            "<p> Signal Quality: " + data.signal_quality + "</p>" +
                            "<p> Data Rate: " + data.data_rate + "</p>" +
                            "<p> Stereo: " + data.stereo + "</p>"
                           );
            $volume.slider('setValue', data.volume);
        });
    }, 5000);

    // Regularly update the text
    setInterval(function() {
        $.get("text", function(data) {
            txt = data.text;
            if (txt != null){
                var npre = /Now Playing:\s+(.*)/g;
                var hit = npre.exec(txt);
                if (hit != null && hit.length > 0){
                    np = [hit[1]];
                    if(np != now_playing[0]){
                        now_playing = np.concat(now_playing);
                        np_html = "<h3>" + np + "</h3>"
                        for (i=1; i<5 && i < now_playing.length; i++){
                            np_html = np_html + " <p>" + now_playing[i] + "</p>"
                        }
                        $("#now-playing").html(np_html);
                    }
                } else {
                    now = new Date();
                    pi_html = "<h3>" + txt + "</h3>";
                    delete prog_info[txt]
                    for (var key in prog_info){
                        if(now - prog_info[key] > 300000) {
                            delete prog_info[key]
                        } else {
                            pi_html = pi_html + "<p>" + key + "</p>"
                        }
                    }
                    prog_info[txt] = now;
                    $("#info").html(pi_html);
                }
            }
        });
    }, 5000);

});
