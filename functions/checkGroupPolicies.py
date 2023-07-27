import boto3

def lambda_handler(event, context):
    
    # Create result structure
    result = {
        'Groups':[]
    }
    
    # Create an IAM client
    iam_client = boto3.client('iam')
    
    # Get all IAM groups
    response = iam_client.list_groups()
    groups = response['Groups']
    
    # Loop through groups
    for group in groups:
        group_name = group['GroupName']
        users_in_group = []
        AWS_policies = []
        customer_policies = []
        
        # Get all policies attached to the group
        response = iam_client.list_attached_group_policies(GroupName=group_name)
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
                    
        # Get users from the group
        response = iam_client.get_group(GroupName=group_name)
        users = response['Users']
        
        # Loop through users and add user names to result
        for user in users:
            users_in_group.append(user['UserName'])
        
        # append group name, user names and relevant statements to result structure 
        result['Groups'].append(
            {
                'GroupName': group_name,
                'UsersInGroup': users_in_group,
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