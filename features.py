"""AIライティング機能の定義。

新しい機能を足したいときは、FEATURES に Feature を1つ追加するだけでOKです。
UI(app.py)はこの定義から入力フォームを自動生成します。
"""

from dataclasses import dataclass, field


@dataclass
class Field:
    key: str
    label: str
    kind: str = "text"  # text | textarea | select | slider
    placeholder: str = ""
    options: list[str] = field(default_factory=list)
    default: object = None
    required: bool = False
    min_value: int = 0
    max_value: int = 0
    step: int = 1


@dataclass
class Feature:
    id: str
    icon: str
    name: str
    description: str
    system: str
    template: str  # {key} 形式で入力値を差し込む
    fields: list[Field]


TONES = ["標準", "丁寧", "フレンドリー", "フォーマル", "カジュアル", "情熱的", "クール・簡潔"]

COMMON_SYSTEM = (
    "あなたは優秀な日本語ライターです。指示された形式だけを出力し、"
    "前置きや『承知しました』のような返答は書かないでください。"
    "Markdown形式で読みやすく出力してください。"
)

FEATURES: list[Feature] = [
    Feature(
        id="blog",
        icon="📝",
        name="ブログ記事作成",
        description="テーマとキーワードから、構成付きのブログ記事を書きます。",
        system=COMMON_SYSTEM + "SEOを意識し、読者にとって有益で独自性のある記事を書きます。",
        template=(
            "以下の条件でブログ記事を執筆してください。\n\n"
            "# 条件\n- テーマ: {topic}\n- 想定読者: {audience}\n- キーワード: {keywords}\n"
            "- 文体: {tone}\n- 目標文字数: 約{length}文字\n- 補足: {notes}\n\n"
            "# 出力形式\n"
            "タイトル(H1)、導入文、H2見出し3〜6個とそれぞれの本文、まとめの順で書いてください。"
            "キーワードは不自然にならない範囲で盛り込んでください。"
        ),
        fields=[
            Field("topic", "テーマ", "text", "例: 在宅ワークの集中力を上げる方法", required=True),
            Field("audience", "想定読者", "text", "例: 在宅勤務3年目の会社員", default="一般読者"),
            Field("keywords", "キーワード(カンマ区切り)", "text", "例: 在宅ワーク, 集中力, 習慣"),
            Field("tone", "文体", "select", options=TONES, default="標準"),
            Field("length", "目標文字数", "slider", min_value=500, max_value=5000, step=100, default=2000),
            Field("notes", "補足・盛り込みたい内容", "textarea", "任意"),
        ],
    ),
    Feature(
        id="email_reply",
        icon="✉️",
        name="メール返信",
        description="受信メールを貼り付けて、返信したい内容を伝えると返信文を作成します。",
        system=COMMON_SYSTEM + "ビジネスメールの作法に沿い、そのまま送れる返信文を作ります。",
        template=(
            "以下の受信メールへの返信文を作成してください。\n\n"
            "# 受信メール\n{received}\n\n"
            "# 返信で伝えたい内容\n{intent}\n\n"
            "# 条件\n- トーン: {tone}\n- 長さ: {length}\n- 署名名義: {sender}\n\n"
            "# 出力形式\n件名(Re:)、本文の順で出力してください。署名名義が空なら署名は省略します。"
        ),
        fields=[
            Field("received", "受信メール", "textarea", "返信したいメールを貼り付け", required=True),
            Field("intent", "返信で伝えたい内容", "textarea", "例: 日程は来週火曜午後なら可能。資料は明日送る。", required=True),
            Field("tone", "トーン", "select", options=TONES, default="丁寧"),
            Field("length", "長さ", "select", options=["短め", "標準", "詳しめ"], default="標準"),
            Field("sender", "署名名義", "text", "例: 田中"),
        ],
    ),
    Feature(
        id="summarize",
        icon="📄",
        name="要約",
        description="長い文章を、目的に合わせた形式で要約します。",
        system=COMMON_SYSTEM + "原文にない情報は絶対に追加せず、事実を正確に要約します。",
        template=(
            "以下の文章を要約してください。\n\n"
            "# 要約の条件\n- 形式: {style}\n- 長さの目安: {length}\n\n"
            "# 原文\n{text}"
        ),
        fields=[
            Field("text", "要約したい文章", "textarea", "ここに文章を貼り付け", required=True),
            Field("style", "形式", "select", options=["箇条書き", "1段落の文章", "3行要約", "要点+結論", "議事録形式(決定事項/ToDo)"], default="箇条書き"),
            Field("length", "長さの目安", "select", options=["極短(1〜2文)", "短め", "標準", "詳しめ"], default="標準"),
        ],
    ),
    Feature(
        id="rewrite",
        icon="✨",
        name="校正・リライト",
        description="誤字脱字の修正や、読みやすい文章への書き換え、文体の変換を行います。",
        system=COMMON_SYSTEM,
        template=(
            "以下の文章を「{mode}」してください。\n\n"
            "# 条件\n- 目指すトーン: {tone}\n- 意味や事実は変えないこと\n\n"
            "# 出力形式\n1. 修正後の文章\n2. 主な変更点(箇条書き、3〜6個)\n\n"
            "# 原文\n{text}"
        ),
        fields=[
            Field("text", "元の文章", "textarea", "ここに文章を貼り付け", required=True),
            Field(
                "mode", "モード", "select",
                options=["校正(誤字脱字・文法の修正のみ)", "読みやすくリライト", "より簡潔に短縮", "より詳しく膨らませる", "文体・トーンを変換"],
                default="読みやすくリライト",
            ),
            Field("tone", "トーン", "select", options=TONES, default="標準"),
        ],
    ),
    Feature(
        id="titles",
        icon="💡",
        name="タイトル・キャッチコピー案",
        description="記事タイトルや広告コピーの案をまとめて出します。",
        system=COMMON_SYSTEM + "切り口の異なる案を出し、ありきたりな表現は避けます。",
        template=(
            "以下の内容に対する「{kind}」を{count}案作成してください。\n\n"
            "# 内容\n{content}\n\n"
            "# 条件\n- トーン: {tone}\n- 各案に、狙い(切り口)を一言添えてください。\n"
            "- 番号付きリストで出力してください。"
        ),
        fields=[
            Field("content", "内容・商品の説明", "textarea", "何についてのタイトル/コピーか", required=True),
            Field("kind", "種類", "select", options=["ブログ記事タイトル", "キャッチコピー", "メールの件名", "動画タイトル", "見出し"], default="ブログ記事タイトル"),
            Field("count", "案の数", "slider", min_value=3, max_value=20, default=10),
            Field("tone", "トーン", "select", options=TONES, default="標準"),
        ],
    ),
    Feature(
        id="sns",
        icon="📣",
        name="SNS投稿作成",
        description="X・Instagram・LinkedInなど媒体に合わせた投稿文を作ります。",
        system=COMMON_SYSTEM + "各媒体の文化と文字数制限に合った投稿を作ります。",
        template=(
            "以下の内容で、{platform}向けの投稿文を{count}パターン作成してください。\n\n"
            "# 内容\n{content}\n\n"
            "# 条件\n- トーン: {tone}\n- ハッシュタグ: {hashtag}\n"
            "- 媒体の特性(文字数・改行・絵文字の使い方)に合わせること\n"
            "- パターンごとに区切り線(---)で分けること"
        ),
        fields=[
            Field("content", "投稿したい内容", "textarea", "伝えたいこと・告知内容", required=True),
            Field("platform", "媒体", "select", options=["X(Twitter)", "Instagram", "LinkedIn", "Facebook", "Threads"], default="X(Twitter)"),
            Field("tone", "トーン", "select", options=TONES, default="フレンドリー"),
            Field("hashtag", "ハッシュタグ", "select", options=["付ける(3〜5個)", "付けない"], default="付ける(3〜5個)"),
            Field("count", "パターン数", "slider", min_value=1, max_value=5, default=3),
        ],
    ),
    Feature(
        id="translate",
        icon="🌏",
        name="翻訳",
        description="自然な表現で翻訳します。ニュアンスの指定も可能です。",
        system=COMMON_SYSTEM + "直訳ではなく、読み手にとって自然な表現を選びます。",
        template=(
            "以下の文章を{target}に翻訳してください。\n\n"
            "# 条件\n- 用途・ニュアンス: {nuance}\n- 翻訳文のみを出力すること(解説は不要)\n\n"
            "# 原文\n{text}"
        ),
        fields=[
            Field("text", "翻訳したい文章", "textarea", "ここに文章を貼り付け", required=True),
            Field("target", "翻訳先", "select", options=["日本語", "英語", "中国語(簡体字)", "中国語(繁体字)", "韓国語", "フランス語", "スペイン語"], default="英語"),
            Field("nuance", "用途・ニュアンス", "select", options=["標準", "ビジネス", "カジュアル", "技術文書", "マーケティング"], default="標準"),
        ],
    ),
    Feature(
        id="outline",
        icon="🗂️",
        name="構成案・アイデア出し",
        description="記事や資料の構成案を作成、またはネタ出しを行います。",
        system=COMMON_SYSTEM,
        template=(
            "以下のテーマで「{kind}」を作成してください。\n\n"
            "# テーマ\n{topic}\n\n"
            "# 条件\n- 想定読者・対象: {audience}\n"
            "- 構成案の場合は、見出し階層(H2/H3)と各見出しで書く内容を一行ずつ添えること\n"
            "- アイデア出しの場合は、10個以上、切り口を変えて出すこと"
        ),
        fields=[
            Field("topic", "テーマ", "text", "例: 副業で月5万円稼ぐ", required=True),
            Field("kind", "種類", "select", options=["記事の構成案", "ブログネタ出し", "プレゼン資料の構成案", "動画台本の構成案"], default="記事の構成案"),
            Field("audience", "想定読者・対象", "text", "例: 20代会社員", default="一般読者"),
        ],
    ),
]

FEATURE_MAP = {f.id: f for f in FEATURES}


def build_prompt(feature: Feature, values: dict) -> str:
    """入力値をテンプレートに差し込む。未入力は『指定なし』にする。"""
    filled = {k: (str(v).strip() if str(v).strip() else "指定なし") for k, v in values.items()}
    return feature.template.format(**filled)
