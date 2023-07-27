import boto3

def lambda_handler(event, context):
    
    # Create result structure
    result = {
        'Users':[]
    }
    
    # Create an IAM client
    iam_client = boto3.client('iam')
    
    # Get all IAM users
    response = iam_client.list_users()
    users = response['Users']
    
    # Loop through users
    for user in users:
        user_name = user['UserName']
        AWS_policies = []
        customer_policies = []
        
        # Get all policies attached to the user
        response = iam_client.list_attached_user_policies(UserName=user_name)
        attached_policies = response['AttachedPolicies']
        
        # Loop through each attached policy
        for policy in attached_policies:
            policy_arn = policy['PolicyArn']
            
            # Check if customer policy
            if not policy_arn.startswith('arn:aws:iam::aws:policy/'):
            
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
                        customer_policies.append(
                            {
                                'ARN': policy_arn,
                                'StatementWithAsterisk': statement
                            }
                        )
            # Check if AWS policy
            else:
                AWS_policies.append({
                                'ARN': policy_arn
                            })
        
        # append user and relevant policies to result structure 
        result['Users'].append(
            {
                'UserName': user_name,
                'AWSPolicies': AWS_policies,
                'CustomerPoliciesWithAsterisk': customer_policies
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