import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Mock TEI XML response with mathematical content
MOCK_TEI_RESPONSE = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" 
     xmlns:xlink="http://www.w3.org/1999/xlink" 
     xmlns:mml="http://www.w3.org/1998/Math/MathML">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Mock Academic Document</title>
            </titleStmt>
            <publicationStmt>
                <publisher>PDF2Audio Mock Service</publisher>
            </publicationStmt>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <div>
                <head>Introduction</head>
                <p>This is a mock academic document generated for testing the PDF2Audio system. 
                The document contains both regular text and mathematical expressions to verify 
                the complete processing pipeline.</p>
            </div>
            
            <div>
                <head>Mathematical Content</head>
                <p>Here are some mathematical expressions that should be converted to speech:</p>
                
                <p>Einstein's famous equation: 
                <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">
                    <mml:mi>E</mml:mi>
                    <mml:mo>=</mml:mo>
                    <mml:mi>m</mml:mi>
                    <mml:msup>
                        <mml:mi>c</mml:mi>
                        <mml:mn>2</mml:mn>
                    </mml:msup>
                </mml:math>
                </p>
                
                <p>A simple fraction: 
                <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">
                    <mml:mfrac>
                        <mml:mn>1</mml:mn>
                        <mml:mn>2</mml:mn>
                    </mml:mfrac>
                    <mml:mo>+</mml:mo>
                    <mml:mfrac>
                        <mml:mn>3</mml:mn>
                        <mml:mn>4</mml:mn>
                    </mml:mfrac>
                    <mml:mo>=</mml:mo>
                    <mml:mfrac>
                        <mml:mn>5</mml:mn>
                        <mml:mn>4</mml:mn>
                    </mml:mfrac>
                </mml:math>
                </p>
                
                <p>Square root example: 
                <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">
                    <mml:msqrt>
                        <mml:mn>16</mml:mn>
                    </mml:msqrt>
                    <mml:mo>=</mml:mo>
                    <mml:mn>4</mml:mn>
                </mml:math>
                </p>
                
                <p>An integral: 
                <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">
                    <mml:mo>∫</mml:mo>
                    <mml:mi>x</mml:mi>
                    <mml:mi>d</mml:mi>
                    <mml:mi>x</mml:mi>
                    <mml:mo>=</mml:mo>
                    <mml:mfrac>
                        <mml:msup>
                            <mml:mi>x</mml:mi>
                            <mml:mn>2</mml:mn>
                        </mml:msup>
                        <mml:mn>2</mml:mn>
                    </mml:mfrac>
                    <mml:mo>+</mml:mo>
                    <mml:mi>C</mml:mi>
                </mml:math>
                </p>
            </div>
            
            <div>
                <head>Conclusion</head>
                <p>This mock document demonstrates the capability of the PDF2Audio system 
                to handle academic content with mathematical expressions. The system should 
                extract this text and convert the mathematical notation into spoken form 
                using the MathJax Speech Rule Engine.</p>
                
                <p>The processing pipeline includes PDF parsing with GROBID, mathematical 
                expression processing, and text-to-speech synthesis with Piper TTS. 
                All components work together to provide accessible audio content for 
                researchers and students.</p>
            </div>
        </body>
    </text>
</TEI>'''

@app.route('/api/isalive', methods=['GET'])
def is_alive():
    """GROBID health check endpoint"""
    return jsonify(True)

@app.route('/api/processFulltextDocument', methods=['POST'])
def process_fulltext_document():
    """Mock GROBID PDF processing endpoint"""
    try:
        if 'input' not in request.files:
            return jsonify({'error': 'No input file provided'}), 400
        
        file = request.files['input']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        logger.info(f"Mock GROBID processing file: {file.filename}")
        
        # Simulate processing time
        time.sleep(3)
        
        # Return mock TEI XML
        return MOCK_TEI_RESPONSE, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        logger.error(f"Mock GROBID error: {e}")
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/api/processHeaderDocument', methods=['POST'])
def process_header_document():
    """Mock GROBID header processing endpoint"""
    return jsonify({'title': 'Mock Document', 'authors': ['Mock Author']})

@app.route('/api/processCitationList', methods=['POST'])
def process_citation_list():
    """Mock GROBID citation processing endpoint"""
    return jsonify({'citations': []})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'grobid-mock',
        'version': '0.8.0-mock'
    })

if __name__ == '__main__':
    logger.info("Starting GROBID Mock Service")
    app.run(host='0.0.0.0', port=8070, debug=True)