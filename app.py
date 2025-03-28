from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import tempfile
import platform
from PIL import Image
import pandas as pd
from flask_cors import CORS

# Create a persistent temporary directory
TEMP_DIR = os.path.join(os.getcwd(), 'temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Import converters with error handling
try:
    from docx2pdf import convert as docx2pdf_convert
except ImportError:
    docx2pdf_convert = None
    print("Warning: docx2pdf not available. DOCX to PDF conversion will be disabled.")

try:
    from pdf2docx import Converter
except ImportError:
    Converter = None
    print("Warning: pdf2docx not available. PDF to DOCX conversion will be disabled.")

def cleanup_temp_files():
    """Clean up temporary files after processing"""
    for f in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, f))
        except Exception as e:
            print(f"Error cleaning up file {f}: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Add root route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert/docx-to-pdf', methods=['POST'])
def docx_to_pdf():
    try:
        if docx2pdf_convert is None:
            return jsonify({'error': 'DOCX to PDF conversion is only supported on Windows'}), 400

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.docx'):
            return jsonify({'error': 'Invalid file format. Please upload a DOCX file.'}), 400

        # Save uploaded file
        input_path = os.path.join(TEMP_DIR, secure_filename(file.filename))
        output_path = os.path.join(TEMP_DIR, 'converted.pdf')
        file.save(input_path)

        try:
            # Convert DOCX to PDF
            docx2pdf_convert(input_path, output_path)
        except Exception as conv_error:
            print(f"Conversion error: {conv_error}")
            return jsonify({'error': 'Failed to convert DOCX to PDF. Please make sure Microsoft Word is installed.'}), 500

        # Send the converted file
        return send_file(
            output_path,
            as_attachment=True,
            download_name='converted.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error in docx_to_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cleanup_temp_files()

@app.route('/api/convert/pdf-to-docx', methods=['POST'])
def pdf_to_docx():
    try:
        if Converter is None:
            return jsonify({'error': 'PDF to DOCX conversion is not available. Please install pdf2docx.'}), 400

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Invalid file format. Please upload a PDF file.'}), 400

        input_path = os.path.join(TEMP_DIR, secure_filename(file.filename))
        output_path = os.path.join(TEMP_DIR, 'converted.docx')
        file.save(input_path)

        # Convert PDF to DOCX using Converter class
        try:
            cv = Converter(input_path)
            cv.convert(output_path)
            cv.close()
        except Exception as conv_error:
            print(f"Conversion error: {conv_error}")
            return jsonify({'error': 'Failed to convert PDF to DOCX'}), 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name='converted.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        print(f"Error in pdf_to_docx: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cleanup_temp_files()

@app.route('/api/convert/images-to-pdf', methods=['POST'])
def images_to_pdf():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400

        images = []
        for file in files:
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                return jsonify({'error': 'Invalid file format. Please upload image files.'}), 400
            
            input_path = os.path.join(TEMP_DIR, secure_filename(file.filename))
            file.save(input_path)
            images.append(Image.open(input_path).convert('RGB'))

        # Convert images to PDF
        output_path = os.path.join(TEMP_DIR, 'converted.pdf')
        images[0].save(output_path, save_all=True, append_images=images[1:])

        return send_file(
            output_path,
            as_attachment=True,
            download_name='converted.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error in images_to_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cleanup_temp_files()

@app.route('/api/convert/csv-to-excel', methods=['POST'])
def csv_to_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

        input_path = os.path.join(TEMP_DIR, secure_filename(file.filename))
        output_path = os.path.join(TEMP_DIR, 'converted.xlsx')
        file.save(input_path)

        # Convert CSV to Excel
        df = pd.read_csv(input_path)
        df.to_excel(output_path, index=False, engine='openpyxl')

        return send_file(
            output_path,
            as_attachment=True,
            download_name='converted.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error in csv_to_excel: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cleanup_temp_files()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 