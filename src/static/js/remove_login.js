document.getElementById("logout").onclick = function () {
    logout();
  };
document.getElementById("profile").onclick = function () {
    profile();
};
document.getElementById("google").onclick = function () {
    signinwithgoogle();
};
function profile() {
    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            window.location.href = '/profile/'+user.uid;
        }}
    )
}
function logout() {
    firebase
      .auth()
      .signOut()
      .then(function () {
        alert("logout successful");
      })
      .catch(function (error) {
        alert("an error happened");
      });
      document.getElementById("firebaseui-auth-container").style.display = "block";
    document.getElementById("logout").style.display = "none";
  }
  
firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
        document.getElementById("firebaseui-auth-container").style.display = "none";
        document.getElementById("logout").style.display = "block";
        $("#Profile").css('display', 'block');
        $.ajax({
            data: {
                name: user.displayName,
              id: user.uid,
              photoURL: user.photoURL,
            },
            type: "POST",
            url: "/setupfirebase",
          }).done(function (data) {
          });
        
    }
});
