# Easy Hand 🛠️

Your all-in-one solution for everyday digital tasks. Easy Hand is a web-based tool that provides various file conversion and utility tools to make your digital life easier.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/fahim)

## 🌟 Features

### File Conversion Tools

- DOCX to PDF conversion
- PDF to DOCX conversion
- PPT/PPTX to PDF conversion
- Jupyter Notebook (IPYNB) to PDF
- Multiple Images to PDF
- CSV to Excel conversion

### Image & Media Processing

- Image Compression
- Image Format Conversion (PNG, JPG, GIF, BMP)

### Text Tools

- Text Case Converter
- Character Counter

### Programming Tools

- JSON Formatter
- Base64 Encoder/Decoder

## 🚀 Getting Started

### Prerequisites

#### For Ubuntu/Linux:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip libreoffice unoconv

# Start unoconv listener (required for PPT conversion)
unoconv --listener &
```

#### For Windows:

- Install Python 3.8 or higher
- Install Microsoft Office (for DOCX and PPT conversions)

### Installation

1. Clone the repository

```bash
git clone https://github.com/fahimmuntashir/easy-hand.git
cd easy-hand
```

2. Create and activate virtual environment

```bash
# For Ubuntu/Linux:
python3 -m venv venv
source venv/bin/activate

# For Windows:
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
python app.py
```

5. Open your browser and navigate to:



## 📁 Project Structure

```

easy-hand/
├── app.py
├── requirements.txt 
├── templates/  
│ └── index.html
├── static/
│ └── css/
│ └── style.css
└── temp/ 

````

## 🤝 Contributing

Welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful commit messages
- Add comments for complex functionality
- Update documentation for new features

## 📝 To-Do

- [ ] Add more file conversion options
- [ ] Implement batch processing
- [ ] Add user authentication
- [ ] Create API documentation
- [ ] Add more image processing tools
- [ ] Implement file size limits
- [ ] Add progress indicators for conversions

## ⚠️ Known Issues

- PPT to PDF conversion requires LibreOffice on Linux systems
- DOCX to PDF conversion requires Microsoft Word on Windows systems
- Large file conversions might take longer

## 🔒 Security

- Temporary files are automatically cleaned up
- File extensions are validated
- CORS is enabled for local development

## 💡 Support the Project

If you find this tool helpful, consider:

- Starring the repository
- Sharing with others
- [Buying me a coffee](https://buymeacoffee.com/fahim) ☕

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask framework
- Various Python libraries used in the project
- All contributors and supporters

## 📬 Contact

For questions, suggestions, or issues:

- Create an issue in the repository

---

