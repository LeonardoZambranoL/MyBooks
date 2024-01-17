var defaultTextColor = "#000000";

function get_book_data(bookId){
    return fetch(`${window.origin}/functions/get_book_data`, {
        method: "POST",
        body: JSON.stringify({ bookId: bookId }),
    }).then((resp) => resp.json()).then((data) => {
        return data;
    }).catch((err) => {
        console.log("error");
    }) ;

}

function delete_container(elementId){
    var containerToDel = document.getElementById(elementId);
        if (containerToDel){
            containerToDel.remove();
        }
}
function set_contents(elementId, contents){
    var element = document.getElementById(elementId);
    element.innerHTML = contents;
}


function htmlDecode(input) {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}