//Decompiled not tested yet
//usage: az deployment group create --resource-group <your-resource-group> --template-file cosmosdb_setup.bicep --parameters @cosmosdb.parameters.json
@description('Name of the Cosmos DB account')

param name string
param location string
param locationName string
param defaultExperience string

resource name_resource 'Microsoft.DocumentDb/databaseAccounts@2025-05-01-preview' = {
  name: name
  location: location
  tags: {
    defaultExperience: defaultExperience
    'hidden-workload-type': 'Learning'
    'hidden-cosmos-mmspecial': ''
  }
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        failoverPriority: 0
        locationName: locationName
      }
    ]
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Local'
      }
    }
    isVirtualNetworkFilterEnabled: false
    virtualNetworkRules: []
    ipRules: []
    minimalTlsVersion: 'Tls12'
    capabilities: []
    capacityMode: 'Serverless'
    enableFreeTier: false
    capacity: {
      totalThroughputLimit: 4000
    }
    disableLocalAuth: false
  }
}
