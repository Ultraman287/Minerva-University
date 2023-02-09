// Creating a function to validate a user's login information:
function validate()
{
    // Initializing the variables for the username and password for login:
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    // Checking whether the user's information is in the database as it was inputted:
    if (username == "Database Username" && password == "Database Password")
    {
        // Alerting the successful login of the user:
        alert("Login successful");

        // Redirecting the user to the main page with their login information present:
        window.location = "main_in.html"; 

        // Returning a default value:
        return false;
    }
}
