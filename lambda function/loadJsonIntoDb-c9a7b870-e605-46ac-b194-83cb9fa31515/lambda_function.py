# import boto3
# import json
# def put_item_in_database(jsondata):
#     #API expect data in dictionary format
#     datadict = json.loads(jsondata)
#     database = boto3.resource('dynamodb')
#     table = database.Table('yelp-restaurants')
#     table.put_item(Item = datadict)


import boto3
import json
from decimal import Decimal
dynamodb = boto3.resource('dynamodb')
def lambda_handler(event, context):
    with open('yelp_data.json', encoding="utf-8") as data:
        data = json.load(data, parse_float=Decimal)
    #  code for pushing into opensearch but I used the curl command see the HW1 document
    #    for each_data in data:
    #     document = {'Restaurant': {'cuisine': each_data['cuisine'], 'restaurantId': each_data['id']}}
    #     response = None
    #     response = client.index(
    #         index = 'restaurants,
    #         body = document,
    #         id = each_data['id'],
    #         refresh = True
    #     )
    print(len(data))
    table = dynamodb.Table('restaurants')
    for item in data:
        table.put_item(Item=item)
  
    
    
    return {
        'statusCode' : 200,
        'body':json.dumps("Hey from lambda")
    }