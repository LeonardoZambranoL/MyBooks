function resend_conf_mail(email) {
  fetch(`${window.origin}/resend_link`, {
    method: "POST",
    body: JSON.stringify({email: email}),
    cache: "no-cache"
  }).then((_res) => {
    window.location.href = "/";
  }).catch((err) => {
        console.log("error");
  });
}