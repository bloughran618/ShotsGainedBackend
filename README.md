### ShotsGainedBackend
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
curl -X POST -H "Content-Type: application/json" -d "{\"userName\": \"terminal\", \"name\": \"hello from terminal\"}" https://qxzavge998.execute-api.us-east-1.amazonaws.com/prod/create_user
```
read_user
```commandline
curl -X POST -H "Content-Type: application/json" -d "{\"userName\": \"terminal\"}" https://qoe10ch059.execute-api.us-east-1.amazonaws.com/prod/read_user
```

calc_shots_gained
```commandline
curl -X POST -H "Content-Type: application/json" -d "{\"from\": {\"distance\": 450, \"type\": \"TEE\"}, \"to\": {\"distance\": 115, \"type\": \"FAIRWAY\"}}" https://w3aubvrrb2.execute-api.us-east-1.amazonaws.com/prod/calc_shots_gained
```

create_round
```commandline
curl -X POST -H "Content-Type: application/json" -d "{\"userName\": \"bloughran\", \"date\": \"06/18/2023\", \"course\": \"Stanley Golf Course\"}" https://iwptv1bljk.execute-api.us-east-1.amazonaws.com/prod/create_round
```

add_hole
```commandline
curl -X POST -H "Content-Type: application/json" -d "{\"userName\": \"bloughran\", \"round\": \"06/18/2023-Stanley Golf Course\", \"shots\":[{\"distance\":450,\"type\":\"tee\"},{\"distance\":115,\"type\":\"fairway\"},{\"distance\":10,\"type\":\"green\"}]}" https://w4czh68x0d.execute-api.us-east-1.amazonaws.com/prod/add_hole
```

finish_round
```commandline
curl -X POST -H "Content-Type: application/json" -d "{\"userName\": \"bloughran\", \"round\": \"06/18/2023-Stanley Golf Course\"}" https://70ir634x4c.execute-api.us-east-1.amazonaws.com/prod/finish_round
```

### TODO:
- Show how to run unittests locally
- Show how to run integration tests locally 
- Show how to run all tests locally
- Finish integration tests
- Replicate beta/gamma env's
- Break out lambda_execution_policy permissions
