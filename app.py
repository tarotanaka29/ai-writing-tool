"""AIライティングツール(個人用) - Streamlit + Gemini API"""

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from features import FEATURES, FEATURE_MAP, Field, build_prompt
from gemini_client import DEFAULT_MODEL, MODELS, stream_text

load_dotenv()

st.set_page_config(page_title="AIライティングツール", page_icon="✍️", layout="wide")

# ---------- セッション状態 ----------
st.session_state.setdefault("history", [])  # 今回の起動中だけ保持(DBなし)
st.session_state.setdefault("result", {})  # 機能ごとの最新結果


# ---------- サイドバー ----------
with st.sidebar:
    st.title("✍️ AIライティング")

    labels = {f.id: f"{f.icon} {f.name}" for f in FEATURES}
    feature_id = st.radio(
        "機能を選択", list(labels), format_func=labels.get, label_visibility="collapsed"
    )

    st.divider()
    st.subheader("⚙️ 設定")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Gemini APIキー",
        value="",
        type="password",
        placeholder="設定済み(.env)" if env_key else "AIza...",
        help=".env に GEMINI_API_KEY を書いておけば入力不要です。",
    ) or env_key
    model = st.selectbox("モデル", MODELS, index=MODELS.index(DEFAULT_MODEL))
    temperature = st.slider("創造性(temperature)", 0.0, 2.0, 0.8, 0.1)


# ---------- 入力フォーム ----------
feature = FEATURE_MAP[feature_id]
st.header(f"{feature.icon} {feature.name}")
st.caption(feature.description)


def render_field(f: Field):
    key = f"{feature.id}_{f.key}"
    if f.kind == "textarea":
        return st.text_area(f.label, placeholder=f.placeholder, height=160, key=key)
    if f.kind == "select":
        idx = f.options.index(f.default) if f.default in f.options else 0
        return st.selectbox(f.label, f.options, index=idx, key=key)
    if f.kind == "slider":
        return st.slider(f.label, f.min_value, f.max_value, f.default, f.step, key=key)
    return st.text_input(f.label, value=f.default or "", placeholder=f.placeholder, key=key)


col_in, col_out = st.columns(2, gap="large")

with col_in:
    st.subheader("入力")
    values = {f.key: render_field(f) for f in feature.fields}
    run = st.button("✨ 生成する", type="primary", use_container_width=True)

with col_out:
    st.subheader("出力")
    out_area = st.container()

    if run:
        missing = [f.label for f in feature.fields if f.required and not str(values[f.key]).strip()]
        if not api_key:
            st.error("Gemini APIキーが未設定です。サイドバーに入力するか .env に設定してください。")
        elif missing:
            st.warning("必須項目を入力してください: " + "、".join(missing))
        else:
            prompt = build_prompt(feature, values)
            try:
                with out_area:
                    text = st.write_stream(
                        stream_text(api_key, model, feature.system, prompt, temperature)
                    )
                st.session_state.result[feature.id] = text
                st.session_state.history.insert(
                    0,
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "feature": f"{feature.icon} {feature.name}",
                        "text": text,
                    },
                )
            except Exception as e:  # APIキー誤り・レート制限・通信エラーなど
                st.error(f"生成に失敗しました: {e}")
    elif feature.id in st.session_state.result:
        with out_area:
            st.markdown(st.session_state.result[feature.id])

    current = st.session_state.result.get(feature.id)
    if current:
        with st.expander("📋 コピー用テキスト", expanded=False):
            st.code(current, language="markdown", wrap_lines=True)
        st.download_button(
            "💾 .mdでダウンロード",
            current,
            file_name=f"{feature.id}_{datetime.now():%Y%m%d_%H%M%S}.md",
            mime="text/markdown",
        )
        if len(current):
            st.caption(f"文字数: {len(current):,}")

# ---------- 履歴 ----------
if st.session_state.history:
    st.divider()
    with st.expander(f"🕘 今回の生成履歴 ({len(st.session_state.history)}件)"):
        for item in st.session_state.history[:20]:
            st.markdown(f"**{item['time']} / {item['feature']}**")
            st.code(item["text"], language="markdown", wrap_lines=True)
