from datetime import datetime
import json

from flask import Flask
from flask import request

from data import users, notifications

app = Flask(__name__)

# get auth token from headers
def get_auth_token(request):
    auth_header = request.headers['Authorization']
    auth_token = auth_header.split(' ')[1]
    return auth_token

# get the last pulled at time from GET parameters
def get_last_pulled_at(request):
    try:
        return int(request.args.get('last_pulled_at', '0'))
    except:
        return 0

# get the schema version from GET parameters
def get_schema_version(request):
    try:
        return int(request.args.get('get_schema_version', '1'))
    except:
        return 1


def pull(request):
    auth_token = get_auth_token(request)
    last_pulled_at = get_last_pulled_at(request)
    schema_version = get_schema_version(request)

    print(f'Auth token: {auth_token}')
    print(f'Last pulled at: {last_pulled_at}')
    print(f'Schema version: {schema_version}')

    # get the user from the JWT (decoding the JWT and get user data)
    my_user = [user for user in users if user.get('access_token') == auth_token][0]

    # query the database for items created after the 'last pulled at' time
    notifications_created = []
    my_ids = [my_user.get('id'), *my_user.get('groups')]
    for notification in notifications:
        # get notifications sent to me and notifications sent to a group I belong to
        if notification.get('to') in my_ids:
            notifications_created.append(notification)

    timestamp = datetime.now().toordinal()

    if last_pulled_at == 0:
        response = {
            "changes": {
                "notifications": {
                    "created": notifications_created,
                    "updated": [],
                    "deleted": [],
                },
            },
            "timestamp": timestamp,
        }

    else:
        # query the database for items updated after the 'last pulled at' time

        # fake an update
        notification_to_update = notifications[2]
        notification_to_update['title'] = "Archery: one space available!"

        notifications_updated = []
        if notification.get('to') in my_ids:
            notifications_updated.append(notification_to_update)

        # query the database for items deleted after the 'last pulled at' time

        # fake a delete
        notifications_deleted = []
        notification_to_delete = notifications[3]

        # we only need the ids of items deleted - would need to store them in the database (with a timestamp) if records are actually deleted
        if notification_to_delete.get('to') in my_ids:
            notifications_deleted = [notification_to_delete.get('id')]

        response = {
            "changes": {
                "notifications": {
                    "created": [],
                    "updated": notifications_updated, 
                    "deleted": notifications_deleted,
                },
            },
            "timestamp": timestamp,
        }

    return json.dumps(response)

def push(request):
    auth_token = get_auth_token(request)
    last_pulled_at = get_last_pulled_at(request)

    print(request.data)
    # If something is created in the app and pushed, the following data is available in the request data
    # {"notifications":{"created":[{"id":"ygz6B0mJCxiSpkB4","_status":"created","_changed":"","title":"New notification","subtitle":null,"body":"Lorem ipsum...","from":null,"to":"","is_sos":false,"latlng":null,"created_at":1728316735928}],"updated":[],"deleted":[]}}
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route("/")
def root():
    return """
    <html>
    <a href='https://watermelondb.dev/docs/Sync/Backend#existing-backend-implementations'>See WatermelonDB docs</a>
    </html>
    """


@app.route("/sync", methods=['GET', 'POST'])
def sync():
    if request.method == 'POST':
        return push(request)
    return pull(request)
    