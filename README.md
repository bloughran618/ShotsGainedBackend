This repo is the backend for ShotGained golf shot tracking and improvement app

Some commands

```agsl
tarraform init
terraform plan
terraform apply
terraform destroy
```

But really you just need 
```agsl
terraform apply
```

APIGW endpoint examples from terminal:
create_user
```commandline
curl -X POST -H "Content-Type: application/json" -d '{"userName": "terminal", "name": "hello from terminal"}' https://qxzavge998.execute-api.us-east-1.amazonaws.com/prod/create_user
```
read_user
```commandline
curl -X POST -H "Content-Type: application/json" -d '{"userName": "terminal"}' https://qoe10ch059.execute-api.us-east-1.amazonaws.com/prod/read_user
```
