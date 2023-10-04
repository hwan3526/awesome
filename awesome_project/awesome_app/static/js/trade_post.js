let currentLocation = undefined;
let pathfinder = document.getElementById("pathfinder");
let pathfinderButton = document.getElementById("pathfinder-button");
let fixLocation = document.getElementById("fix-location");

function getAddr(lat, lon) {
    let geocoder = new kakao.maps.services.Geocoder();
    let coord = new kakao.maps.LatLng(lat, lon);
    let callback = function (result, status) {
        if (status === kakao.maps.services.Status.OK) {
            console.log(result);
            currentLocation = result[0].address.address_name;
            pathfinder.href = "https://map.kakao.com/?sName=" + currentLocation + "&eName=" + fixLocation.innerText.split(' | ')[1];
        }
    };
    geocoder.coord2Address(coord.getLng(), coord.getLat(), callback);
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
        let lat = position.coords.latitude;
        let lon = position.coords.longitude;

        getAddr(lat, lon);
    });
} else {
    pathfinderButton.classList.toggle("button-disabled");
    pathfinder.style.cursor = "not-allowed";
    pathfinder.style.pointerEvents = "none";
}
