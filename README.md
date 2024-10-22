# Financial Transaction Assistant

## Overview
This project is an AI-powered tool designed to extract, categorize, and manage financial transactions from audio, text, or image inputs. It uses **Whisper** for audio transcription, **LlamaCpp** or **Ollama** for language processing, and FastAPI to create a server that handles requests for transaction extraction and management. The AI model classifies transactions into three categories: **Personal Expenses**, **Shared Expenses**, and **Debt**.

The system is capable of:
- Transcribing audio files and extracting transactions from them.
- Extracting text from images of receipts and identifying transactions.
- Processing text inputs and extracting transactions.
- Storing, updating, and deleting user transaction data.

## Features
- **Audio Transcription**: Transcribes audio files and extracts financial transaction details.
- **Receipt Parsing**: Extracts transaction details from images of receipts.
- **Text Processing**: Processes text inputs to extract transaction data.
- **Transaction Management**: Provides CRUD operations to manage stored transactions.
  
## Tools & Technologies
- **Whisper**: Used for audio transcription.
- **LlamaCpp**: Language model used for transaction extraction and categorization.
- **LangChain**: Manages tools and routes inputs to the appropriate processing pipeline.
- **FastAPI**: Provides a RESTful API interface for file uploads and transaction management.
- **Python**: Core language for development.
  
## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/financial-transaction-assistant.git
   cd financial-transaction-assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Environment Setup**:
   - Ensure you have the **Whisper model** downloaded for audio transcription (`small` version used in this example).
   - Set up the **LlamaCpp model** with the appropriate model path (in this case, `microsoft--Phi-3-mini-4k-instruct-gguf`).

## API Endpoints

### 1. **Status Check**
   - **Endpoint**: `/`
   - **Method**: `GET`
   - **Description**: Verifies if the server is running and logs the client's IP.
   - **Response**: JSON with server status.

### 2. **Text Input**
   - **Endpoint**: `/text`
   - **Method**: `POST`
   - **Description**: Upload text to extract transactions.
   - **Request Body**: 
     ```json
     {
       "text": "Transaction details...",
       "who": "username"
     }
     ```
   - **Response**: List of extracted transactions in JSON format.

### 3. **Audio Upload**
   - **Endpoint**: `/audio`
   - **Method**: `POST`
   - **Description**: Upload an audio file for transcription and transaction extraction.
   - **File Format**: `.mp3`, `.wav`, `.webm`, etc.
   - **Response**: List of extracted transactions.

### 4. **Image Upload**
   - **Endpoint**: `/image`
   - **Method**: `POST`
   - **Description**: Upload an image of a receipt to extract transactions.
   - **Response**: List of extracted transactions.

### 5. **View Transactions**
   - **Endpoint**: `/transactions/{who}`
   - **Method**: `GET`
   - **Description**: Fetch all transactions for a specific user.
   - **Response**: List of transactions for the user.

### 6. **Update Transaction**
   - **Endpoint**: `/transactions/{who}/{transaction_id}`
   - **Method**: `PUT`
   - **Description**: Update a specific transaction.
   - **Request Body**: 
     ```json
     {
       "Date": "new date",
       "Description": "new description",
       "Amount": new_amount,
       "Category": "new category"
     }
     ```
   - **Response**: Updated transaction.

### 7. **Delete Transaction**
   - **Endpoint**: `/transactions/{who}/{transaction_id}`
   - **Method**: `DELETE`
   - **Description**: Delete a specific transaction.
   - **Response**: Success or error message.

## Usage

1. **Transcription**: Upload audio or text to the API to extract transaction data. Audio files are transcribed using Whisper, and text files or images are parsed directly.
   
2. **Transaction Categorization**: The system uses the `LlamaCpp` model to identify and categorize transactions into **Personal Expenses**, **Shared Expenses**, and **Debt**.

3. **Data Management**: The API allows users to store, update, and delete transactions, making it useful for personal finance management.

## Running the Application

To run the application, use the following command:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Access the API documentation at `http://localhost:8000/docs`.

## Future Improvements
- **Async Transcription**: Implement asynchronous audio transcription.
- **Enhanced Error Handling**: Improve error handling for various file formats and incorrect inputs.
- **Multi-Language Support**: Extend the system to support transcription in multiple languages.

## License
This project is licensed under the MIT License.
