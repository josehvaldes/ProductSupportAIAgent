
##Source
{
	"id": "B008IFXQFU",
	"title": "TP-Link USB WiFi ...",
	"category": "WirelessUSBAdapters",
	"price": 10.99,
	"rating": 4.2,
	"description": "USB WiFi Adapter ",
	"review_count": 179691.0,
	"product_url": "link here",
	"image_url": "lnk here",
	"category_full": [
		"Computers&Accessories",
		"NetworkingDevices",
	],
	"vector_text": "combined title description here",
	"vector_metadata": {
		"total_tokens": 530,
		"total_vectors": 2,
		"total_storage_mb": 0.005859375
	},
	"chunks":[
		"First chunk",
		"Second chunk"
	],
	"brand": "TP-Link"
},

##CosmosDB
{
  "id": "",
  "title": "TP-Link USB WiFi Adapter",
  "description": "USB WiFi Adapter for PC...",
  "category": "WirelessUSBAdapters",
  "price": 10.99,
  "brand": "TP-Link",
  "rating": 4.2,
  "review_count": 179691,
  "product_url": "...",
  "image_url": "...",
  "category_full": ["Computers&Accessories", "NetworkingDevices"],
  "availability": "in_stock",
  
  // Add this for convenience:
  "total_chunks": 2,  // ← Useful to know how many chunks exist
  
  // Partition key for Cosmos DB
  "_partitionKey": "WirelessUSBAdapters"  // ← category for efficient queries
}


##MILVUS
{
  "id": "B008IFXQFU_chunk_0",  // ← Unique per chunk
  "product_id": "B008IFXQFU",   // ← Link to Cosmos DB
  "text": "TP-Link USB WiFi Adapter. USB WiFi Adapter for PC...",
  "embedding": [0.123, 0.456, ..., 0.789],  // ← 1536-dimensional vector
  
  // Metadata for filtering
  "chunk_index": 0,
  "total_chunks": 2,
  "category": "WirelessUSBAdapters",
  "price": 10.99,
  "brand": "TP-Link"  // ← Add this for brand filtering
}
from pymilvus import CollectionSchema, FieldSchema, DataType

fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
    FieldSchema(name="product_id", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="chunk_index", dtype=DataType.INT64),
    FieldSchema(name="total_chunks", dtype=DataType.INT64),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="price", dtype=DataType.FLOAT),
    FieldSchema(name="brand", dtype=DataType.VARCHAR, max_length=100)
]

schema = CollectionSchema(fields, description="Product chunks")


##AZURE AI Search
{
  "id": "B008IFXQFU_chunk_0",
  "product_id": "B008IFXQFU",
  "title": "TP-Link USB WiFi Adapter",  // ← Keep title for keyword matching
  "text": "TP-Link USB WiFi Adapter. USB WiFi Adapter for PC...",
  "chunk_index": 0,
  "total_chunks": 2,
  
  // Searchable/filterable fields
  "category": "WirelessUSBAdapters",
  "price": 10.99,
  "brand": "TP-Link",
  
  // For hybrid search
  "embedding": [0.123, 0.456, ..., 0.789]
}

##Schema
{
  "name": "products-chunks-index",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true, "searchable": false},
    {"name": "product_id", "type": "Edm.String", "filterable": true},
    {"name": "title", "type": "Edm.String", "searchable": true},
    {"name": "text", "type": "Edm.String", "searchable": true},
    {"name": "chunk_index", "type": "Edm.Int32", "filterable": true},
    {"name": "total_chunks", "type": "Edm.Int32"},
    {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "price", "type": "Edm.Double", "filterable": true, "sortable": true},
    {"name": "brand", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "embedding", "type": "Collection(Edm.Single)", "searchable": true, "dimensions": 1536}
  ]
}

