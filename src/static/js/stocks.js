var id = firebase.auth().currentUser;
console.log(id)
function check_price(){
var stock_name = $("#stock").val()
var quantity = $("#quantity").val()
console.log(stock_name)
console.log(quantity)
if(id!=0){
    $.ajax({
        data: {
        stock: stock_name,
        },
        type: "POST",
        url: "/check_stockprice",
    }).done(function (data) {
        alert(`One ${stock_name} stock costs ${data} FEX`)
    });
    
}else{
    alert("Please log in!")
}

}
function buy_stock(){
    var stock_name = $("#stock").val()
var quantity = $("#quantity").val()
console.log(stock_name)
console.log(quantity)
if(id!=None){

    $.ajax({
            data: {
            stock: stock_name,
            quantity: quantity,
            id: user.uid
            },
            type: "POST",
            url: "/buy_stock",
        }).done(function (data) {
            alert(data)
        });
    }else{
        alert("Please log in!")
    }
        
}
function sell_stock(){
    var stock_name = $("#stock").val()
var quantity = $("#quantity").val()
console.log(stock_name)
console.log(quantity)
if(id!=None){

    $.ajax({
            data: {
            stock: stock_name,
            quantity: quantity,
            id: user.uid
            },
            type: "POST",
            url: "/sell_stock",
        }).done(function (data) {
            alert(data)
        });}else{
            alert("Please log in!")
        }
        
}