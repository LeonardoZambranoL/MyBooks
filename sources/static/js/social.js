// to share books
var receiverType = document.getElementById("receiverType");

if (receiverType){

    receiverType.addEventListener("change", function() {

    var personSelector = document.getElementById("personSelector");
    var groupSelector = document.getElementById("groupSelector");
    var submitButton = document.getElementById("shareBookSubmit");

    if (receiverType.value == 0) { // Person
        personSelector.style.display = "block";
        groupSelector.style.display = "none";
        submitButton.style.display = "block";
    } else if (receiverType.value == 1){ // Group
        personSelector.style.display = "none";
        groupSelector.style.display = "block";
        //submitButton.style.display = "block";
    }
     else {
        personSelector.style.display = "none";
        groupSelector.style.display = "none";
        submitButton.style.display = "none";
    }

});
}

function accept_decline_shared_book(id, action, container){
    //action
    // 0 = decline
    // 1 = accept
    if (action == 0){
        var proceed = confirm("Are you sure you want to decline this book?");
    } else if(action == 1){
        var proceed = true;
    } else {
        var proceed = false;
    }

    if (proceed){
        fetch(`${window.origin}/functions/accept_decline_shared_book`, {
            method: "POST",
            body: JSON.stringify({ notifId: id, action: action }),
        }).then((resp) => resp.json()).then(function(data) {
            alert(data.msg)
            if (data.status == "success"){
                delete_container(container);
            }
        }).catch((err) => {
            console.log("error");
        }) ;
    }
}
