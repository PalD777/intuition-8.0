function conv_change(mult){
    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            $.ajax({
                data: {
                  id: user.uid,
                  mult: mult,
                },
                type: "POST",
                url: "/change_conv",
              }).done(function (data) {
                alert(data);
              });
        }})
}