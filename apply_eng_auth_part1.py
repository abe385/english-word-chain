# -*- coding: utf-8 -*-
"""
english-word-chain.html に、ログイン・課金機能を組み込むスクリプト(パート1: CSS+HTML)。

使い方:
    python apply_eng_auth_part1.py <対象フォルダ>

例:
    python apply_eng_auth_part1.py C:\\word-chain-worker\\english-word-chain
"""
import sys
import shutil
import datetime
import os

if len(sys.argv) < 2:
    print("エラー: 対象フォルダを指定してください")
    sys.exit(1)

TARGET_DIR = sys.argv[1]
HTML_PATH = os.path.join(TARGET_DIR, "english-word-chain.html")

if not os.path.exists(HTML_PATH):
    print(f"エラー: {HTML_PATH} が見つかりません")
    sys.exit(1)

with open(HTML_PATH, "r", encoding="utf-8") as f:
    content = f.read()

if "loginOverlay" in content:
    print("すでにログイン機能が追加済みのようです。二重適用防止のため中止します。")
    sys.exit(0)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(TARGET_DIR, f"english-word-chain.html.backup_{timestamp}")
shutil.copy(HTML_PATH, backup_path)
print(f"バックアップを作成しました: {backup_path}")


def replace_once(content, find, replace, label):
    if find not in content:
        print(f"エラー: 置換対象が見つかりませんでした ({label})")
        sys.exit(1)
    print(f"{label}: OK")
    return content.replace(find, replace, 1)


# ---- ① CSSを追加(.closeBtn定義の直後に挿入) ----
find1 = """  .closeBtn{
    margin-top:8px; background:none; border:1px solid var(--indigo); color:var(--indigo);
    border-radius:10px; padding:10px; width:100%; font-weight:700; cursor:pointer;
    font-family:'Zen Kaku Gothic New', sans-serif;
  }"""

replace1 = find1 + """

  /* ==================== ログイン・課金UI ==================== */
  .card input{
    width:100%; padding:14px; border-radius:10px; border:1.5px solid var(--paper-dim);
    font-size:17px; margin-bottom:10px; background:#fff; font-family:'Zen Kaku Gothic New', sans-serif;
  }
  .authError{ color:var(--danger); font-size:14px; font-weight:700; min-height:18px; margin-bottom:8px; text-align:left; }
  .linkBtn{
    background:none; border:none; color:var(--indigo); font-size:14px; font-weight:700;
    text-decoration:underline; cursor:pointer; padding:0; font-family:inherit;
  }
  .accountBar{
    font-size:13px; color:var(--paper); display:flex; flex-direction:column; gap:8px;
    align-items:center; margin-top:8px; padding:8px 10px; background:rgba(255,255,255,0.08); border-radius:10px;
  }
  .upgradeBigBtn{
    background:var(--gold); color:#2b2b22; font-weight:900; font-size:16px;
    border:none; border-radius:12px; padding:12px 26px; cursor:pointer;
  }
  .smallLogout{
    font-size:12px; color:#c9d2e8; font-weight:500; background:none; border:none;
    text-decoration:underline; cursor:pointer; font-family:inherit;
  }
  .authTabs{
    display:flex; gap:8px; margin-bottom:16px; background:var(--paper-dim);
    border-radius:12px; padding:4px;
  }
  .authTabs button{
    flex:1; padding:11px 8px; border:none; border-radius:9px; font-size:14px;
    font-weight:700; cursor:pointer; background:none; color:#4a4a3f; font-family:inherit;
  }
  .authTabs button.activeTab{
    background:var(--accent); color:#fff;
  }"""

content = replace_once(content, find1, replace1, "① CSSの追加")

# ---- ② HTML: アカウントバーをヘッダーに追加 ----
find2 = '<div class="sub">一人で挑戦。答えたら即判定、わからない単語は意味も調べられます。</div>'
replace2 = find2 + '\n    <div class="accountBar" id="accountBar"></div>'
content = replace_once(content, find2, replace2, "② アカウントバーの追加")

# ---- ③ HTML: ログイン・パスワード再設定モーダルを追加(upgradeOverlayの直前) ----
find3 = '<div class="overlay" id="upgradeOverlay" style="display:none;">'
replace3 = """<div class="overlay" id="loginOverlay" style="display:none;">
  <div class="card">
    <div class="authTabs">
      <button id="tabSignup" class="activeTab">🆕 はじめての方</button>
      <button id="tabLogin">🔑 2回目以降の方(ログイン)</button>
    </div>
    <h2 id="authTitle">はじめまして</h2>
    <p id="authDesc">メールアドレスと、お好きなパスワード(8文字以上)を決めるだけで始められます。メール認証は不要です。登録すると5日間無料でお試しいただけます。</p>
    <div class="authError" id="authError"></div>
    <input type="email" id="authEmail" placeholder="メールアドレス" autocomplete="email">
    <input type="password" id="authPassword" placeholder="パスワード(8文字以上)" autocomplete="new-password">
    <input type="password" id="authPasswordConfirm" placeholder="パスワード(確認用・もう一度入力)" autocomplete="new-password">
    <button class="primary" id="authSubmitBtn">無料で始める</button>
    <div style="text-align:center; margin-top:10px; display:none;" id="forgotPasswordWrap">
      <button class="linkBtn" id="forgotPasswordLink">パスワードを忘れた方はこちら</button>
    </div>
  </div>
</div>

<div class="overlay" id="forgotOverlay" style="display:none;">
  <div class="card">
    <h2>🔑 パスワード再設定</h2>
    <p>登録済みのメールアドレスを入力してください。再設定用のリンクをメールでお送りします。</p>
    <div class="authError" id="forgotError"></div>
    <input type="email" id="forgotEmail" placeholder="メールアドレス" autocomplete="email">
    <button class="primary" id="forgotSubmitBtn">再設定メールを送る</button>
    <button class="closeBtn" id="forgotBackBtn">ログイン画面に戻る</button>
  </div>
</div>

<div class="overlay" id="resetOverlay" style="display:none;">
  <div class="card">
    <h2>🔑 新しいパスワードを設定</h2>
    <p>新しいパスワード(8文字以上)を入力してください。</p>
    <div class="authError" id="resetError"></div>
    <input type="password" id="resetPassword" placeholder="新しいパスワード(8文字以上)" autocomplete="new-password">
    <input type="password" id="resetPasswordConfirm" placeholder="新しいパスワード(確認用)" autocomplete="new-password">
    <button class="primary" id="resetSubmitBtn">パスワードを更新する</button>
  </div>
</div>

<div class="overlay" id="upgradeOverlay" style="display:none;">"""
content = replace_once(content, find3, replace3, "③ ログイン・再設定モーダルの追加")

# ---- ④ HTML: 決済確認画面(法対応リンク・年齢確認)をupgradeOverlay内に追加 ----
find4 = """    <p id="upgradeBody">無料版はここまでです。プレミアムにアップグレードすると、ラウンド数・辞書検索回数が無制限になります。</p>
    <button class="primary" id="fakeBuyBtn">アップグレードする(デモ・¥480)</button>
    <button class="closeBtn" id="closeUpgradeBtn">閉じる</button>
    <div class="installNote">※ これはデモ表示です。実際の課金・決済は発生しません。本番運用時はApple/GoogleのIn-App Purchase等に置き換える想定です。</div>"""

replace4 = """    <p id="upgradeBody">無料版はここまでです。プレミアムにアップグレードすると、ラウンド数・辞書検索回数が無制限になります。</p>
    <div style="font-size:12px; margin-bottom:12px; line-height:1.8; color:#4a4a3f; text-align:left;">
      <a href="terms.html" target="_blank" style="color:var(--indigo);">利用規約</a>
      ・<a href="privacy.html" target="_blank" style="color:var(--indigo);">プライバシーポリシー</a>
      ・<a href="tokushoho.html" target="_blank" style="color:var(--indigo);">特定商取引法に基づく表記</a>
      をご確認ください。
    </div>
    <label style="display:flex; align-items:flex-start; gap:8px; font-size:13px; text-align:left; margin-bottom:14px; cursor:pointer;">
      <input type="checkbox" id="ageConfirmCheckbox" style="margin-top:3px; width:18px; height:18px; flex-shrink:0;">
      <span>私は18歳以上であり、上記の利用規約・プライバシーポリシー・特定商取引法に基づく表記の内容に同意します。</span>
    </label>
    <div class="authError" id="paywallError"></div>
    <button class="primary" id="fakeBuyBtn">アップグレードする(月額110円)</button>
    <button class="closeBtn" id="closeUpgradeBtn">閉じる</button>
    <button class="linkBtn" id="portalLinkBtn" style="display:none; margin-top:10px;">契約管理はこちら</button>"""

content = replace_once(content, find4, replace4, "④ 法対応リンク・年齢確認の追加")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("")
print("パート1(CSS+HTML)の処理が完了しました。続けてパート2(JS)を実行してください。")
