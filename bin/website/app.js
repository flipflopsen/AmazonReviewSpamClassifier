

var reviewTxt = document.getElementById('reviewInput');
var helpful = document.getElementById('helpfulInput');
var not_helpful = document.getElementById('notHelpfulInput');
var stars = document.getElementById('starsInput');
var jsonBtn = document.getElementById('jsonButton');
var output = document.getElementById('output');
var outputANN = document.getElementById('outputANN');

jsonBtn.addEventListener('click', function() {

    let inputArr = [];

    var data = {
        reviewTxt: reviewTxt.value,
        helpful: helpful.value,
        not_helpful: not_helpful.value,
        stars: stars.value
    }

    output.innerHTML = JSON.stringify(data)
    inputArr.push(data);

    //safe in local storage
    localStorage.setItem('listOfInputs', JSON.stringify(inputArr) )

    //POST request to Server
    postDataToBackend(inputArr);


})


function postDataToBackend(data) {

    let formData = new FormData();

    let dataReceived = '';
    let token = '{{csrf_token}}'
    formData.append('dataFromWebsite', data);
    formData.append('crsfmiddlewaretoken', token )

    //URL für Serveranbindung hier anpassen 
    fetch('/sendreview/', {
        method: 'POST',
        body: data
    })
    .then(resp => {
        if (resp.status === 200) {
            return resp.json()
        } else {
            console.log("Status: " + resp.status)
            return Promise.reject("server")
        }
    })
    .then(dataJson => {
        dataReceived = JSON.parse(dataJson)
    })
    .catch(err => {
        if (err === "This is a server error! ") return
        console.log(err)
    })

    outputANN.innerHTML('Das Review ist zu ' + decimalToPercentage(dataReceived) + ' fake!' );

console.log('Received: ${dataReceived}')       



}

function decimalToPercentage(deciaml){
    return deciaml * 100 + '%';
}


jsonBtn.addEventListener('click', function createJSONFromInputs() {

    let items = [];
    const addItems = (ev) => {
        ev.preventDefault();
        let reviewInfo = {

            reviewTxt: document.getElementById('reviewInput'),
            helpful: document.getElementById('helpfulInput'),
            not_helpful: document.getElementById('notHelpfulInput'),
            stars: document.getElementById('starsInput')
        }
        items.push(reviewInfo);
        document.forms[0].reset();

        //just to check
        console.log('added', {items} );
        let pre = document.getElementById('');
        pre.textContent = '\n' + JSON.stringify(items, '\t', 2);

        //pass to RestAPI
        //for now safe to local storage 
        localStorage.setItem('listOfInputs', JSON.stringify(items) )
   }
   document.addEventListener('DOMContentLoaded', ()=>{
    document.getElementById('btn').addEventListener('click', addItems);

   })

   
})

const menu = document.querySelector('#mobile-menu');
const menuLinks = document.querySelector('.navbar__menu');

menu.addEventListener('click', function() {
  menu.classList.toggle('is-active');
  menuLinks.classList.toggle('active');
});













