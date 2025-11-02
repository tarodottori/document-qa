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

# デバッグモードの追加
debug_mode = st.checkbox("デバッグモード", value=True)

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
        
        if debug_mode:
            st.write("### デバッグ情報")
            st.write(f"**ドキュメント長:** {len(document)} 文字")
            st.write(f"**質問:** {question}")
            with st.expander("ドキュメント内容（最初の500文字）"):
                st.text(document[:500])
        
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
        
        if debug_mode:
            st.write("**リクエストURL:**", f"{GEMINI_API_URL}?key=****")
            with st.expander("リクエストペイロード"):
                st.json(payload)
        
        # Generate an answer using the Gemini API.
        try:
            if debug_mode:
                st.write("**リクエスト送信中...**")
            
            with st.spinner("Generating answer..."):
                response = requests.post(
                    f"{GEMINI_API_URL}?key={gemini_api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=120
                )
            
            if debug_mode:
                st.write(f"**HTTPステータスコード:** {response.status_code}")
                st.write(f"**レスポンスヘッダー:** {dict(response.headers)}")
                with st.expander("生のレスポンステキスト（最初の1000文字）"):
                    st.code(response.text[:1000])
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    if debug_mode:
                        with st.expander("完全なレスポンスJSON"):
                            st.json(response_data)
                    
                    # Extract text from the response
                    full_response = ""
                    if 'candidates' in response_data:
                        if debug_mode:
                            st.write(f"**候補数:** {len(response_data['candidates'])}")
                        
                        for idx, candidate in enumerate(response_data['candidates']):
                            if debug_mode:
                                st.write(f"**候補 {idx}:**")
                                if 'finishReason' in candidate:
                                    st.write(f"  - finishReason: {candidate['finishReason']}")
                            
                            if 'content' in candidate:
                                parts = candidate['content'].get('parts', [])
                                if debug_mode:
                                    st.write(f"  - parts数: {len(parts)}")
                                
                                for part_idx, part in enumerate(parts):
                                    if 'text' in part:
                                        text_content = part['text']
                                        if debug_mode:
                                            st.write(f"  - part {part_idx} テキスト長: {len(text_content)}")
                                        full_response += text_content
                    else:
                        if debug_mode:
                            st.warning("レスポンスに 'candidates' キーがありません")
                    
                    if debug_mode:
                        st.write(f"**抽出されたテキスト長:** {len(full_response)}")
                        with st.expander("抽出されたテキスト全文"):
                            st.text(full_response)
                    
                    if full_response:
                        st.write("### 回答:")
                        st.write(full_response)
                    else:
                        st.warning("No response generated.")
                        
                except Exception as e:
                    st.error(f"レスポンス解析エラー: {str(e)}")
                    if debug_mode:
                        st.exception(e)
            else:
                error_message = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if debug_mode:
                        with st.expander("エラーレスポンス詳細"):
                            st.json(error_data)
                    if 'error' in error_data:
                        error_message = error_data['error'].get('message', error_message)
                except Exception as e:
                    if debug_mode:
                        st.write("エラーレスポンスのJSON解析に失敗:")
                        st.exception(e)
                
                st.error(error_message)
                
        except requests.exceptions.Timeout:
            st.error("リクエストがタイムアウトしました（120秒）")
        except requests.exceptions.RequestException as e:
            st.error(f"API通信エラー: {str(e)}")
            if debug_mode:
                st.exception(e)
