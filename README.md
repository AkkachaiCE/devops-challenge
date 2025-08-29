# devops-challenge

## Start Project

docker compose up -d

terraform plan -var-file="./environments/env.tfvars"

## End Project

docker compose down

## Troubleshooting commands

curl http://localhost:4566/_localstack/health | jq | grep -v "disabled"

docker exec -it aws-localstack env | grep AWS_