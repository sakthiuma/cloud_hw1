
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """

def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        }
    }

def greet(intent_request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('recommendation')
    response = table.scan()
    print(response)
    msg = ""
    data = response['Items']
    print(data)
    if len(data) == 1:
        if "cuisine" in data[0]:
            msg = " I see your previous restaurant recommendation was " + str(data[0]['cuisine'])
    # else:
    #     msg = ""
    print("data from the recommendation" , msg)
    source = intent_request['invocationSource']
    logger.debug(source)
    
    table.delete_item(Key={'sessionId':'1'})
    print("deleted item")
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'How can I help you?' + msg})
   

def dining_recommendation(intent_request):
    logger.debug(intent_request['currentIntent'])
    # slots = get_slots(intent_request)
    # logger.debug(slots)
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Almost done!!You will be notified with on your mail id once we find places according to your preference'})

def thank_you(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you'})

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False



""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    # if intent_name == 'OrderFlowers':
    #     return order_flowers(intent_request)
    logger.debug(intent_request['currentIntent'])
    if intent_name == 'GreetingIntent':
        return greet(intent_request)
        
    if intent_name == 'DiningSuggestionsIntent':
        logger.debug(" in dining")
        return dining_recommendation(intent_request)
        
    if intent_name == 'ThankyouIntent':
        return thank_you(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
