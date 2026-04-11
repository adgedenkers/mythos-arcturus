# workers/embedding_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 94

---

### File: workers/embedding_worker.py

#### Purpose
This file contains the logic for generating text embeddings using a pre-trained model and storing these embeddings in a Qdrant vector database. It processes incoming payloads containing text messages and their metadata, generating embeddings and storing them with relevant metadata.

#### Architecture
The file is structured around three main functions:
1. `get_model`: Lazy loads and returns a sentence-transformers model.
2. `get_qdrant`: Lazy loads and returns a Qdrant client instance.
3. `process_embedding`: Processes an incoming payload to generate and store a text embedding.

The file uses global variables `_model` and `_qdrant` to ensure that the model and Qdrant client are only loaded once.

#### Patterns
- **Lazy Initialization**: The `get_model` and `get_qdrant` functions use lazy initialization to load the model and Qdrant client only when needed.
- **Singleton Pattern**: The global variables `_model` and `_qdrant` act as singletons, ensuring that only one instance of the model and client are created throughout the application.

#### Dependencies
- **Standard Libraries**: `os`, `logging`
- **External Libraries**: `typing`, `datetime`, `dotenv`, `sentence_transformers`, `qdrant_client`

#### Interfaces
- **Functions Exposed**:
  - `get_model()`: Returns the sentence-transformers model.
  - `get_qdrant()`: Returns the Qdrant client instance.
  - `process_embedding(payload: Dict[str, Any]) -> Dict[str, Any]`: Processes a payload to generate and store a text embedding.

#### Database
- **Qdrant**: The file interacts with the Qdrant vector database to store text embeddings in the `text_embeddings` collection.

#### Configuration
- **Environment Variables**: The file loads environment variables from `/opt/mythos/.env` using `dotenv.load_dotenv()`. It specifically uses `QDRANT_HOST` and `QDRANT_PORT` to configure the Qdrant client.

#### Key Logic
1. **Model Initialization**: The `get_model` function initializes the `SentenceTransformer` model with the pre-trained model `"all-MiniLM-L6-v2"`.
2. **Qdrant Client Initialization**: The `get_qdrant` function initializes the Qdrant client with host and port values from environment variables.
3. **Embedding Generation and Storage**:
   - The `process_embedding` function extracts necessary metadata from the payload.
   - It checks if the content is empty and logs a warning if so.
   - It generates an embedding using the loaded model.
   - It stores the embedding in Qdrant with additional metadata such as `user_uuid`, `conversation_id`, `content_preview`, `content_length`, `message_type`, and `created_at`.

#### Integration Points
- **Message Queue/Bus**: This worker is likely integrated with a message queue or bus system (e.g., RabbitMQ, Kafka) where it consumes messages (payloads) containing text and metadata.
- **Qdrant**: The worker integrates with the Qdrant vector database to store the generated embeddings.
- **Logging**: The worker logs information and errors using the Python `logging` module, which can be integrated with a centralized logging system.

### Summary
The `embedding_worker.py` file is a critical component of the Mythos system, responsible for generating text embeddings and storing them in Qdrant. It uses lazy initialization and singleton patterns to efficiently manage resources and integrates with environment configurations and logging systems.
