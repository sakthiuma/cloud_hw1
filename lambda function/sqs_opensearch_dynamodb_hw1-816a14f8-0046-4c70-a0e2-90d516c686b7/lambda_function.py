import json
from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import smtplib
from email.mime.text import MIMEText



def os_connection_setup():
    host = "search-lex-bot-elasticsearch-jz6wdka5rp55mtntkkxqu26vva.us-east-1.es.amazonaws.com"
    port = 443
    #commented out the authentication as git guardian was throwing an issue.
    #auth = ("sakthi", "")
    
    client = OpenSearch(
        hosts = [{"host": host, "port": port}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
        connection_class = RequestsHttpConnection
    )
    
    return client

def os_search_query(cuisine, client):
    resp = client.search(
    index="restaurants",
    body={
        "query": {
            "bool": {
                "must": {
                    "match_phrase": {
                        "cuisine": cuisine,
                    }
                },
            },
        },            
    }
    )
    #print(resp)
    return resp

def db_query(os_resp):
    items = [] 
    print("in db_query")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('restaurants')
    #print(os_resp['hits']['hits'])
    for each_data in os_resp['hits']['hits']:
        # print(each_data)
        # print("\n")
        restaurant_id = each_data['_source']['restaurantId']
        print(restaurant_id)
        cuisine = each_data['_source']['cuisine']
        response = table.query(KeyConditionExpression= Key('id').eq(restaurant_id))
        print(response['Items'])
        #items.append(response['Items'][0])
        return (response['Items'][0])
        #print("\n")
        #print(items)
    #return items
    
def delete_sqs_message(queueUrl, receipt_handle):
    sqs_client = boto3.client("sqs", region_name="us-east-1")
    sqs_client.delete_message(QueueUrl=queueUrl, ReceiptHandle=receipt_handle)
    print('Message deleted')
    
def get_message_from_sqs():
    queueUrl = 'https://sqs.us-east-1.amazonaws.com/040944046258/DiningRecommendatio.fifo'
    now = datetime.now()
    current_time = now.strftime("%S")
    sqs_client = boto3.client("sqs", region_name="us-east-1")
    #queue = sqs_client.Queue('https://sqs.us-east-1.amazonaws.com/040944046258/DiningRecommendatio.fifo')
    response = sqs_client.receive_message(
        QueueUrl = queueUrl,
        ReceiveRequestAttemptId=current_time
        )
    print(response)
    print(response['Messages'][0]['Body'])
    delete_sqs_message(queueUrl, response['Messages'][0]['ReceiptHandle'])
    return response['Messages'][0]['Body']
    #return response['Messages'][0]['Body']
    
def store_exisiting_recommendation(content):
    print("storing existing recommendation")
    dyno_db_recommend = boto3.resource('dynamodb')
    table = dyno_db_recommend.Table('recommendation')
    table.put_item(Item = {
        'sessionId': "1",
        'cuisine':content
    })
    
def send_email_through_ses(to_emailId, mail_body):
    SENDER = "violetorigin1999@gmail.com"
    RECIPIENT = to_emailId
    AWS_REGION = "us-east-1"
    client = boto3.client('ses',region_name=AWS_REGION)
    response = client.send_email(
    Destination={'ToAddresses': [RECIPIENT,]},
    Message={
        'Body': {'Text': {'Data': mail_body}},
        'Subject': {'Data': "Restaurant Suggestions"},
    },
    Source=SENDER
    )
    print("Email sent! Message ID:", ), print(response['MessageId'])
    store_exisiting_recommendation(mail_body)
    
    # try:
        
    # except ClientError as e:
    #     print(e.response['Error']['Message'])
    # else:
    #     print("Email sent! Message ID:", ),
    #     print(response['MessageId'])

# def send_email(mail_body, to_emailId):
#     gmail_user = "violetorigin1999@gmail.com"
#     gmail_app_password = "qcuktepgtxuayjln"
#     sent_from = gmail_user
#     sent_to = to_emailId # have to change this
#     sent_subject = "Hello World"
#     sent_body = "Its me World"
    
#     try:
#             msg = MIMEText(mail_body)
#             msg['Subject'] = sent_subject
#             msg['From'] = sent_from
#             msg['To'] = ','.join(sent_to)
#             smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#             smtp_server.login(gmail_user, gmail_app_password)
#             smtp_server.sendmail(sent_from, sent_to, msg.as_string())
#             smtp_server.quit()
#     except Exception as exception:
#         print("Error: %s!\n\n" % exception)

def lambda_handler(event, context):
    
    user_resp = get_message_from_sqs()
    print("user resp", user_resp, type(user_resp))
    resp_dict = json.loads(user_resp)
    print("resp dict", resp_dict['Cuisine'], type(resp_dict))
    client = os_connection_setup()
    resp = os_search_query(resp_dict['Cuisine'], client)
    #resp = os_search_query("Chinese", client)
    print(resp, type(resp))
    
    rest_result = db_query(resp)
    #print(rest_result['location'], type(rest_result['location']))
    rest_location_dict = eval(rest_result['location'].replace("'", "\"")) 
    #print(type(rest_location_dict), rest_location_dict)
    #print(" ".join(rest_location_dict['display_address']))
    mail_body = ""
    mail_body  += rest_result['name'] + "\n"+ rest_result['cuisine'] +"\n"+  " ".join(rest_location_dict['display_address']) + " \n"+rest_result['phone']

    print(mail_body)
    send_email_through_ses("sakthiumamaheswari@gmail.com", mail_body)

   
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
