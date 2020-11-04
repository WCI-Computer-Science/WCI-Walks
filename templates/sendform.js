function sendlogin() {
    var form = document.login;

    const XHR = new XMLHttpRequest();
    const FD = new FormData();

    //NOTE: sanitize the input later
    for (var name in form) FD.append(name, form.name);
    
    //DEBUG
    XHR.addEventListener('load', (ev) => console.log('Success'));
    XHR.addEventListener('error', (ev) => console.log('Error'));

    XHR.open('POST', '/users');
    XHR.send(FD);
}