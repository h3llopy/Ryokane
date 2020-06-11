odoo.define('web_find_us.multiple_maps', function (require) {
"use strict";

$(document).ready(function() {
    var map_api_key = $('.map_api_key').val();
    $.getScript('https://maps.googleapis.com/maps/api/js?key='+map_api_key, () => {

        if(window.location.href.indexOf("find_us_on_map") > -1){

            var ajax = require('web.ajax');
            var locations;
            ajax.jsonRpc("/show_partner_mails", 'call').then(function (data) {
                locations = data['address']


            var map = new google.maps.Map(document.getElementById('jsn'), {
              zoom: 4,
              center: new google.maps.LatLng(locations[0][2], locations[0][3]),
              mapTypeId: google.maps.MapTypeId.ROADMAP
            });

            var infowindow = new google.maps.InfoWindow();

            var marker, i;
            console.log(locations)

            for (i = 0; i < locations.length; i++) {  
                console.log(locations[i])
              marker = new google.maps.Marker({
                position: new google.maps.LatLng(locations[i][2], locations[i][3]),
                map: map
              });

              google.maps.event.addListener(marker, 'click', (function(marker, i) {
                return function() {
                  infowindow.setContent(locations[i][0] + "<br />" +locations[i][1]);
                  infowindow.open(map, marker);
                }
              })(marker, i));
            }
        });
    }
});

$('div.partner_location').click(function(){
    var partner_latitude = $(this).find(".partner_latitude").val();
    var partner_longitude = $(this).find(".partner_longitude").val();
    var city = $(this).find(".city_population").val();
    var country = $(this).find(".partner_longitude").val();
    var map = new google.maps.Map(document.getElementById('jsn'), {
          zoom: 10,
          center: new google.maps.LatLng(partner_latitude, partner_longitude),
          mapTypeId: 'terrain'
        });

    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(partner_latitude, partner_longitude),
        map: map
    });
            
    });
           
});
});