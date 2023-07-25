# aws-lambda-iam-audit

venv aufbauen
req text einlesen


sam build

sam local invoke HelloNameFunction -e events/events.json

sam deploy --guided
hier auch lternative angeben, also als gesamten befehl oder über config file

sam remote invoke checkUserPolicies --stack-name aws-lambda-iam-audit --event-file events/testEvent.json | jq
install jq for prettier output

if changes

sam build 
und sam deploy wenn config file existier


clean up
sam delete
sam delete --stack-name aws-sam-cli-managed-default    