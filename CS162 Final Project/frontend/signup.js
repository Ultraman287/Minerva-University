function checkinputs() {
    var email = document.getElementById("email").value;
    var password1 = document.getElementById("password1").value;
    var password2 = document.getElementById("password2").value;
    var name = document.getElementById("username").value;

    // if (email == "" || password1 == "" || password2 == "" || name == "") {
    //     alert("Please fill all the fields");
    //     return false;
    // }
    // if (password1 != password2) {
    //     alert("Passwords do not match");
    //     return false;
    // }

    // Send a post request to the backend
    // Make a normal http request

    console.log(email, password1, password2, name);

    fetch('auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password1,
                username: name
                })
            })
        }
console.log('This works');


//     var xhr = new XMLHttpRequest();
//     xhr.open("POST", "auth/register", true);
//     xhr.setRequestHeader("Content-Type", "application/json");
//     xhr.onreadystatechange = function () {
//         if (xhr.readyState === 4 && xhr.status === 200) {
//             var json = JSON.parse(xhr.responseText);
//             console.log(json.email + ", " + json.password);
//         }
//     }
//     var data = JSON.stringify({ "email": email, "password": password1, "name": name });

//     console.log(data);
//     xhr.send(data);


// }
