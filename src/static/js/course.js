function complete_course(course){
    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            $.ajax({
                data: {
                  id: user.uid,
                  course: course,
                },
                type: "POST",
                url: "/add_course_money",
              }).done(function (data) {
                alert(data);
                window.location.reload()
              });
        }})
}