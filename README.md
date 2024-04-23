### README for EduTask ChatGPT

#### Project Overview

EduTask is designed to process and analyze educational syllabi by leveraging the power of a vector database integrated with a large language model. This application helps in extracting, cleaning, and transforming PDF documents into a format suitable for enhanced querying and retrieval. The end goal is to utilize the preprocessed data in a Retrieval Augmented Generation (RAG) system to provide contextual support to the language model and generate tasks out of syllabus.

#### Prerequisites

Before you begin, make sure you have the following:

1. Python installed on your machine.
2. Basic knowledge of command line operations.
3. Access to Unstructured API. Obtain an API key from [[Unstructured API Key portal](https://unstructured.io/blog/how-to-build-an-end-to-end-rag-pipeline-with-unstructured-s-api)](#).

#### Installation

1. **Install the Unstructured library**:
   You can install the library from PyPI or the GitHub repository.
   ```bash
   pip install unstructured
   ```

2. **Clone the project repository**:
   Clone or download the repository to your local machine.
   ```bash
   git clone <repository_url>
   cd EduTask
   ```



#### Configuration

Configure your environment and project settings:
1. **Set up the API Key in `Utils.py`**:
   Open `Utils.py` and implement the logic to retrieve the Unstructured API key. Replace the placeholder method with your actual API key retrieval logic.
   ```python
   class Utils:
       def get_dlai_api_key(self):
           # Return your Unstructured API key here
           return "your_unstructured_api_key_here"
   ```

#### Usage

Follow these steps to run the application:

1. **Start the application**:
   Run the application using Python. This will start a local server.
   ```bash
   python app.py
   ```

2. **Access the application**:
   Open a web browser and navigate to `http://localhost:5000/` to access the EduTask interface.

3. **Upload Files**:
   Use the web interface to upload your syllabus files in PDF, DOC, or DOCX format. The system will process these files and display the extracted tasks.

4. **View Results**:
   After processing, the application will display the list of tasks extracted from your syllabus.

#### Additional Information

- The application uses Flask for the backend and Bootstrap for the frontend.
- It is equipped to handle multiple file uploads and the interface includes dynamic messaging to inform the user about the processing status.

#### Troubleshooting

If you encounter issues:
- Ensure that your API key is valid and active.
- Check if the Unstructured library is correctly installed and updated.
- Verify that your files are in the supported formats and not corrupted.

#### Support

For more help or to report issues, please reach out to the support team via the repository's issues section or contact support through the project's website.

---

This README provides a comprehensive guide to setting up and using EduTask for processing educational syllabi with advanced AI capabilities. Adjust any sections as necessary to match your specific project setup or additional configurations.
