from qdrant_client import QdrantClient
import os

try:
    path = "./qdrant_data_test"
    if not os.path.exists(path):
        os.makedirs(path)
    
    print(f"Initializing Qdrant at {path}...")
    client = QdrantClient(path=path)
    print("Success!")
    
    # Try to create a collection
    from qdrant_client.models import Distance, VectorParams
    client.create_collection(
        collection_name="test",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print("Collection created!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
