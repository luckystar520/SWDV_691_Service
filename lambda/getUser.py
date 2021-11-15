import json
import boto3

client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    '''
    print('event')
    print(event)
    
    print('context')
    print(context)
    '''
    response = {}
    
    headers = {}
    if 'headers' in event:
        headers = event['headers']
        
    if 'access-token' in headers:
        access_token = headers['access-token']
        
        try:
            user_info = client.get_user(AccessToken = access_token)
            
            user_attrs = user_info['UserAttributes']
            
            userid = ""
            username = ""
            
            for user_attr in user_attrs:
                name = user_attr['Name']
                value = user_attr['Value']
                
                if name == 'sub':
                    userid = value
                elif name == 'name':
                    username = value
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'userid': userid,
                    'username': username
                })
            }
        except:
            print("Invalid access token: " + access_token)
    
    return {
        'statusCode': 400,
        'body': "Invalid access token: " + access_token
    }

