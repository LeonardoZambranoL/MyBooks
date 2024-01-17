// For customizing bg
var bgType = document.getElementById("bgType");

if (bgType){
bgType.addEventListener("change", function() {

    var colorSelector = document.getElementById("solidColorSelector");
    var imageSelector = document.getElementById("customImageSelector");

    if (bgType.value == 0) {
        colorSelector.style.display = "none";
        imageSelector.style.display = "none";
    } else if (bgType.value == 1){
        colorSelector.style.display = "block";
        imageSelector.style.display = "none";
    } else if (bgType.value == 2){
        colorSelector.style.display = "none";
        imageSelector.style.display = "block";
    } else {
        colorSelector.style.display = "none";
        imageSelector.style.display = "none";
    }

});
}

var solidBgColor = document.getElementById("solidColor");

if (solidBgColor){
solidBgColor.addEventListener("change", function() {
    var colorSelector = document.getElementById("solidColorSelector");
    if (colorSelector.style.display == "block"){
        document.body.style.background = solidBgColor.value;
    }
});
}