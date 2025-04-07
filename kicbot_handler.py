from kicbot import create_message


def lambda_handler():
    return {
        'statusCode': 200,
        'body': f'Hello from kicbot test handler: {create_message}'
    }
