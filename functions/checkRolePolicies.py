import boto3
from datetime import datetime

def lambda_handler(event, context):
    
    # Create result structure
    result = {
        'ExecutionDate': datetime.now().isoformat(timespec='seconds'),
        'Roles':[]
    }
    
    # Create an IAM client
    iam_client = boto3.client('iam')
    
    # Get all IAM roles
    response = iam_client.list_roles()
    roles = response['Roles']
    
    # Loop through roles
    for role in roles:
        
        # Check if AWS service linked role
        if not role['Path'].startswith('/aws-service-role/'):
            role_name = role['RoleName']
            assume_role_policy = role['AssumeRolePolicyDocument']
            statements_with_asterisk = []
            
            # Get all policies attached to the role
            response = iam_client.list_attached_role_policies(RoleName=role_name)
            attached_policies = response['AttachedPolicies']
            
            # Loop through each attached policy
            for policy in attached_policies:
                policy_arn = policy['PolicyArn']
                
                # Get the details of the policy
                response = iam_client.get_policy(PolicyArn=policy_arn)
                policy_version_arn = response['Policy']['DefaultVersionId']
                
                response = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version_arn)
                policy_document = response['PolicyVersion']['Document']
                
                # Loop through statements of the policy document
                statements = policy_document['Statement']
                for statement in statements:
                    
                    # Check the statement for asterisks in either the resource or action field
                    if asterisk_in_statement(statement):
                        statements_with_asterisk.append(
                            {
                                'PolicyArn': policy_arn,
                                'Statement': statement
                            }
                        )
        
            # append group name, user names and relevant statements to result structure 
            result['Roles'].append(
                {
                    'RoleName': role_name,
                    'AssumeRolePolicyDocument': assume_role_policy,
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