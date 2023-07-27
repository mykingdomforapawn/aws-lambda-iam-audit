import boto3
import json

def lambda_handler(event, context):
    
    # Create result structure
    result = {
        'Lambdas':[]
    }
    
    # Create an S3 client
    lambda_client = boto3.client('lambda')    
    
    # List all Lambda functions
    response = lambda_client.list_functions()
    functions = response['Functions']
    
    # Loop through Lambda functions
    for function in functions:
        function_name = function['FunctionName']
        statements_with_asterisk = []
        
        # Get the policy for the bucket
        try:
            response = lambda_client.get_policy(FunctionName=function_name)
        except lambda_client.exceptions.ResourceNotFoundException:
            result['Lambdas'].append(
                {
                    'FunctionName': function_name,
                    'StatementsWithAsterisk': statements_with_asterisk
                }
            )
            continue
            
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
        result['Lambdas'].append(
            {
                'FunctionName': function_name,
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