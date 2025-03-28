from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import tempfile
import platform
from PIL import Image
import pandas as pd
from flask_cors import CORS
from nbconvert import PDFExporter
import nbformat
import io
import subprocess

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

@app.route('/api/convert/ppt-to-pdf', methods=['POST'])
def ppt_to_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith(('.ppt', '.pptx')):
            return jsonify({'error': 'Invalid file format. Please upload a PPT/PPTX file.'}), 400

        input_path = os.path.join(TEMP_DIR, secure_filename(file.filename))
        output_path = os.path.join(TEMP_DIR, 'converted.pdf')
        file.save(input_path)

        try:
            # Convert using unoconv
            subprocess.run(['unoconv', '-f', 'pdf', '-o', output_path, input_path], check=True)
            
            if not os.path.exists(output_path):
                raise Exception("Conversion failed")

        except subprocess.CalledProcessError as conv_error:
            print(f"Conversion error: {conv_error}")
            return jsonify({'error': 'Failed to convert PPT to PDF. Please make sure unoconv and LibreOffice are installed.'}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Conversion failed'}), 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name='converted.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error in ppt_to_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cleanup_temp_files()

@app.route('/api/convert/ipynb-to-pdf', methods=['POST'])
def ipynb_to_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.ipynb'):
            return jsonify({'error': 'Invalid file format. Please upload an IPYNB file.'}), 400

        # Read the notebook
        notebook_content = nbformat.reads(file.read().decode('utf-8'), as_version=4)
        
        # Convert to PDF
        pdf_exporter = PDFExporter()
        pdf_data, resources = pdf_exporter.from_notebook_node(notebook_content)
        
        # Create response
        return send_file(
            io.BytesIO(pdf_data),
            as_attachment=True,
            download_name='converted.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error in ipynb_to_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/compress-image', methods=['POST'])
def compress_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return jsonify({'error': 'Invalid file format. Please upload a PNG or JPEG file.'}), 400

        # Open and compress image
        image = Image.open(file)
        output = io.BytesIO()
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
            
        # Save with compression
        image.save(output, format='JPEG', quality=60, optimize=True)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name='compressed_image.jpg',
            mimetype='image/jpeg'
        )

    except Exception as e:
        print(f"Error in compress_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/convert-image', methods=['POST'])
def convert_image():
    try:
        if 'file' not in request.files or 'format' not in request.form:
            return jsonify({'error': 'No file or format provided'}), 400
            
        file = request.files['file']
        target_format = request.form['format'].lower()
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if target_format not in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            return jsonify({'error': 'Invalid target format'}), 400

        # Open and convert image
        image = Image.open(file)
        output = io.BytesIO()
        
        # Convert to RGB if necessary (except for PNG which can handle RGBA)
        if target_format != 'png' and image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
            
        # Save in new format
        image.save(output, format=target_format.upper())
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f'converted_image.{target_format}',
            mimetype=f'image/{target_format}'
        )

    except Exception as e:
        print(f"Error in convert_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 