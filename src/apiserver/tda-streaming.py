import json
from datetime import datetime
import urllib

with open('user.json', 'r') as f:
    user_data = json.loads(f.read())
    print(user_data)

websocket_url = "wss://" + user_data.get('streamerInfo').get('streamerSocketUrl') + "/ws"

#Fill the credentials from the userpriciple
credentials = {

    "userid": user_data['accounts'][0].get('accountId'),
    "token": user_data['streamerInfo'].get('token'),
    "company": user_data['accounts'][0].get('company'),
    "segment": user_data['accounts'][0].get('segment'),
    "cddomain": user_data['accounts'][0].get('accountCdDomainId'),
    "usergroup": user_data['streamerInfo'].get('userGroup'),
    "accesslevel": user_data['streamerInfo'].get('accessLevel'),
    "authorized": "Y",
    "timestamp": int(datetime.timestamp(datetime.strptime(user_data['streamerInfo'].get('tokenTimestamp'), "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
    "appid": user_data['streamerInfo'].get('appId'),
    "acl": user_data['streamerInfo'].get('acl')
}

# Set the authentication message to obtain user principals
authentication_message = {
    "requests": [
        {
            "service": "ADMIN",
            "requestid": "0",
            "command": "LOGIN",
            "account": user_data['accounts'][0].get('accountId'),
            "source": user_data['streamerInfo'].get('appId'),
            "parameters": {
                "credential": urllib.parse.urlencode(credentials),
                "token": user_data['streamerInfo'].get('token'),
                "version": "1.0",
                "qoslevel" : 2
            }
        }
    ]
}
sub_message = {
    "requests" : [
        {
            "service": "QUOTE",
            "requestid": "0",
            "command": "SUBS",
            "account": user_data.get('primaryAccountId'),
            "source": user_data.get('userId'),
            "parameters": {
                "keys": "AAPL",
                "fields": "0,1,2,3,4,5,6,7,8,9"
            }
        }
    ]
}
unsub_message = {
    "requests" : [
        {
            "service": "QUOTE",
            "requestid": "0",
            "command": "UNSUBS",
            "account": user_data.get('primaryAccountId'),
            "source": user_data.get('userId'),
            "parameters": {
                "keys": "AAPL",
                "fields": "0,1,2,3,4,5,6,7,8,9",
                "frequency": "m1"
            }
        }
    ]
}
subscribed = 0
message_count = 0
def on_message(ws, message):
    global subscribed
    global message_count
    message = json.loads(message)
    print("*****Received message")
    print(message)

    if subscribed == 0:
        print("*****Subscribing to quote")
        print(json.dumps(sub_message))
        ws.send(json.dumps(sub_message))
        subscribed = 1
    else:
        print("***************")
        message_count += 1
        if message_count == 50: 
            print("*****Unsubscribing to quote")
            print(json.dumps(unsub_message))
            ws.send(json.dumps(unsub_message))


def on_error(ws, error):
    print(error)

def on_open(ws):
    # Subscribe to real-time data
    print("Connection open. Send the auth message")
    print(json.dumps(authentication_message))
    ws.send(json.dumps(authentication_message))

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed with status code:", close_status_code)
    print("Close message:", close_msg)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(websocket_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_open=on_open,
                            on_close=on_close)

ws.run_forever()
