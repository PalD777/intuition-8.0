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
              id: firebase.auth().currentUser.uid,
              photoURL: user.photoURL,
            },
            type: "POST",
            url: "/setupfirebase",
          }).done(function (data) {
          });
          var id=user.uid
        
    }
});
function check_price(){
var stock_name = $("#stock").val()
var quantity = $("#quantity").val()
console.log(stock_name)
console.log(quantity)
      $.ajax({
          data: {
          stock: stock_name,
          },
          type: "POST",
          url: "/check_stockprice",
      }).done(function (data) {
        if(data=="0"){
          alert(`Stock not found`)
        }else{
          alert(`One ${stock_name} stock costs ${data} FEX`)
        }
          
      });
      
  console.log(firebase.auth().currentUser.uid)

}
function buy_stock(){
  alert("Trying to buy stock")
    var stock_name = $("#stock").val()
var quantity = $("#quantity").val()
console.log(stock_name)
console.log(quantity)

    $.ajax({
            data: {
            stock: stock_name,
            quantity: quantity,
            id: firebase.auth().currentUser.uid
            },
            type: "POST",
            url: "/buy_stock",
        }).done(function (data) {
            alert(data)
        });
    
        
}
function sell_stock(){
  alert("Trying to sell stock")
    var stock_name = $("#stock").val()
var quantity = $("#quantity").val()
console.log(stock_name)
console.log(quantity)


    $.ajax({
            data: {
            stock: stock_name,
            quantity: quantity,
            id: firebase.auth().currentUser.uid
            },
            type: "POST",
            url: "/sell_stock",
        }).done(function (data) {
            alert(data)
        });
        
}