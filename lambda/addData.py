import boto3
import uuid
import time
import json

cognitoClient = boto3.client('cognito-idp')

ddbClient = boto3.resource('dynamodb')
pasteTable = ddbClient.Table('paste')

def lambda_handler(event, context):
    request_body = json.loads(event['body'])
    contentType = request_body['content_type']
    content = request_body['content']
    print(event)
    
    headers = {}
    if 'headers' in event:
        headers = event['headers']
        print(headers)
        
        
    userId = ""
    if 'access-token' in headers:
        access_token = headers['access-token']
        print(access_token)
        
        try:
            user_info = cognitoClient.get_user(AccessToken = access_token)
            
            print("User Info:")
            print(user_info)
            
            user_attrs = user_info['UserAttributes']
            
            for user_attr in user_attrs:
                name = user_attr['Name']
                value = user_attr['Value']
                
                if name == 'sub':
                    userId = value
        except:
            userId = ""
    
    if userId == "":
        print("Invalid access token: " + access_token)
        return {
            'statusCode': 403,
            'body': "Invalid access token: " + access_token
        }
    
    pasteId = str(uuid.uuid4())
    pasteTime = int(time.time())
    
    input = { 'pasteId': pasteId, 'userId': userId, 'content': content, 'pasteTime': pasteTime }
    response = pasteTable.put_item(Item=input)
    
    return {
        'statusCode': 200,
        'body': content
    }
    