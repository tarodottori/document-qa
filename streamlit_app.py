import streamlit as st
import requests

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide a Gemini API key, which you can get [here](https://makersuite.google.com/app/apikey). "
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Gemini API endpoint
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
    
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )
    
    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )
    
    if uploaded_file and question:
        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        
        # Prepare the request payload for Gemini API
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"Here's a document: {document} \n\n---\n\n {question}"
                        }
                    ]
                }
            ]
        }
        
        # Generate an answer using the Gemini API.
        try:
            with st.spinner("Generating answer..."):
                response = requests.post(
                    f"{GEMINI_API_URL}?key={gemini_api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=120
                )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract text from the response
                full_response = ""
                if 'candidates' in response_data:
                    for candidate in response_data['candidates']:
                        if 'content' in candidate:
                            for part in candidate['content'].get('parts', []):
                                if 'text' in part:
                                    full_response += part['text']
                
                if full_response:
                    st.write(full_response)
                else:
                    st.warning("No response generated.")
            else:
                error_message = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_message = error_data['error'].get('message', error_message)
                except:
                    pass
                st.error(error_message)
                
        except requests.exceptions.RequestException as e:
            st.error(f"API communication error: {str(e)}")
