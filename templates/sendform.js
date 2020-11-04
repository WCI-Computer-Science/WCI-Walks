function sendlogin() {
    var form = document.getElementById('login');
    document.write('Starting');

    const XHR = new XMLHttpRequest();
    const FD = new FormData();

    //NOTE: Perform input checks first to ensure
    //everything is clean (no special characters) and in format
    for (var name in form) FD.append(name, form.name);
    
    //DEBUG
    XHR.addEventListener('load', (ev) => console.log('Success'));
    XHR.addEventListener('error', (ev) => console.log('Error'));

    XHR.open('POST', 'xyz');
    XHR.send(FD);
}