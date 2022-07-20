window.addEventListener("load", onLoad1);

function storestate(state) {
    if (state == "MD: MANUAL" || state == "MD: AUTO"){
        localStorage.setItem("lastState", state);
    }
    else{
        localStorage.setItem("dog", state)
    }
}

// Loads values from diffrent things that is needed when the page is reloaded, refreshed or whatever
function onLoad1() {
    let state = localStorage.getItem("lastState");
    let dog = localStorage.getItem("dog");
    let state_face1 = localStorage.getItem("state_face1");
    let state_face2 = localStorage.getItem("state_face2");

    if (state == "MD: MANUAL") {
        document.getElementById("toggle1").checked = true;
        document.getElementById("toggle").checked = true;
    }
    else {
        document.getElementById("toggle1").checked = false;
    }

    if (dog == "ST: DOG2") {
        document.getElementById("onOff").checked = true;
        document.getElementById("toggle2").checked = true;
    }
    else {
        document.getElementById("toggle2").checked = false;
    }

    if (state_face1 == "found"){
        enable_face("face1")
    }
    else {
        reset_face("face1")
    }

    if (state_face2 == "found"){
        enable_face("face2")
    }
    else {
        reset_face("face2")
    }
    
    change_dog_info("dog1")
    change_dog_info("dog2")

    GET_CTRL(state);
    GET_CTRL(dog);
}

// Since there is a small animation when toggleboxes are switched it needs to wait for some time before showing them or it looks ugly, only happens when page is loaded
var delayInMilliseconds = 70;

 setTimeout(function() {
    document.getElementById("toggle1").style.visibility = "visible";
    document.getElementById("toggle2").style.visibility = "visible";
}, delayInMilliseconds);

// send values to server
function GET_CTRL(cmd) {
    let dog = localStorage.getItem("dog");
    if (dog == "ST: DOG1") {
        cmd = "D1: " + cmd
    }
    else if (dog == "ST: DOG2") {
        cmd = "D2: " + cmd
    }
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", `/ctrl?cmd=${cmd}`, false ); // false for synchronous request
    xmlHttp.send( null );
}

// fetch values from server
function GET(url) {
    
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", url, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText
}

// basic polling, fetches new logs from server every second
var mySynFunc = (url) => {
    txt = GET(url)
    document.getElementById('log1').innerHTML = txt
}

function updateLogs() {
    let dog = localStorage.getItem("dog");
if (dog == "ST: DOG1") {
    mySynFunc('/log1')
}
else if (dog == "ST: DOG2") {
    mySynFunc('/log2')
}
}
/* This id must be used to stop your function interval */
var id = setInterval(updateLogs, 200)

// basic polling, fetches new alerts from server every second
// with usage of localstorage the variables will be saved even tho the site is refreshed, 
//if server is restarted they will go back to defalut (offline) except face req (needs to be reseted manually)
var pollingAlerts = (url) => {
    txt = GET(url)
    if (txt.includes("AR:1")) {
        localStorage.setItem("d1_state", "I'm stuck!")
        localStorage.setItem("d1_color", "red")
        change_dog_info("dog1")
    }
    if (txt.includes("AR:2")) {
        localStorage.setItem("d2_state", "I'm stuck!")
        localStorage.setItem("d2_color", "red")
        change_dog_info("dog2")
    }
    if (txt.includes("ARD:1")) {
        localStorage.setItem("d1_state", "Operational")
        localStorage.setItem("d1_color", "black")
        change_dog_info("dog1")
    }
    if (txt.includes("ARD:2")) {
        localStorage.setItem("d2_state", "Operational")
        localStorage.setItem("d2_color", "black")
        change_dog_info("dog2")
    }
    if (txt.includes("OF:1")) {
        localStorage.setItem("d1_state", "Offline")
        localStorage.setItem("d1_color", "black")
        change_dog_info("dog1")
    }
    if (txt.includes("OF:2")) {
        localStorage.setItem("d2_state", "Offline")
        localStorage.setItem("d2_color", "black")
        change_dog_info("dog2")
    }
    if (txt.includes("ON:1")) {
        localStorage.setItem("d1_state", "Online")
        localStorage.setItem("d1_color", "black")
        change_dog_info("dog1")
    }
    if (txt.includes("ON:2")) {
        localStorage.setItem("d2_state", "Online")
        localStorage.setItem("d2_color", "black")
        change_dog_info("dog2")
    }

    if (txt.includes("FACE:1")) {
        enable_face("face1")
        localStorage.setItem("state_face1", "found");
    }
    if (txt.includes("FACE:2")) {
        enable_face("face2")
        localStorage.setItem("state_face2", "found");
    }
}

var id1 = setInterval(pollingAlerts, 1000, '/alerts');

// changes the info on dog 1 or dog 2
function change_dog_info(dogid) {
    let dog1_state =  localStorage.getItem("d1_state")
    let dog1_color =  localStorage.getItem("d1_color")
    let dog2_state =  localStorage.getItem("d2_state")
    let dog2_color =  localStorage.getItem("d2_color")
    if (dogid == "dog1") {
        document.getElementById("h1").innerHTML = "Dog 1: " + dog1_state;
        document.getElementById("h1").style.color = dog1_color;
    }
    else {
        document.getElementById("h2").innerHTML = "Dog 2: " + dog2_state;
        document.getElementById("h2").style.color = dog2_color;
    }
}

// Lets the user know that an unknown face has been found, also shows a reset button for user to press if reset is wanted
function enable_face(face) {
    if(face == "face1"){
        document.getElementById("dog1_dot").style.backgroundColor = "red";
        document.getElementById("face1").innerHTML = "Unknown face detected";
        document.getElementById("reset1").style.visibility = "visible";
        
    }
    else {
        document.getElementById("dog2_dot").style.backgroundColor = "red";
        document.getElementById("face2").innerHTML = "Unknown face detected";
        document.getElementById("reset2").style.visibility = "visible";
    }
}

// Sets the dot, color and text back to original, also hiddes reset button since there is nothing to reset
function reset_face(face) {
    if (face == "face1") {
        document.getElementById("dog1_dot").style.backgroundColor = 'rgb(' + 47 + ',' + 218 + ',' + 13 + ')';
        document.getElementById("face1").innerHTML = "No humans detected";
        document.getElementById("reset1").style.visibility = "hidden";
    }
    else {
        document.getElementById("dog2_dot").style.backgroundColor = 'rgb(' + 47 + ',' + 218 + ',' + 13 + ')';
        document.getElementById("face2").innerHTML = "No humans detected";
        document.getElementById("reset2").style.visibility = "hidden";
    }
}

// fetches keystrokes and sends them to server
document.addEventListener('keydown', (e) => {
    GET_CTRL(`KC: ${e.keyCode}`)
    
});
