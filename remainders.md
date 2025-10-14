#remainders

az deployment group what-if --resource-group rg-shopassistai-test-01 --template-file storage_setup.bicep --parameters storage.parameters.json

az deployment group create --resource-group rg-shopassistai-test-01 --template-file storage_setup.bicep --parameters storage.parameters.json

az deployment group create --name deploy-milvus --resource-group rg-milvus-test-01 --template-file main.bicep --parameters adminPassword=<passwordhere>

