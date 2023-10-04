function previewImage(event) {
  let reader = new FileReader();
  reader.onload = function () {
    let output = document.getElementById("imagePreview");
    output.src = reader.result;
    output.classList.add("img-upload-fit");
  };
  reader.readAsDataURL(event.target.files[0]);
}

document.getElementsByName("location")[0].style.marginBottom = "8px";

function findLocation() {
  window.open("/fix_location/", "거래 희망 장소 설정", "width=800px, height=800px, left=100px, top=50px");
}
