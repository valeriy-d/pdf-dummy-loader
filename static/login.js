var get = function(selector) {
    return document.querySelector(selector);
}

$(document).ready(function() {
    var button = get("[id='submit']");

    button.addEventListener('click', login);
});

function login() {
    var username = get("[name='username']").value,
        password = get("[name='password']").value;

    var form = new FormData(get('form'));

    $.ajax({
        url: '/login',
        method: 'POST',
        data: {
            username: username,
            password: password
        },
        success: function(data) {
            document.cookie = "username=" + data.token;
            window.location = '/';
        },
        failure: function() {

        }
    });
}
