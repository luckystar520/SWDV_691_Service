import json
import boto3
import decimal
import ast
from boto3.dynamodb.conditions import Key

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    cognitoClient = boto3.client('cognito-idp')
    
    ddbClient = boto3.resource('dynamodb')
    pasteTable = ddbClient.Table('paste')
    
    headers = {}
    if 'headers' in event:
        headers = event['headers']
        print(headers)
        
    userEmail = ""
    access_token = ""
    if 'access-token' in headers:
        access_token = headers['access-token']
        print(access_token)
        
        try:
            user_info = cognitoClient.get_user(AccessToken = access_token)
            print("User Info: ")
            print(user_info)
            
            user_attrs = user_info['UserAttributes']
            for user_attr in user_attrs:
                name = user_attr['Name']
                value = user_attr['Value']
                
                if name == 'email':
                    userEmail = value
        except Exception as e:
            userEmail = ""
            print(e)
    
    if userEmail == "":
        print("Invalid access token: " + access_token)
        return {
            'statusCode': 403,
            'body': "Invalid access token: " + access_token
        }
        
    data = pasteTable.query(
        IndexName="username-pasteTime-index",
        KeyConditionExpression=Key('username').eq(userEmail)
    )

    items = []
    for item in data['Items']:
        item['pasteTime'] = str(item['pasteTime'])
        items.append(item)
    
    print(items)
    json_str = json.dumps({'items': items})
    print(json_str)
    
    return {
        'statusCode': 200,
        'body': json_str
    }
