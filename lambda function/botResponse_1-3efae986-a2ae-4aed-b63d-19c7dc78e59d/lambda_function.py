import json
import boto3
from datetime import datetime

sessionAttributes = {}
userMsgs = []
def lambda_handler(event, context):
    
    # TODO implement
    #print(event['messages'][0]['unstructured']['text'])
    msg = event['messages'][0]['unstructured']['text']
    print(msg)
    #lexUserId = 'chatbot-demo' + str(datetime.datetime.now())
	
    retVals = pushChat(msg, sessionAttributes);
    #print(retVals['slots'])
    print("ret", retVals['message'])
   
    response = {
        'statusCode': 200,
        'messages' : [{
            'type': 'unstructured',
            'unstructured': {
                #'text': 'I \'m still under development. Please come back'
            
                'text':retVals['message']
            }
            
        }]
        #JSON.stringify('I \'m still under development. Please come back'),
    };
    if retVals['message'] == 'Almost done!!You will be notified with on your mail id once we find places according to your preference':
        print(retVals['slots'])
        sendMsgToSQS(retVals['slots'])
    return response;
    

def pushChat(msg, sessionAttributes):
    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName='DiningConciergeChatbot',
        botAlias='DCC',
        userId='sm10539',
        inputText=msg
        )
    return response


def sendMsgToSQS(msg):
    now = datetime.now()
    current_time = now.strftime("%H%M%S")
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/040944046258/DiningRecommendatio.fifo",
        MessageBody=json.dumps(msg),
        MessageGroupId="sakthi_sqs",
        MessageDeduplicationId = current_time
    )
    print("sent message")
    return





#     retMsg = '';
#     params = {
# 			'botAlias': '$LATEST',
# 			'botName': ' DiningConciergeChatbot',
# 			'inputText': msg,
# 			'userId': lexUserId,
# 			'sessionAttributes': sessionAttributes
# 		};
# 	lexruntime = new AWS.LexRuntime();
# 	lexruntime.postText(params, function(err, data) {
# 		if (err) {
# 			console.log(err, err.stack);
# 			#showError('Error:  ' + err.message + ' (see console for details)')
# 		}
# 		if (data) {
# 			sessionAttributes = data.sessionAttributes;
# 			retMsg = data.response; 
# 		}
	
# 	});
	
# 	retDict = {
# 	    'retMsg': retMsg,
# 	    'sessionAttributes': sessionAttributes
# 	};
	
# 	return retDict;