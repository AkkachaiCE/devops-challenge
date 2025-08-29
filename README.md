# devops-challenge

## Troubleshooting commands

curl http://localhost:4566/_localstack/health | jq | grep -v "disabled"

docker exec -it aws-localstack env | grep AWS_