# devops-challenge

## Start Project

docker compose up -d

terraform plan -var-file="./environments/env.tfvars"
terraform apply -var-file="./environments/env.tfvars"

aws s3api create-bucket \
  --bucket ducket-bucket-0829 \
  --region us-east-1 \
  --endpoint-url=http://localhost:4566

aws s3api list-buckets --endpoint-url=http://localhost:4566

awslocal iam list-policies --scope Local


## End Project

docker compose down

## Troubleshooting commands

curl http://localhost:4566/_localstack/health | jq | grep -v "disabled"

docker exec -it aws-localstack env | grep AWS_