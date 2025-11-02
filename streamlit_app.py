import streamlit as st
import requests
from pypdf import PdfReader
from io import BytesIO

# Show title and description.
st.title("📄 インストラクショナルデザイン 教え方ヒント生成")
st.write(
    "インストラクショナルデザインに関する文書をアップロードし、教育シナリオを入力すると、Geminiが教え方のヒントを提供します。"
    "このアプリを使用するには、Gemini APIキーが必要です。[こちら](https://makersuite.google.com/app/apikey)から取得できます。"
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")

# デバッグモードの追加
debug_mode = st.checkbox("デバッグモード", value=True)

if not gemini_api_key:
    st.info("Gemini APIキーを入力してください。", icon="🗝️")
else:
    # Gemini API endpoint
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "インストラクショナルデザインに関する文書をアップロード (.txt, .md, .pdf)",
        type=("txt", "md", "pdf")
    )

    # 4つの入力欄
    st.subheader("教育シナリオの入力")

    input1 = st.text_area(
        "教える相手はどんな人ですか？",
        placeholder="例: 大学1年生、プログラミング初心者",
        disabled=not uploaded_file,
        help="対象者の年齢、経験レベル、背景などを記入してください"
    )

    input2 = st.text_area(
        "何を教えたいですか？",
        placeholder="例: Pythonの基本文法",
        disabled=not uploaded_file,
        help="教える内容やトピックを記入してください"
    )

    input3 = st.text_area(
        "それを教えた結果、どんなことを理解してもらったり、できるようになっていたりすることを期待しますか？",
        placeholder="例: 簡単なプログラムを自分で書けるようになる",
        disabled=not uploaded_file,
        help="期待する学習成果や到達目標を記入してください"
    )

    input4 = st.text_area(
        "相手について、その他の留意事項や補足情報を教えてください。（任意）",
        placeholder="例: オンライン授業を想定、週1回90分の授業",
        disabled=not uploaded_file,
        help="その他、考慮すべき情報があれば記入してください"
    )

    # バリデーション: 必須項目がすべて入力されているか
    can_submit = uploaded_file and input1.strip() and input2.strip() and input3.strip()

    # 実行ボタン
    submit_button = st.button(
        "教え方のヒントを表示させる",
        disabled=not can_submit,
        type="primary"
    )

    if submit_button:
        # ファイルの読み込みとテキスト抽出
        try:
            document = ""
            file_type = uploaded_file.name.split(".")[-1].lower()

            if file_type in ["txt", "md"]:
                # テキストファイルの処理
                document = uploaded_file.read().decode("utf-8")
            elif file_type == "pdf":
                # PDFファイルの処理
                pdf_bytes = BytesIO(uploaded_file.read())
                pdf_reader = PdfReader(pdf_bytes)

                # 全ページのテキストを抽出
                for page in pdf_reader.pages:
                    document += page.extract_text() + "\n"

            if debug_mode:
                st.write("### デバッグ情報")
                st.write(f"**ファイル形式:** {file_type}")
                st.write(f"**ドキュメント長:** {len(document)} 文字")
                with st.expander("ドキュメント内容（最初の500文字）"):
                    st.text(document[:500])
                st.write("**入力情報:**")
                st.write(f"- 対象者: {input1[:50]}...")
                st.write(f"- 教える内容: {input2[:50]}...")
                st.write(f"- 期待する成果: {input3[:50]}...")
                if input4.strip():
                    st.write(f"- その他留意事項: {input4[:50]}...")

            # プロンプトの構築
            prompt_parts = [
                "以下はインストラクショナルデザインに関する参考文書です。",
                "この文書に記載されている理論、原則、フレームワーク、手法を理解してください。\n",
                "【参考文書】",
                document,
                "\n---\n",
                "上記の参考文書に記載されているインストラクショナルデザインの考え方に基づいて、",
                "以下の教育シナリオに対する「教え方のヒント」を提供してください。\n",
                "【対象者】",
                input1,
                "\n【教える内容】",
                input2,
                "\n【期待する学習成果】",
                input3,
            ]

            # 任意項目が入力されている場合のみ追加
            if input4.strip():
                prompt_parts.extend([
                    "\n【その他の留意事項】",
                    input4,
                ])

            prompt_parts.extend([
                "\n---\n",
                "参考文書で解説されているインストラクショナルデザインの原則や手法を適用し、",
                "このシナリオに最適な教え方のヒントを、具体的かつ実践的に提示してください。"
            ])

            full_prompt = "\n".join(prompt_parts)

            # Prepare the request payload for Gemini API
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ]
            }

            if debug_mode:
                st.write("**リクエストURL:**", f"{GEMINI_API_URL}?key=****")
                with st.expander("構築されたプロンプト"):
                    st.text(full_prompt[:2000] + ("..." if len(full_prompt) > 2000 else ""))
                with st.expander("リクエストペイロード"):
                    st.json(payload)

            # Generate an answer using the Gemini API.
            try:
                if debug_mode:
                    st.write("**リクエスト送信中...**")

                with st.spinner("教え方のヒントを生成中..."):
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
                            st.write("### 教え方のヒント:")
                            st.write(full_response)
                        else:
                            st.warning("ヒントが生成されませんでした。")

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

        except Exception as e:
            st.error(f"ファイル処理エラー: {str(e)}")
            if debug_mode:
                st.exception(e)
