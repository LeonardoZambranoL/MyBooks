function deleteItem(itemType,itemID, container) {
  var r = confirm("Are you sure you want to delete that book?");
  if (r){
      fetch(`${window.origin}/functions/delete_item`, {
        method: "POST",
        body: JSON.stringify({ itemType: itemType, itemID: itemID }),
      }).then( function(){
          delete_container(container);
      }).catch((err) => {
        console.log(err);
      });
  }
}

function editBookInfo(bookId){
    var bookName = document.getElementById("book_name_"+bookId);
    var bookDescription = document.getElementById("book_description_"+bookId);
    var editDeleteDiv = document.getElementById("edit_delete_buttons_"+bookId);
    var downloadShareReadDiv = document.getElementById("download_share_read_buttons_"+bookId);
    var saveCancelDiv = document.getElementById("save_cancel_buttons_"+bookId);

    downloadShareReadDiv.style.display = "none";
    saveCancelDiv.style.display = "inline-block";
    editDeleteDiv.style.display = "none";

    if (!bookDescription.innerHTML){
        bookDescription.innerHTML = "Description";
    }

    bookName.contentEditable = true;
    bookDescription.contentEditable = true;

    bookName.style.color = "#db411a";
    bookDescription.style.color = "#db411a";
}

function saveBookEdit(bookId){

    var bookName = document.getElementById("book_name_"+bookId);
    var bookDescription = document.getElementById("book_description_"+bookId);
    var editDeleteDiv = document.getElementById("edit_delete_buttons_"+bookId);
    var downloadShareReadDiv = document.getElementById("download_share_read_buttons_"+bookId);
    var saveCancelDiv = document.getElementById("save_cancel_buttons_"+bookId);

    bookName.style.color = defaultTextColor;
    bookDescription.style.color = defaultTextColor;

    bookName.contentEditable = false;
    bookDescription.contentEditable = false;

    downloadShareReadDiv.style.display = "inline-block";
    saveCancelDiv.style.display = "none";
    editDeleteDiv.style.display = "inline-block";

    newName = bookName.innerHTML;
    newDescription = bookDescription.innerHTML;

    fetch(`${window.origin}/edit_book`, {
        method: "POST",
        body: JSON.stringify({ bookId: bookId, newName: htmlDecode(newName), newDescription: htmlDecode(newDescription) }),
    }).then((resp) => resp.json()).then(function(data) {
        let result = data.msg
        alert(result)
    }).catch((err) => {
        console.log("error");
    }) ;
}

function cancelBookEdit( bookId ){

    var bookName = document.getElementById("book_name_"+bookId);
    var bookDescription = document.getElementById("book_description_"+bookId);
    var editDeleteDiv = document.getElementById("edit_delete_buttons_"+bookId);
    var downloadShareReadDiv = document.getElementById("download_share_read_buttons_"+bookId);
    var saveCancelDiv = document.getElementById("save_cancel_buttons_"+bookId);

    bookName.style.color = defaultTextColor;
    bookDescription.style.color = defaultTextColor;

    bookName.contentEditable = false;
    bookDescription.contentEditable = false;

    downloadShareReadDiv.style.display = "inline-block";
    saveCancelDiv.style.display = "none";
    editDeleteDiv.style.display = "inline-block";

    get_book_data(bookId).then((data) => {
        set_contents("book_name_"+bookId, data.name);
        set_contents("book_description_"+bookId, data.description);
    });
}