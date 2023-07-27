import boto3
import json

def lambda_handler(event, context):
    
    # Create result structure
    result = {
        'Buckets':[]
    }
    
    # Create an S3 client
    s3_client = boto3.client('s3')    
    
    # List all S3 buckets
    response = s3_client.list_buckets()
    buckets = response['Buckets']
    
    # Loop through buckets
    for bucket in buckets:
        bucket_name = bucket['Name']
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        location_constraint = response.get('LocationConstraint')
        
        # Check if bucket from a specific region
        if location_constraint == 'eu-west-1':
            statements_with_asterisk = []
            
            # Get the policy for the bucket
            response = s3_client.get_bucket_policy(Bucket=bucket_name)
            attached_policy = response['Policy']
            policy_document = json.loads(attached_policy)
            
            # Loop through statements of the policy document
            statements = policy_document['Statement']
            for statement in statements:
                    
                # Check the statement for asterisks in either the resource or action field
                if asterisk_in_statement(statement):
                    statements_with_asterisk.append(
                        {
                            'Statement': statement
                        }
                    )
        
            # append user and relevant policies to result structure 
            result['Buckets'].append(
                {
                    'BucketName': bucket_name,
                    'StatementsWithAsterisk': statements_with_asterisk
                }
            )
    
    return result
    
    
def asterisk_in_statement(statement):
        
    # Check if an asterisk is present in actions or resource field of the statement
    if 'Action' in statement and 'Allow' in statement['Effect'] and '*' in statement['Action']:
        return True
    elif 'Resource' in statement and 'Allow' in statement['Effect'] and '*' in statement['Resource']:
        return True

    return False