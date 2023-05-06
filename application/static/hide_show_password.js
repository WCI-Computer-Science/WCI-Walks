var password_shown = false;
function toggle_password_visibility(o, password_field_id) {
    password_shown = !password_shown;
    document.getElementById(password_field_id).type = password_shown ? 'text' : 'password';
    o.innerText = password_shown ? 'Hide' : 'Show';
}