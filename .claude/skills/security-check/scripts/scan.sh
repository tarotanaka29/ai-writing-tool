#!/usr/bin/env bash
# 簡易セキュリティスキャン(読み取り専用)。プロジェクトルートで実行する。
# 出力は手がかり。ヒットは該当行を読んで本物か判断すること。
# 注意: キーの実値は出力しない(行番号とファイル名のみ表示)。

cd "${1:-.}" || exit 1
SRC=(--include='*.py' --include='*.md' --include='*.toml' --include='*.txt' --include='*.json' --include='*.example'
     --exclude-dir=.venv --exclude-dir=__pycache__ --exclude-dir=.git --exclude-dir=skills --exclude-dir=.claude --exclude-dir=.agents)

echo "== 1. APIキー/シークレット風の文字列(値は伏せて表示) =="
grep -rnE "${SRC[@]}" 'AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9]{20,}|(api[_-]?key|secret|token|password)[[:space:]]*[=:][[:space:]]*["'"'"'][^"'"'"']{8,}' . \
  | sed -E 's/(:[0-9]+:).*/\1 <伏せ字: 要確認>/' || true
echo

echo "== 2. .env の扱い =="
if [ -f .env ]; then
  echo ".env: 存在する"
  git check-ignore -q .env 2>/dev/null && echo ".env: git で無視される (OK)" || echo ".env: git で無視されていない or git 管理外 → 要確認"
  git ls-files --error-unmatch .env >/dev/null 2>&1 && echo "!! .env が git に追跡されている(重大)" || echo ".env: 追跡されていない (OK)"
  perm=$(stat -f '%Lp' .env 2>/dev/null || stat -c '%a' .env 2>/dev/null)
  echo ".env パーミッション: $perm (600 推奨)"
else
  echo ".env: なし"
fi
echo "-- .env.example の中身が実キーでないか(キー名のみ表示)"
[ -f .env.example ] && sed -E 's/=.*/=<値は伏せ>/' .env.example
echo "-- git 履歴に AIza 形式のキーが入っていないか"
n=$(git log -p --all -S'AIza' --oneline -- . 2>/dev/null | grep -cE 'AIza[0-9A-Za-z_-]{20,}')
echo "該当行数: ${n:-0}"
echo

echo "== 3. 危険な API の使用箇所 =="
grep -rnE "${SRC[@]}" 'unsafe_allow_html|components\.v1|eval\(|exec\(|subprocess|os\.system|pickle|yaml\.load\(|shell=True|verify=False' . || echo "(なし)"
echo

echo "== 4. Streamlit 設定 =="
for f in .streamlit/config.toml ~/.streamlit/config.toml; do
  [ -f "$f" ] && { echo "-- $f"; grep -nE 'address|enableCORS|enableXsrfProtection|headless|port' "$f" || echo "(関連設定なし)"; }
done
echo

echo "== 5. 依存関係の固定状況 =="
if [ -f requirements.txt ]; then
  grep -vE '^\s*(#|$)' requirements.txt | while read -r l; do
    case "$l" in *==*) echo "固定: $l";; *) echo "未固定: $l";; esac
  done
fi
for t in pip-audit bandit; do
  if [ -x .venv/bin/$t ] || command -v $t >/dev/null 2>&1; then echo "$t: 利用可"; else echo "$t: 未インストール(未実施として報告)"; fi
done
