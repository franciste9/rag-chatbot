"""Flask app entry point - SIMPLIFIED VERSION WITH DEBUG OUTPUT"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import sys
import traceback
import threading
import uuid
import config

config.validate_config()

# Set up frontend path
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Global service instances (lazy-loaded)
processor = None
retriever = None
chat_service = None
_init_lock = threading.Lock()


def init_services():
    """Initialize services on first use"""
    global processor, retriever, chat_service

    with _init_lock:
        if processor is None:
            try:
                logger.info("Initializing DocumentProcessor...")
                from ingestion import DocumentProcessor
                processor = DocumentProcessor()
                logger.info("✅ DocumentProcessor initialized")
            except Exception as e:
                logger.error(f"❌ DocumentProcessor failed: {str(e)}")
                raise

        if retriever is None:
            try:
                logger.info("Initializing RetrieverService...")
                from retrieval import RetrieverService
                retriever = RetrieverService()
                logger.info("✅ RetrieverService initialized")
            except Exception as e:
                logger.error(f"❌ RetrieverService failed: {str(e)}")
                logger.error(traceback.format_exc())
                raise

        if chat_service is None:
            try:
                logger.info("Initializing ChatService...")
                from chat import ChatService
                chat_service = ChatService()
                logger.info("✅ ChatService initialized")
            except Exception as e:
                logger.error(f"❌ ChatService failed: {str(e)}")
                raise


@app.errorhandler(Exception)
def handle_error(e):
    """Global error handler"""
    logger.error(f"❌ EXCEPTION: {str(e)}")
    logger.error(traceback.format_exc())
    print(f"\n{'='*60}")
    print(f"ERROR: {str(e)}")
    print(f"{'='*60}\n")
    return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/', methods=['GET'])
def serve_index():
    """Serve frontend index.html"""
    return send_from_directory(frontend_dir, 'index.html')


@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files"""
    return send_from_directory(frontend_dir, path)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200


@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process a PDF document"""
    logger.info("Upload request received")
    
    try:
        init_services()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename or not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDFs allowed'}), 400

        safe_name = secure_filename(file.filename)
        temp_path = f'/tmp/{uuid.uuid4()}_{safe_name}'
        file.save(temp_path)
        logger.info(f"Processing file: {file.filename}")
        
        try:
            result = processor.process_document(temp_path)
            doc_id = str(uuid.uuid4())
            
            # Store in Pinecone
            retriever.store_chunks(result['chunks'], result['embeddings'], doc_id)
            
            logger.info(f"✅ Document processed: {file.filename} ({len(result['chunks'])} chunks)")
            
            return jsonify({
                'filename': file.filename,
                'doc_id': doc_id,
                'num_chunks': result['num_chunks'],
                'text_length': len(result['text']),
                'status': 'processed'
            }), 200
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    """Search for relevant chunks"""
    logger.info("Search request received")
    
    try:
        init_services()
        
        data = request.json or {}
        query = data.get('query')
        top_k = data.get('top_k', 5)
        doc_id = data.get('doc_id')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        logger.info(f"Searching for: {query}")
        results = retriever.search(query, top_k=top_k, doc_id=doc_id)
        logger.info(f"Found {len(results)} results")
        
        return jsonify({'results': results}), 200
        
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with retrieval and LLM"""
    logger.info("Chat request received")
    
    try:
        init_services()
        
        data = request.json or {}
        query = data.get('query')
        doc_id = data.get('doc_id')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        logger.info(f"Chat query: {query} (doc_id={doc_id or 'all'})")

        # Retrieve relevant chunks, scoped to the uploaded document if given
        search_results = retriever.search(query, top_k=5, doc_id=doc_id)
        logger.info(f"Retrieved {len(search_results)} chunks")
        
        if not search_results:
            logger.info("No relevant chunks found")
            return jsonify({
                'query': query,
                'answer': 'No relevant information found in documents.',
                'sources': []
            }), 200
        
        context_chunks = [r['text'] for r in search_results]
        
        # Get LLM response
        logger.info("Calling Claude API...")
        answer = chat_service.chat(query, context_chunks)
        logger.info("✅ Got response from Claude")
        
        return jsonify({
            'query': query,
            'answer': answer,
            'sources': search_results
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Chat failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("🚀 RAG Chatbot API starting...")
    logger.info("="*60)
    print("\n🚀 RAG Chatbot API running on http://localhost:5001\n")
    app.run(debug=config.DEBUG, port=config.PORT)