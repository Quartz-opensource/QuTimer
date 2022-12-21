function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}
function update_event () {

    const Http = new XMLHttpRequest();
    const url='http://127.0.0.1:1145/api/get_event';
    Http.open("GET", url);
    // Http.setRequestHeader(  "Access-Control-Allow-Origin", "*");  //允许所有来源访同
    // Http.setRequestHeader(  "Access-Control-Allow-Method","POST,GET");  //允许访问的方式
    Http.send();
    Http.onreadystatechange = (e) => {
        let result_json = JSON.parse(Http.responseText);
        console.log(result_json)
    }
    let result_json = JSON.parse(Http.responseText);
    document.getElementById("main_text").innerHTML=result_json;
}
window.onload=function() {
    update_event()
}
