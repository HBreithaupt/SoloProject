function initMap() {
  $.get("/user/address/retrieve", function(result) {
    var geocoder = new google.maps.Geocoder();
    var uluru = {};
    var address = result.street + " " + result.city + " " + result.state;

    geocoder.geocode({address: address}, function(result, status) {
      uluru = {lat: parseFloat(result[0].geometry.location.lat()), lng: parseFloat(result[0].geometry.location.lng())};
      var map = new google.maps.Map(document.getElementById('map'), {zoom: 15, center: uluru});
      var marker = new google.maps.Marker({position: uluru, map: map});
    });
  });
}



$(document).ready(function() {

});
