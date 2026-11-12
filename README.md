# AIライティングツール(個人用)

Python + Streamlit + Gemini API で作った、ライティング支援ツールです。DB・認証なし。

## 機能
- 📝 ブログ記事作成 / ✉️ メール返信 / 📄 要約
- ✨ 校正・リライト / 💡 タイトル・キャッチコピー案 / 📣 SNS投稿作成
- 🌏 翻訳 / 🗂️ 構成案・アイデア出し

## セットアップ
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # GEMINI_API_KEY を記入(https://aistudio.google.com/apikey)
streamlit run app.py
```

## 機能の追加方法
`features.py` の `FEATURES` に `Feature(...)` を1つ追加するだけで、サイドバーと入力フォームが自動で増えます。

## ファイル構成
- `app.py` … UI
- `features.py` … 各機能のプロンプト・入力項目の定義
- `gemini_client.py` … Gemini API呼び出し(ストリーミング)
