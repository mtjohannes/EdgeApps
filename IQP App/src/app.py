import os
import sys
import traceback
import json
import paho.mqtt.client as mqtt
import datetime

class App():
    '''
    This application subscribes to data on an MQTT data topic,
    inserts data values into IQP fields, and published the string back to the broker on a different topic

    Attributes:
        predix_edge_broker - the name of the predix edge broker as defined
                            in our docker-compose file
        topic - either a string or a list of strings indicating which topic(s) to subsrcibe to
        tag_name - string indicating the tag of the data we want to modify
        client - manages relationship with MQTT data broker
    '''

    def __init__(self, predix_edge_broker, publish_broker, pub_topic, sub_topic):
        '''
        Initializes App class with default names for predix_edge_broker,
        a single topic called 'app_data', and a sample tag to look for
        '''
        self.predix_edge_broker = predix_edge_broker
        self.publish_broker = publish_broker
        self.sub_topic = sub_topic        
        self.pub_topic = pub_topic
        self.client = mqtt.Client()

        #add MQTT callbacks and enable logging for easier debugging
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.message_callback_add(self.sub_topic, self.scalar_on_message)
        self.client.enable_logger()

    def on_connect(self, client, userdata, flags, rc):
        '''
        The callback for when the client receives a CONNACK response from the server.
        The variables it takes are part of the underlying MQTT library
        '''
        print("Connected with result code "+str(rc))
        client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, msg):
        '''
        The callback for when a PUBLISH message is received from the server.
        '''
        print(msg.topic+" "+str(msg.payload))

    def on_publish(self, client, userdata, is_published):
        '''
        the callback for when we send something to be published
        '''
        print("Is published " + str(is_published))


    def scalar_on_message(self, client, userdata, msg):
        '''
        Specific callback for our topic
        '''
        #Convert message from bytearray to json object
        payload_as_string = bytes.decode(msg.payload)
        payload = json.loads(payload_as_string)

        iqp_payload = iqp_data(payload)
 
        payload_as_string = json.dumps(iqp_payload)
        client.publish(self.pub_topic, payload_as_string.encode())

def iqp_data(message):
    '''
    This function takes in a JSON message and goes through the body of it
    If an item in the body has the tag we are looking to scale, it scales it and updates the tag name
    '''
    item = message['body']
    length = len(item)
    for i in range(length):
        if item[i]['name'] == "Temp_data":
            tempValue = item[i]['datapoints'][0][1]
            tempTS = datetime.datetime.utcfromtimestamp(item[i]['datapoints'][0][0]).isoformat
        if item[i]['name'] == "Humidity_data":
            humidityValue = item[i]['datapoints'][0][1]
            humidityTS = item[i]['datapoints'][0][0].isoformat
        if item[i]['name'] == "Light_data":
            lightValue = item[i]['datapoints'][0][1]
            lightTS = item[i]['datapoints'][0][0].isoformat
        if item[i]['name'] == "Windspeed_data":
            windSpeedValue = item[i]['datapoints'][0][1]
            windSpeedTS = item[i]['datapoints'][0][0].isoformat
        if item[i]['name'] == "WindDir_data":
            directionValue = item[i]['datapoints'][0][1]
            directionTS = item[i]['datapoints'][0][0].isoformat
        if item[i]['name'] == "Pressure_data":
            pressureValue = item[i]['datapoints'][0][1]
            pressureTS = item[i]['datapoints'][0][0].isoformat

        iqp_string = "met=Temperature~data=%s~desc=celsius~time=%s~lat=37.25113696564767~long=-122.64522661381929~alt=undefined; \
        met=Humidity~data=%s~desc=percent~time=%s~lat=37.25113696564767~long=-122.64522661381929~alt=undefined; \
        met=Light~data=%s~desc=lm~time=%s~lat=37.25113696564767~long=-122.64522661381929~alt=undefined; \
        met=WindSpeed~data=%s~desc=km/h~time=%s~lat=37.25113696564767~long=-122.64522661381929~alt=undefined; \
        met=Direction~data=%s~desc=angle~time=%s~lat=37.25113696564767~long=-122.64522661381929~alt=undefined; \
        met=Pressure~data=%s~desc=psi~time=%s~lat=37.25113696564767~long=-122.64522661381929~alt=undefined" \
        % (tempValue, tempTS, humidityValue, humidityTS, lightValue, lightTS, windSpeedValue, windSpeedTS, directionValue, directionTS, pressureValue, pressureTS)

    return iqp_string

if __name__ == '__main__':
    #Set broker values if we are running locally
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            BROKER = "3.39.89.88"
            SUB_TOPIC = "iqp_data"
            PUB_TOPIC = "IQP_GE/ev1230"
    #Otherwise, read from environment variables
    else:
        try:
            BROKER = os.environ['BROKER']
            SUB_TOPIC = os.environ['SUB_TOPIC']
            PUB_TOPIC = os.environ['PUB_TOPIC']
        except KeyError:
            print(traceback.print_tb(sys.exc_info()[2]))
            sys.exit("Not all of your environment variables are set")
    APP = App(BROKER, PUB_TOPIC, SUB_TOPIC)
    APP.client.connect(APP.predix_edge_broker)
    APP.client.loop_forever()
