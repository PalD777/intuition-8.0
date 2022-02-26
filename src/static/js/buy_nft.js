function buynft(nft, price){
    alert('Transaction in progress')

    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            $.ajax({
                data: {
                  id: user.uid,
                  nft: nft,
                  price: price,
                },
                type: "POST",
                url: "/buy_nft",
              }).done(function (data) {
                alert(data);
              });
        }})
}