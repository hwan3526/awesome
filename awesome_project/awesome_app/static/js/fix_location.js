document.getElementById("header").style.width = "80%";
document.getElementById("content").style.width = "80%";
document.getElementById("region-certified").style.display = "none";
document.getElementById("region-warn").style.display = "none";
document.getElementById("region-warn").style.color = "red";
document.getElementById("region-warn").style.fontWeight = "bold";
document.getElementById("region-warn").innerText = "!!인증하신 동네와 다른 동네입니다!!";

let mapContainer = document.getElementById("map"),
  mapOption = {
    center: new kakao.maps.LatLng(33.450701, 126.570667),
    level: 3,
  };

let map = new kakao.maps.Map(mapContainer, mapOption);

let imageSrc = 'https://brandnew.daangn.com/static/83204de0c76f5d19f87a4cd3d02a23df/49a66/logoImage.png',
  imageSize = new kakao.maps.Size(42, 72),
  imageOption = {offset: new kakao.maps.Point(21, 72)};
let markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize, imageOption),
  markerPosition = new kakao.maps.LatLng(37.54699, 127.09598);
let marker = new kakao.maps.Marker({
  position: markerPosition, 
  image: markerImage
});

let currentLocation = undefined;

kakao.maps.event.addListener(map, 'center_changed', function() {
  let latlng = map.getCenter();

  getAddr(latlng.getLat(),latlng.getLng());
});

function getAddr(lat, lon) {
  let geocoder = new kakao.maps.services.Geocoder();

  let coord = new kakao.maps.LatLng(lat, lon);
  let callback = function (result, status) {
    if (status === kakao.maps.services.Status.OK) {
      console.log(result);
      currentLocation = result[0].address.address_name;

      document.getElementById("region-info").innerText =
        "지정하신 거래 희망 장소는 " + currentLocation + " 입니다.";

      let regionCertifiedValue = document.getElementById('region-certified').innerText;
      let regionArray = regionCertifiedValue.split(" ");
      let lastRegionPart = regionArray[regionArray.length - 1];

      let currentLocationArray = currentLocation.split(" ");
      let regionWarn = document.getElementById("region-warn");

      if (currentLocationArray.includes(lastRegionPart)) {
        regionWarn.style.display = "none";
      } else {
        regionWarn.style.display = "block";
      }
    }
  };
  geocoder.coord2Address(coord.getLng(), coord.getLat(), callback);

  marker.setMap(null);
  marker = new kakao.maps.Marker({
    position: coord, 
    image: markerImage
  });
  marker.setMap(map);
}

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(function (position) {
    let lat = position.coords.latitude;
    let lon = position.coords.longitude;

    let locPosition = new kakao.maps.LatLng(lat, lon);
    map.setCenter(locPosition);
    let geocoder = new kakao.maps.services.Geocoder();

    getAddr(lat, lon);
  });
} else {
  let locPosition = new kakao.maps.LatLng(33.450701, 126.570667);
  document.getElementById("region-info").innerText = "사용자 환경문제로 인해 위치정보를 사용할 수 없습니다.";
  map.setDraggable(false);
  map.setCenter(locPosition);
}

opener.document.getElementById("region-warn").style.display = "none";
opener.document.getElementById("region-warn").style.color = "red";
opener.document.getElementById("region-warn").style.fontWeight = "bold";
opener.document.getElementById("region-warn").style.textAlign = "center";
opener.document.getElementById("region-warn").style.marginBottom = "8px";
opener.document.getElementById("region-warn").innerText = "!!인증하신 동네와 다른 동네입니다!!";

function fixLocation(){
  opener.document.getElementsByName("location")[0].value = currentLocation;
  if (document.getElementById("region-warn").style.display == "block"){
    opener.document.getElementById("region-warn").style.display = "block";
  } else {
    opener.document.getElementById("region-warn").style.display = "none";
  }
  window.close();
}