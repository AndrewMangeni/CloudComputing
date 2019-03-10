var AWS = require('aws-sdk');

exports.handler = (event, context, callback) => {

    //console.log(JSON.stringify(event));
    var message = event.messages[0].unstructured.text;

    AWS.config.region = 'us-west-2';

    var lexruntime = new AWS.LexRuntime();

    var params = {
        botAlias: "Prod",
        botName: "ChatBot",
        inputText: message,
        userId: "00",
        sessionAttributes: {}
    };


    lexruntime.postText(params, function(err, data) {
        if (err) {
            console.log(err, err.stack); // an error occurred
            callback(err, "failed");


        } else {
            console.log(data); // got something back from Amazon Lex
            context.succeed(data);

        }
    });

};
