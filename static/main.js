$(document).ready(function() {
    setupForm();
});

function setupForm() {
    var form = document.querySelector('form');
    form.action = '/upload';
    form.method = 'post';
    form.enctype = 'multipart/form-data';
}