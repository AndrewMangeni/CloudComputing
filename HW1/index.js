document.getElementById("m")
    .addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("b").click();
    }
});


AWS.config.region = 'us-east-2';

var poolData = {
    UserPoolId : 'us-east-2_vEr6Jc0kU', // your user pool id here
    ClientId : '15d35hg1i6m0b1nam39qm889tg' // your app client id here
};

var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);


/*
var cognitoUser = userPool.getCurrentUser();
//Get URL
if (cognitoUser != null){

}
else{
  var resnode = document.createElement("LI");
  var textresnode = document.createTextNode("Bot: something is wrong");
  resnode.appendChild(textresnode);
  document.getElementById("messages").appendChild(resnode);
}
*/

var url = window.location.href;


//Add check for login
var frontindex = url.indexOf('=')+1;
var backindex = url.indexOf("&");
var token = url.substring(frontindex,backindex);

AWS.config.credentials = new AWS.CognitoIdentityCredentials({
  IdentityPoolId: 'us-east-2:bafa3c2e-483f-4788-a493-f04e9be4ac3a',
  Logins: {
    'cognito-idp.us-east-2.amazonaws.com/us-east-2_vEr6Jc0kU': token
  }
});



AWS.config.credentials.get(function(){

// Credentials will be available when this function is called.
var accessKeyId = AWS.config.credentials.accessKeyId;
var secretAccessKey = AWS.config.credentials.secretAccessKey;
var sessionToken = AWS.config.credentials.sessionToken;
//console.log("here buddy!");
//console.log(accessKeyId);
//console.log(secretAccessKey);
//console.log(sessionToken);

});


function chatwithBot(){


  var message = document.getElementById("m").value;
  document.getElementById("m").value = '';
  var node = document.createElement("LI");
  var textnode = document.createTextNode("User: " + message);
  node.appendChild(textnode);
  document.getElementById("messages").appendChild(node);

  if (token != null) {

        var apigClient = apigClientFactory.newClient({
        accessKey: AWS.config.credentials.accessKeyId,
        secretKey: AWS.config.credentials.secretAccessKey,
        region: "us-east-2",
        sessionToken: AWS.config.credentials.sessionToken
      });



        var params = {
          // This is where any modeled request parameters should be added.
          // The key is the parameter name, as it is defined in the API in API Gateway.
          //param0: '',
          //param1: ''
        };

        var body = { //"messages": message
        "messages": [
         {
           "type": "userSendAMessage",
           "unstructured": {
             "id": "0",
             "text": message,
             "timestamp": "0"
           }
         }
         ]
          // This is where you define the body of the request,
        };

        var additionalParams = {
          // If there are any unmodeled query parameters or headers that must be
          //   sent with the request, add them here.
          //headers: {
          //  'Access-Control-Allow-Origin':'*'
          //},
          //queryParams: {
            //param0: '',
            //param1: ''
          //}
        };



        apigClient.chatbotPost(params, body, additionalParams)
            .then(function(result){
              console.log(result);
              var resmessage = result.data.message;
              var resnode = document.createElement("LI");
              var textresnode = document.createTextNode("Bot: " + resmessage);
              resnode.appendChild(textresnode);
              document.getElementById("messages").appendChild(resnode);
              // Add success callback code here.
            }).catch( function(result){
              console.log(result);
              var message = "Sorry an error occurred.";
              var node = document.createElement("LI");
              var textnode = document.createTextNode("HigherUps: " + message);
              node.appendChild(textnode);
              document.getElementById("messages").appendChild(node);
              // Add error callback code here.
            });




  }
  else {
    console.log('Missing token, need to log in');
    var message = "You must log in!";
    var node = document.createElement("LI");
    var textnode = document.createTextNode("HigherUps: " + message);
    node.appendChild(textnode);
    document.getElementById("messages").appendChild(node);
  }




}
