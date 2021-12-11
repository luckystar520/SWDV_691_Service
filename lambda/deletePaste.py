import json
import boto3
import decimal
import ast
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    cognitoClient = boto3.client('cognito-idp')

    ddbClient = boto3.resource('dynamodb')
    pasteTable = ddbClient.Table('paste')

    request_body = json.loads(event['body'])
    print(request_body)
    request_pasteId = request_body['pasteId']
    print(request_pasteId)
    
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
        KeyConditionExpression=Key('pasteId').eq(request_pasteId)
    )
    
    print(data)
    
    with pasteTable.batch_writer() as batch:
        for item in data['Items']:
            print(item)
            batch.delete_item(Key={'pasteId': item['pasteId']})
    
    return {
        'statusCode': 200,
        'body': request_pasteId
    }