"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
from botocore.vendored import requests
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


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

#change from flower to cuisine
#change pickup_time to diningtime
#TODO add in Location check (maybe remove whitespace)
def validate_suggest_food(location, cuisine_type, partysize, date, dining_time):
    #TODO can i take out cuisine types now
    #cuisine_types = ['japanese', 'chinese', 'mexican', 'american', 'korean', 'italian', 'greek', 'indian']
    #if cuisine_type is not None and cuisine_type.lower() not in cuisine_types:
    #    return build_validation_result(False,
    #                                   'CuisineType',
    #                                   'Sorry, I dont recognize {} type of food, how about a different type of cuisine?  '
    #                                   'I do not have tastebuds but I heard Italian food is good!'.format(cuisine_type))

    if partysize is not None:
        partysize = parse_int(partysize)
        if math.isnan(partysize):
            # Not a valid partysize; use a prompt defined on the build-time model.
            return build_validation_result(False, 'PartySize', None)
        #TODO should I take out 30
        #if partysize > 30:
        #    return build_validation_result(False, 'PartySize',
        #                'That party size is too large for restaurants to accomodate. Can you specify a party size smaller than 30?')


    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'DiningDate', 'I did not understand that, what date would you like to eat?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'DiningDate', 'Please pick a date from today onwards. What date would you like to eat?')

    if dining_time is not None:
        if len(dining_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)

        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)

        #TODO take out the hour check
        #if hour < 5 and hour > 1:
            # Outside of business hours
        #    return build_validation_result(False, 'DiningTime', 'Most places are not open at that time. Can you specify a time after 5am and before 1am?')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def suggest_food(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    #TODO ADD in the party size and location
    location = get_slots(intent_request)["Location"]
    partysize = get_slots(intent_request)["PartySize"]
    cuisine_type = get_slots(intent_request)["CuisineType"]
    date = get_slots(intent_request)["DiningDate"]
    dining_time = get_slots(intent_request)["DiningTime"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_suggest_food(location, cuisine_type, partysize, date, dining_time)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        #TODO is this a problem? Adding the price. SHould i take out
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        #if flower_type is not None:
        #    output_session_attributes['Price'] = len(flower_type) * 5  # Elegant pricing model

        #this turns this type into a delegate one
        return delegate(output_session_attributes, get_slots(intent_request))


    #TODO call the YELP API

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return callYelp(location, cuisine_type, partysize, date, dining_time, intent_request)


#TODO formatting for the response

def callYelp(location, cuisine_type, partysize, date, dining_time,intent_request):
    hour, minute = dining_time.split(':')
    hour = parse_int(hour)
    minute = parse_int(minute)
    today = datetime.datetime.today()
    #dt = datetime.datetime.strptime(date+' '+dining_time+':00', '%Y-%m-%d %H:%M:%S')
    dt = today.replace(hour=hour, minute=minute)
    unixtime = str(int(time.mktime(dt.timetuple())))

    url = 'https://api.yelp.com/v3/businesses/search?location='+str(location) + '&term='+ str(cuisine_type) + '&limit=3' + '&open_at=' + unixtime
    header = {"Authorization":"Bearer ix93l_b_9I4rw0tZKBxVGetfqfLwy0rNNP9OxdY1pggdl4N3j7QMmN3Tz1hmBW3qbmOzAA7hCwFitc_1RLI0K4u9bN4e1ahwRAahEDMj5ixpEkaRoVoOyavfuHN_XHYx"}
    response = requests.get(url, headers=header)
    business_list = response.json()['businesses']
    if len(business_list) < 1:
        message = 'Sorry, there were no restaurants that fit that criteria. Please try again.'


    else:
        message = 'Here are my ' + str(cuisine_type) + ' restaurant suggestions for ' + str(partysize) + ' people, for ' + str(date) + ' at ' + str(dining_time) + '. '
        i = 1
        #can we do other shorter address address
        for business in business_list:
            #address = ''
            #for ad in business['display_address']:
            #    address = address + ad
            nextmess = '{}. {}, located at {}. '.format(str(i), business['name'], business['location']['address1'])
            i+=1
            message = message + nextmess
        message = message + "Enjoy your meal ya filthy animal!"



    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': message})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return suggest_food(intent_request)

    if intent_name == 'GreetingIntent':
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Hello there, my name is Dining Bot. But you can call me Dino! How can I help you?'})

    if intent_name == 'ThankYouIntent':
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Glad I could help! Hope you have a nice day. Come back soon!'})

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
