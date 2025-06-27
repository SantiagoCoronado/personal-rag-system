import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from openai import RateLimitError

from app.services.embeddings import EmbeddingService, embedding_service
from app.models import Document, Embedding, User
from app.database import get_db


class TestEmbeddingService:
    """Test suite for Task 8: Embedding Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.service = EmbeddingService()
        self.mock_db = Mock(spec=Session)
        
    def test_service_initialization(self):
        """Test that embedding service initializes correctly"""
        assert self.service.model == "text-embedding-ada-002"
        assert self.service.batch_size == 100
        assert self.service.max_retries == 3
        assert self.service.client is not None
    
    @patch('app.services.embeddings.OpenAI')
    def test_generate_embedding_success(self, mock_openai):
        """Test successful single embedding generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        mock_client = Mock()
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = EmbeddingService()
        service.client = mock_client
        
        result = service.generate_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_client.embeddings.create.assert_called_once_with(
            input="test text",
            model="text-embedding-ada-002"
        )
    
    def test_generate_embedding_empty_text(self):
        """Test that empty text raises ValueError"""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.service.generate_embedding("")
            
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.service.generate_embedding("   ")
    
    @patch('app.services.embeddings.OpenAI')
    @patch('time.sleep')
    def test_generate_embedding_rate_limit_retry(self, mock_sleep, mock_openai):
        """Test rate limit handling with retry logic"""
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = [
            RateLimitError("Rate limit", response=Mock(), body=Mock()),
            RateLimitError("Rate limit", response=Mock(), body=Mock()),
            Mock(data=[Mock(embedding=[0.1, 0.2, 0.3])])
        ]
        
        mock_openai.return_value = mock_client
        service = EmbeddingService()
        service.client = mock_client
        
        result = service.generate_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]
        assert mock_client.embeddings.create.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries
    
    @patch('app.services.embeddings.OpenAI')
    def test_batch_generate_embeddings_success(self, mock_openai):
        """Test successful batch embedding generation"""
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
            Mock(embedding=[0.7, 0.8, 0.9])
        ]
        
        mock_client = Mock()
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = EmbeddingService()
        service.client = mock_client
        
        texts = ["text1", "text2", "text3"]
        result = service.batch_generate_embeddings(texts)
        
        expected = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        assert result == expected
        mock_client.embeddings.create.assert_called_once_with(
            input=texts,
            model="text-embedding-ada-002"
        )
    
    def test_batch_generate_embeddings_empty_list(self):
        """Test batch generation with empty list"""
        result = self.service.batch_generate_embeddings([])
        assert result == []
    
    @patch('app.services.embeddings.OpenAI')
    def test_batch_generate_embeddings_large_batch(self, mock_openai):
        """Test batch processing with batches larger than batch_size"""
        mock_client = Mock()
        
        # Mock responses for two batches
        mock_response1 = Mock()
        mock_response1.data = [Mock(embedding=[i, i+1, i+2]) for i in range(100)]
        
        mock_response2 = Mock()
        mock_response2.data = [Mock(embedding=[i, i+1, i+2]) for i in range(100, 150)]
        
        mock_client.embeddings.create.side_effect = [mock_response1, mock_response2]
        mock_openai.return_value = mock_client
        
        service = EmbeddingService()
        service.client = mock_client
        service.batch_size = 100
        
        texts = [f"text{i}" for i in range(150)]
        result = service.batch_generate_embeddings(texts)
        
        assert len(result) == 150
        assert mock_client.embeddings.create.call_count == 2
    
    def test_store_embeddings_success(self):
        """Test successful embedding storage"""
        # Mock document
        mock_document = Mock()
        mock_document.id = 1
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_document
        
        # Mock existing embeddings query
        self.mock_db.query.return_value.filter.return_value.delete.return_value = None
        
        chunks = ["chunk1", "chunk2", "chunk3"]
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        
        result = self.service.store_embeddings(self.mock_db, 1, chunks, embeddings)
        
        assert result is True
        assert self.mock_db.add.call_count == 3
        self.mock_db.commit.assert_called_once()
    
    def test_store_embeddings_document_not_found(self):
        """Test storing embeddings when document doesn't exist"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.service.store_embeddings(self.mock_db, 999, ["chunk"], [[0.1, 0.2]])
        
        assert result is False
        self.mock_db.add.assert_not_called()
        self.mock_db.commit.assert_not_called()
    
    def test_store_embeddings_database_error(self):
        """Test handling database errors during storage"""
        mock_document = Mock()
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_document
        self.mock_db.commit.side_effect = Exception("Database error")
        
        result = self.service.store_embeddings(self.mock_db, 1, ["chunk"], [[0.1, 0.2]])
        
        assert result is False
        self.mock_db.rollback.assert_called_once()
    
    def test_search_similar_chunks_success(self):
        """Test successful similarity search"""
        # Mock embeddings
        mock_embedding1 = Mock()
        mock_embedding1.id = 1
        mock_embedding1.document_id = 1
        mock_embedding1.chunk_text = "chunk1"
        mock_embedding1.chunk_index = 0
        mock_embedding1.embedding = [1.0, 0.0, 0.0]
        mock_embedding1.document = Mock()
        mock_embedding1.document.filename = "test.pdf"
        
        mock_embedding2 = Mock()
        mock_embedding2.id = 2
        mock_embedding2.document_id = 1
        mock_embedding2.chunk_text = "chunk2"
        mock_embedding2.chunk_index = 1
        mock_embedding2.embedding = [0.0, 1.0, 0.0]
        mock_embedding2.document = Mock()
        mock_embedding2.document.filename = "test.pdf"
        
        self.mock_db.query.return_value.all.return_value = [mock_embedding1, mock_embedding2]
        
        query_embedding = [0.9, 0.1, 0.0]  # More similar to first embedding
        
        result = self.service.search_similar_chunks(self.mock_db, query_embedding, limit=2)
        
        assert len(result) == 2
        assert result[0]['similarity'] > result[1]['similarity']  # First should be more similar
        assert result[0]['chunk_text'] == "chunk1"
        assert result[0]['document_filename'] == "test.pdf"
    
    def test_search_similar_chunks_with_user_filter(self):
        """Test similarity search filtered by user"""
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        result = self.service.search_similar_chunks(self.mock_db, [0.1, 0.2], user_id=1)
        
        assert result == []
        mock_query.join.assert_called_once()
    
    def test_search_similar_chunks_empty_database(self):
        """Test similarity search with no embeddings in database"""
        self.mock_db.query.return_value.all.return_value = []
        
        result = self.service.search_similar_chunks(self.mock_db, [0.1, 0.2])
        
        assert result == []
    
    def test_get_document_chunks_success(self):
        """Test successful retrieval of document chunks"""
        mock_embedding1 = Mock()
        mock_embedding1.id = 1
        mock_embedding1.chunk_text = "chunk1"
        mock_embedding1.chunk_index = 0
        mock_embedding1.embedding = [0.1, 0.2]
        
        mock_embedding2 = Mock()
        mock_embedding2.id = 2
        mock_embedding2.chunk_text = "chunk2"
        mock_embedding2.chunk_index = 1
        mock_embedding2.embedding = [0.3, 0.4]
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [
            mock_embedding1, mock_embedding2
        ]
        self.mock_db.query.return_value = mock_query
        
        result = self.service.get_document_chunks(self.mock_db, 1)
        
        assert len(result) == 2
        assert result[0]['chunk_text'] == "chunk1"
        assert result[1]['chunk_text'] == "chunk2"
        assert result[0]['chunk_index'] == 0
        assert result[1]['chunk_index'] == 1
    
    def test_get_document_chunks_empty(self):
        """Test getting chunks for document with no chunks"""
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        result = self.service.get_document_chunks(self.mock_db, 999)
        
        assert result == []
    
    def test_cosine_similarity_calculation(self):
        """Test that cosine similarity is calculated correctly"""
        # Test vectors
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])  # Identical
        vec3 = np.array([0.0, 1.0, 0.0])  # Orthogonal
        
        # Calculate similarities manually
        sim_identical = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        sim_orthogonal = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))
        
        assert abs(sim_identical - 1.0) < 1e-10  # Should be 1.0
        assert abs(sim_orthogonal - 0.0) < 1e-10  # Should be 0.0
    
    def test_global_service_instance(self):
        """Test that global embedding service instance exists"""
        assert embedding_service is not None
        assert isinstance(embedding_service, EmbeddingService)


# Integration test with actual database setup
@pytest.fixture
def test_db():
    """Create test database session"""
    from app.database import engine, SessionLocal
    from app.models import Base
    
    # Create test tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)


def test_embedding_service_integration(test_db):
    """Integration test for embedding service with real database"""
    # Create test user
    from app.models import User, Document
    
    user = User(email="test@example.com", hashed_password="hashed")
    test_db.add(user)
    test_db.commit()
    
    # Create test document
    document = Document(
        user_id=user.id,
        filename="test.pdf",
        file_path="/path/to/test.pdf"
    )
    test_db.add(document)
    test_db.commit()
    
    # Test storing embeddings
    service = EmbeddingService()
    chunks = ["This is chunk 1", "This is chunk 2"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    
    success = service.store_embeddings(test_db, document.id, chunks, embeddings)
    assert success is True
    
    # Test retrieving chunks
    retrieved_chunks = service.get_document_chunks(test_db, document.id)
    assert len(retrieved_chunks) == 2
    assert retrieved_chunks[0]['chunk_text'] == "This is chunk 1"
    assert retrieved_chunks[1]['chunk_text'] == "This is chunk 2"
    
    # Test similarity search
    query_embedding = [0.1, 0.2, 0.3]  # Similar to first chunk
    similar_chunks = service.search_similar_chunks(
        test_db, query_embedding, user_id=user.id, limit=1
    )
    assert len(similar_chunks) == 1
    assert similar_chunks[0]['chunk_text'] == "This is chunk 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])