# -*- coding: utf-8 -*-
"""
english-word-chain.html に、ログイン・課金機能のJavaScriptロジックを組み込むスクリプト(パート2)。
パート1(CSS+HTML)を先に実行してから使うこと。

使い方:
    python apply_eng_auth_part2.py <対象フォルダ>
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

if "API_BASE = " in content:
    print("すでにJSロジックが追加済みのようです。二重適用防止のため中止します。")
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


# ---- ① els オブジェクトに新しい要素を追加 ----
find1 = """    battleOverlay: document.getElementById('battleOverlay'), battleCard: document.getElementById('battleCard'),
  };"""
replace1 = """    battleOverlay: document.getElementById('battleOverlay'), battleCard: document.getElementById('battleCard'),
    accountBar: document.getElementById('accountBar'),
    loginOverlay: document.getElementById('loginOverlay'),
    authTitle: document.getElementById('authTitle'), authDesc: document.getElementById('authDesc'),
    authError: document.getElementById('authError'), authEmail: document.getElementById('authEmail'),
    authPassword: document.getElementById('authPassword'), authPasswordConfirm: document.getElementById('authPasswordConfirm'),
    authSubmitBtn: document.getElementById('authSubmitBtn'),
    forgotPasswordWrap: document.getElementById('forgotPasswordWrap'), forgotPasswordLink: document.getElementById('forgotPasswordLink'),
    forgotOverlay: document.getElementById('forgotOverlay'), forgotEmail: document.getElementById('forgotEmail'),
    forgotError: document.getElementById('forgotError'), forgotSubmitBtn: document.getElementById('forgotSubmitBtn'),
    forgotBackBtn: document.getElementById('forgotBackBtn'),
    resetOverlay: document.getElementById('resetOverlay'), resetPassword: document.getElementById('resetPassword'),
    resetPasswordConfirm: document.getElementById('resetPasswordConfirm'), resetError: document.getElementById('resetError'),
    resetSubmitBtn: document.getElementById('resetSubmitBtn'),
    ageConfirmCheckbox: document.getElementById('ageConfirmCheckbox'), paywallError: document.getElementById('paywallError'),
    portalLinkBtn: document.getElementById('portalLinkBtn'),
  };"""
content = replace_once(content, find1, replace1, "① els への追加")

# ---- ② isPremium の宣言直後に、認証まわりの全ロジックを追加 ----
find2 = "  let isPremium = false;"
replace2 = """  let isPremium = false;

  // ==================== ログイン・課金機能 ====================
  const API_BASE = "https://english-word-chain-account.hisashi-word-chain.workers.dev";
  let authToken = localStorage.getItem('engAuthToken');
  let authStatus = null;
  let isSignupMode = true;
  let resetTokenValue = null;

  async function apiFetch(path, options = {}){
    const headers = Object.assign({}, options.headers || {});
    if(authToken) headers['Authorization'] = `Bearer ${authToken}`;
    if(options.body) headers['Content-Type'] = 'application/json';
    const res = await fetch(`${API_BASE}${path}`, Object.assign({}, options, { headers }));
    const data = await res.json().catch(() => ({}));
    if(!res.ok) throw new Error(data.error || 'エラーが発生しました');
    return data;
  }

  function showAuthOverlay(){ els.loginOverlay.style.display = 'flex'; }
  function hideAuthOverlay(){ els.loginOverlay.style.display = 'none'; }

  function updateAccountBar(){
    if(!authStatus){ els.accountBar.innerHTML = ''; return; }
    let html = '';
    if(authStatus.status === 'trial'){
      html = `<div>🎁 無料期間中</div><button id="acctUpgradeBtn" class="upgradeBigBtn">🚀 アップグレードする</button>`;
    } else if(authStatus.status === 'active'){
      html = `<div>✅ 有料会員</div><button id="acctPortalBtn" class="upgradeBigBtn">契約管理</button>`;
    } else {
      html = `<div>⏰ 無料期間が終了しました</div><button id="acctUpgradeBtn" class="upgradeBigBtn">🚀 アップグレードする</button>`;
    }
    html += `<button id="acctLogoutBtn" class="smallLogout">ログアウト</button>`;
    els.accountBar.innerHTML = html;
    const up = document.getElementById('acctUpgradeBtn'); if(up) up.addEventListener('click', () => openUpgradeFlow());
    const pt = document.getElementById('acctPortalBtn'); if(pt) pt.addEventListener('click', openPortal);
    const lo = document.getElementById('acctLogoutBtn'); if(lo) lo.addEventListener('click', logout);
  }

  async function refreshAuthStatus(){
    if(!authToken){ isPremium = false; refreshTierUIIfReady(); showAuthOverlay(); return; }
    try{
      const data = await apiFetch('/auth/me', { method: 'GET' });
      authStatus = data;
      isPremium = (data.status === 'active');
      updateAccountBar();
      hideAuthOverlay();
      refreshTierUIIfReady();
    } catch(e){
      authToken = null;
      localStorage.removeItem('engAuthToken');
      isPremium = false;
      refreshTierUIIfReady();
      showAuthOverlay();
    }
  }

  function refreshTierUIIfReady(){
    if(typeof refreshTierUI === 'function') refreshTierUI();
  }

  function setAuthMode(signup){
    isSignupMode = signup;
    els.authTitle.textContent = isSignupMode ? 'はじめまして' : 'おかえりなさい';
    els.authDesc.textContent = isSignupMode
      ? 'メールアドレスと、お好きなパスワード(8文字以上)を決めるだけで始められます。メール認証は不要です。登録すると5日間無料でお試しいただけます。'
      : '登録済みのメールアドレスとパスワードでログインしてください。';
    els.authSubmitBtn.textContent = isSignupMode ? '無料で始める' : 'ログイン';
    els.authError.textContent = '';
    els.authPasswordConfirm.style.display = isSignupMode ? 'block' : 'none';
    els.authPasswordConfirm.value = '';
    els.forgotPasswordWrap.style.display = isSignupMode ? 'none' : 'block';
    document.getElementById('tabSignup').classList.toggle('activeTab', isSignupMode);
    document.getElementById('tabLogin').classList.toggle('activeTab', !isSignupMode);
  }

  async function handleAuthSubmit(){
    const email = els.authEmail.value.trim();
    const password = els.authPassword.value;
    els.authError.textContent = '';
    if(isSignupMode){
      if(password.length < 8){ els.authError.textContent = 'パスワードは8文字以上にしてください'; return; }
      if(password !== els.authPasswordConfirm.value){ els.authError.textContent = 'パスワードが一致しません。もう一度ご確認ください。'; return; }
    }
    try{
      const path = isSignupMode ? '/auth/signup' : '/auth/login';
      const data = await apiFetch(path, { method: 'POST', body: JSON.stringify({ email, password }) });
      authToken = data.token;
      localStorage.setItem('engAuthToken', authToken);
      await refreshAuthStatus();
    } catch(e){
      els.authError.textContent = e.message;
    }
  }

  async function logout(){
    try{ await apiFetch('/auth/logout', { method: 'POST' }); } catch(e){ /* ignore */ }
    authToken = null;
    authStatus = null;
    isPremium = false;
    localStorage.removeItem('engAuthToken');
    updateAccountBar();
    refreshTierUIIfReady();
    showAuthOverlay();
  }

  function openForgotPassword(){
    els.loginOverlay.style.display = 'none';
    els.forgotOverlay.style.display = 'flex';
    els.forgotError.textContent = '';
    els.forgotError.style.color = '';
    els.forgotEmail.value = els.authEmail.value || '';
  }
  function closeForgotPassword(){
    els.forgotOverlay.style.display = 'none';
    els.loginOverlay.style.display = 'flex';
  }
  async function handleForgotSubmit(){
    const email = els.forgotEmail.value.trim();
    els.forgotError.style.color = '';
    els.forgotError.textContent = '';
    if(!email){ els.forgotError.textContent = 'メールアドレスを入力してください'; return; }
    try{
      await apiFetch('/auth/request-reset', { method: 'POST', body: JSON.stringify({ email }) });
      els.forgotError.style.color = 'var(--ok)';
      els.forgotError.textContent = '再設定用のメールを送信しました(登録されている場合)。メールをご確認ください。';
    } catch(e){
      els.forgotError.textContent = e.message;
    }
  }

  function checkResetTokenInUrl(){
    const params = new URLSearchParams(window.location.search);
    const token = params.get('reset_token');
    if(token){
      resetTokenValue = token;
      els.loginOverlay.style.display = 'none';
      els.resetOverlay.style.display = 'flex';
      return true;
    }
    return false;
  }
  async function handleResetSubmit(){
    const password = els.resetPassword.value;
    const confirmPw = els.resetPasswordConfirm.value;
    els.resetError.textContent = '';
    if(password.length < 8){ els.resetError.textContent = 'パスワードは8文字以上にしてください'; return; }
    if(password !== confirmPw){ els.resetError.textContent = 'パスワードが一致しません'; return; }
    try{
      await apiFetch('/auth/reset-password', { method: 'POST', body: JSON.stringify({ token: resetTokenValue, password }) });
      els.resetOverlay.style.display = 'none';
      history.replaceState(null, '', window.location.pathname);
      setAuthMode(false);
      showAuthOverlay();
      alert('パスワードを再設定しました。新しいパスワードでログインしてください。');
    } catch(e){
      els.resetError.textContent = e.message;
    }
  }

  function openUpgradeFlow(){
    if(!authToken){ showAuthOverlay(); return; }
    els.ageConfirmCheckbox.checked = false;
    els.paywallError.textContent = '';
    els.portalLinkBtn.style.display = (authStatus && authStatus.status === 'active') ? 'inline-block' : 'none';
    showUpgrade('無料版はここまでです。プレミアムにアップグレードすると、ラウンド数・辞書検索回数が無制限になります。');
  }

  function confirmUpgrade(){
    if(!els.ageConfirmCheckbox.checked){
      els.paywallError.textContent = '同意いただける場合のみお進みいただけます。';
      return;
    }
    els.paywallError.textContent = '';
    startCheckout();
  }

  async function startCheckout(){
    if(!authToken){ showAuthOverlay(); return; }
    try{
      const data = await apiFetch('/billing/create-checkout-session', { method: 'POST' });
      window.location.href = data.url;
    } catch(e){
      alert('決済ページの取得に失敗しました: ' + e.message);
    }
  }

  async function openPortal(){
    try{
      const data = await apiFetch('/billing/portal', { method: 'POST' });
      window.location.href = data.url;
    } catch(e){
      alert('契約管理ページの取得に失敗しました: ' + e.message);
    }
  }

  async function checkBillingReturn(){
    const params = new URLSearchParams(window.location.search);
    if(params.get('billing') === 'success'){
      for(let i = 0; i < 5; i++){
        await new Promise(r => setTimeout(r, 1500));
        await refreshAuthStatus();
        if(authStatus && authStatus.status === 'active') break;
      }
      history.replaceState(null, '', window.location.pathname);
    }
  }
"""
content = replace_once(content, find2, replace2, "② 認証ロジックの追加")

# ---- ③ fakeBuyBtn のイベントを、本物の決済確認に置き換え ----
find3 = """  document.getElementById('fakeBuyBtn').addEventListener('click', ()=>{
    // DEMO ONLY: no real payment is processed. In production this would call
    // a real payment API (e.g. Apple/Google In-App Purchase or Stripe Checkout).
    isPremium = true;
    refreshTierUI();
    els.upgradeOverlay.style.display = 'none';
    setFeedback('🌟 プレミアムにアップグレードしました(実際の課金はありません)', true);
    if(state && !state.alive === false){}
  });"""

replace3 = """  document.getElementById('fakeBuyBtn').addEventListener('click', confirmUpgrade);
  els.portalLinkBtn.addEventListener('click', openPortal);
  els.authSubmitBtn.addEventListener('click', handleAuthSubmit);
  document.getElementById('tabSignup').addEventListener('click', () => setAuthMode(true));
  document.getElementById('tabLogin').addEventListener('click', () => setAuthMode(false));
  els.forgotPasswordLink.addEventListener('click', openForgotPassword);
  els.forgotBackBtn.addEventListener('click', closeForgotPassword);
  els.forgotSubmitBtn.addEventListener('click', handleForgotSubmit);
  els.resetSubmitBtn.addEventListener('click', handleResetSubmit);
  if(!checkResetTokenInUrl()){
    refreshAuthStatus().then(checkBillingReturn);
  }"""

content = replace_once(content, find3, replace3, "③ fakeBuyBtn イベントの置き換え")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("")
print("処理が完了しました。上記でエラーが無ければ全て成功です。")
