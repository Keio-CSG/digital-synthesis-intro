#!/usr/bin/env python3
"""Generate the static course website into docs/ (GitHub Pages).
Code snippets are read from the repo files so the site and the repo cannot drift apart.
Usage: python3 tools/build_site.py"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)

NL = "\n"

def code(path, start=None, end=None, lang=""):
    """Embed a repo file (optionally between two marker substrings) as a code block."""
    txt = (ROOT / path).read_text()
    if start:
        txt = txt[txt.index(start):]
    if end:
        txt = txt[:txt.index(end)]
    return f'<figure class="code"><figcaption>{html.escape(path)}</figcaption><pre><code>{html.escape(txt.strip(chr(10)))}</code></pre></figure>'

def snippet(text, cap=""):
    c = f"<figcaption>{html.escape(cap)}</figcaption>" if cap else ""
    return f'<figure class="code">{c}<pre><code>{html.escape(text.strip(chr(10)))}</code></pre></figure>'

def img(name, alt, cap):
    return f'<figure class="img"><img src="img/{name}" alt="{html.escape(alt)}" loading="lazy"><figcaption>{html.escape(cap)}</figcaption></figure>'

def note(kind, title, body):
    return f'<aside class="note {kind}"><strong>{title}</strong><div>{body}</div></aside>'

PAGES = []   # (slug, title, summary, body)


ARCH_SVG = """
<svg viewBox="0 0 940 420" role="img" aria-label="MAC4 のアーキテクチャ図" class="arch">
  <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--muted)"/></marker></defs>
  <!-- top level -->
  <text x="10" y="18" class="h">MAC4（トップ）</text>
  <rect x="10" y="28" width="300" height="372" rx="10" class="top"/>
  <g class="lane"><rect x="40" y="52" width="190" height="62" rx="8"/><text x="135" y="78">lane 0</text><text x="135" y="98" class="s">a[3:0] × b[3:0] → acc[11:0]</text></g>
  <g class="lane"><rect x="40" y="132" width="190" height="62" rx="8"/><text x="135" y="158">lane 1</text><text x="135" y="178" class="s">a[7:4] × b[7:4] → acc[23:12]</text></g>
  <g class="lane"><rect x="40" y="212" width="190" height="62" rx="8"/><text x="135" y="238">lane 2</text><text x="135" y="258" class="s">a[11:8] × b[11:8] → acc[35:24]</text></g>
  <g class="lane"><rect x="40" y="292" width="190" height="62" rx="8"/><text x="135" y="318">lane 3</text><text x="135" y="338" class="s">a[15:12] × b[15:12] → acc[47:36]</text></g>
  <text x="160" y="366" class="s">共通の入力: clk, rst_n, clr, en</text>
  <text x="160" y="390" class="s">各レーンは同じ回路（MAC4_LANE）</text>
  <!-- lane detail -->
  <text x="350" y="18" class="h">1レーン（MAC4_LANE）の中身</text>
  <rect x="340" y="28" width="590" height="372" rx="10" class="top"/>
  <g class="blk"><rect x="360" y="90" width="90" height="46" rx="6"/><text x="405" y="110">a_q</text><text x="405" y="126" class="s">4bit レジスタ</text></g>
  <g class="blk"><rect x="360" y="170" width="90" height="46" rx="6"/><text x="405" y="190">b_q</text><text x="405" y="206" class="s">4bit レジスタ</text></g>
  <g class="blk"><rect x="360" y="250" width="90" height="46" rx="6"/><text x="405" y="270">en_q, clr_q</text><text x="405" y="286" class="s">制御レジスタ</text></g>
  <g class="calc"><rect x="500" y="115" width="100" height="72" rx="6"/><text x="550" y="146">乗算</text><text x="550" y="166" class="s">4bit × 4bit</text><text x="550" y="180" class="s">→ 8bit</text></g>
  <g class="calc"><rect x="650" y="115" width="90" height="72" rx="6"/><text x="695" y="146">加算</text><text x="695" y="166" class="s">acc + 積</text><text x="695" y="180" class="s">12bit</text></g>
  <g class="blk big"><rect x="785" y="115" width="125" height="72" rx="6"/><text x="847" y="144">acc</text><text x="847" y="164" class="s">12bit レジスタ</text><text x="847" y="178" class="s">= 出力 acc</text></g>
  <path d="M450,113 H475 V135 H498 M450,193 H475 V167 H498 M600,151 H648 M740,151 H783" class="arr"/>
  <path d="M847,187 V235 H695 V189" class="arr fb"/>
  <text x="770" y="253" class="s">前の値に足し込む（フィードバック）</text>
  <path d="M450,273 H700 V290 H847 V189" class="arr ctl"/>
  <text x="560" y="312" class="s">clr_q = 1 でゼロに戻す / en_q = 1 のときだけ更新</text>
  <text x="360" y="62" class="s l">入力 a, b, en, clr（1クロック遅れて取り込み）</text>
  <text x="360" y="376" class="s l">すべてのレジスタは同じクロック clk で動く。rst_n（非同期リセット）で 0 に戻る。</text>
</svg>
"""

# ---------------------------------------------------------------- index
FLOW_SVG = """
<svg viewBox="0 0 920 250" role="img" aria-label="RTLからsignoffまでのフロー" class="flow">
  <defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--muted)"/></marker></defs>
  <g class="n"><rect x="10"  y="20" width="130" height="54" rx="8"/><text x="75"  y="44">RTL + TB</text><text x="75" y="62" class="s">02 シミュレーション</text></g>
  <g class="n"><rect x="170" y="20" width="130" height="54" rx="8"/><text x="235" y="44">論理合成</text><text x="235" y="62" class="s">03 DC</text></g>
  <g class="n"><rect x="330" y="20" width="130" height="54" rx="8"/><text x="395" y="44">等価性検証</text><text x="395" y="62" class="s">04 Formality</text></g>
  <g class="n"><rect x="490" y="20" width="130" height="54" rx="8"/><text x="555" y="44">配置配線</text><text x="555" y="62" class="s">05 P&amp;R</text></g>
  <g class="n"><rect x="650" y="20" width="130" height="54" rx="8"/><text x="715" y="44">寄生抽出</text><text x="715" y="62" class="s">06 StarRC</text></g>
  <g class="n hl"><rect x="650" y="150" width="130" height="54" rx="8"/><text x="715" y="174">signoff STA</text><text x="715" y="192" class="s">07 PrimeTime</text></g>
  <g class="n hl"><rect x="490" y="150" width="130" height="54" rx="8"/><text x="555" y="174">SDF付き GLS</text><text x="555" y="192" class="s">08 論理シミュレーション</text></g>
  <g class="n hl"><rect x="330" y="150" width="130" height="54" rx="8"/><text x="395" y="174">DRC / LVS</text><text x="395" y="192" class="s">09 物理検証</text></g>
  <g class="n"><rect x="170" y="150" width="130" height="54" rx="8"/><text x="235" y="174">テープアウト</text><text x="235" y="192" class="s">GDS を渡す</text></g>
  <path d="M140,47 H168 M300,47 H328 M460,47 H488 M620,47 H648" class="a"/>
  <path d="M715,74 V148 M648,177 H622 M488,177 H462 M328,177 H302" class="a"/>
  <text x="787" y="112" class="s">ネットリスト・GDS・SPEF・SDF</text>
</svg>
"""
PAGES.append(("index", "デジタル論理合成入門", "RTLからsignoffまでを、動くリポジトリで体験する。", f"""
<p class="lead">論理合成（RTL → ゲート）だけでなく、<strong>配置配線・寄生抽出・signoffタイミング・ゲートレベルシミュレーション・物理検証</strong>までを、小さな回路で一周します。各ステップは1コマンドで動き、出力ログの読み方まで学べます。</p>
{FLOW_SVG}
{img("layout.png","最終レイアウト","このコースで最後にできあがるもの: 配置配線後のレイアウト（GDS）。色が金属配線の層、縦の太い線が電源。")}
<h2>使うツール</h2>
<table>
<tr><th>ステップ</th><th>ツール</th></tr>
<tr><td>RTL・ゲートレベルシミュレーション</td><td>Cadence Xcelium</td></tr>
<tr><td>論理合成</td><td>Synopsys Design Compiler（<code>dc_shell</code>）</td></tr>
<tr><td>等価性検証</td><td>Synopsys Formality（<code>fm_shell</code>）</td></tr>
<tr><td>配置配線</td><td>Synopsys IC Compiler II（<code>icc2_shell</code>）</td></tr>
<tr><td>寄生抽出</td><td>Synopsys StarRC（<code>StarXtract</code>）</td></tr>
<tr><td>signoff STA</td><td>Synopsys PrimeTime（<code>pt_shell</code>）</td></tr>
<tr><td>DRC / LVS</td><td>Siemens Calibre</td></tr>
</table>
<h2>このコースで答えられるようになる問い</h2>
<table>
<tr><th>ステップ</th><th>答える問い</th><th>主な入力 → 出力</th></tr>
<tr><td><a href="02-rtl-sim.html">02 RTLシミュレーション</a></td><td>RTLは仕様どおり動くか</td><td>RTL, TB → PASS/FAIL（Xcelium）</td></tr>
<tr><td><a href="03-synthesis.html">03 論理合成</a></td><td>目標周波数で動くゲート回路にできるか</td><td>RTL, SDC → ネットリスト（Design Compiler）</td></tr>
<tr><td><a href="04-formal.html">04 等価性検証</a></td><td>合成しても論理は変わっていないか</td><td>RTL, ネットリスト → 等価/非等価（Formality）</td></tr>
<tr><td><a href="05-pnr.html">05 配置配線</a></td><td>実際のレイアウトにできるか（クロックツリー込み）</td><td>ネットリスト → GDS（IC Compiler II）</td></tr>
<tr><td><a href="06-extraction.html">06 寄生抽出</a></td><td>配線の抵抗・容量はいくらか</td><td>レイアウト → SPEF（StarRC）</td></tr>
<tr><td><a href="07-sta.html">07 signoff STA</a></td><td>全コーナーで setup / hold を満たすか</td><td>ネットリスト, SPEF, SDC → slack（PrimeTime）</td></tr>
<tr><td><a href="08-gls.html">08 ゲートレベルシミュレーション</a></td><td>遅延込みでも正しく動くか</td><td>ネットリスト, SDF → PASS/FAIL（Xcelium）</td></tr>
<tr><td><a href="09-physical-verification.html">09 物理検証</a></td><td>製造ルールを守り、回路図と一致するか</td><td>GDS → DRC/LVSレポート（Calibre）</td></tr>
</table>
{note("tip","進め方","まず <a href='01-setup.html'>01 セットアップ</a> でリポジトリを用意し、<code>make all</code> で全体を一度通してから、各章を読みながらログを開いてください。各章の最後に演習があります。")}
{note("warn","このサイトについて","プロセス固有のファイル（ライブラリ・ルールデック・ツールの場所など）は含まれません。それらは各研究室・各自の環境で用意し、<code>config/</code> に置きます（<a href='01-setup.html'>01 セットアップ</a>）。")}
"""))

# ---------------------------------------------------------------- 01 setup
PAGES.append(("01-setup", "01 セットアップ", "リポジトリの構成と、環境依存部分の分け方。", f"""
<p>このリポジトリは<strong>環境に依存する情報を <code>config/</code> に隔離</strong>しています。スクリプト本体にはパスもライブラリ名も書かれていません。</p>
<h2>ディレクトリ構成</h2>
{snippet('''
rtl/      RTL（MAC4_LANE.v = 1レーン, MAC4.v = 4レーンのトップ）
tb/       自己チェック付きテストベンチ
const/    SDC（DC・ICC2・PrimeTime で共通に使う）
sim/      RTLシミュレーション / ゲートレベルシミュレーション
dc/       論理合成        fm/   等価性検証
icc2/     配置配線        rcx/  寄生抽出
sta/      signoff STA     verif/ DRC・LVS
config/   環境依存ファイル（local.example.* をコピーして自分用を作る）
docs/     このWebサイト（tools/build_site.py で生成）
Makefile  make all で全ステップ
''')}
<h2>手順</h2>
<ol>
<li>リポジトリを取得する（<code>git clone https://github.com/Keio-CSG/digital-synthesis-intro.git</code>）。</li>
<li><strong>研究室のメンバーは、用意済みの config をコピーします。</strong>研究室のサーバでは、次の場所に置いてあります（開けない場合は指導教員か先輩に聞いてください）。
{snippet('''
csh tools/setup_config.csh /home/ylab/yoshioka/digital-synthesis-intro-config
make sim            # 動けば設定はOK
''')}
<code>config/</code> に必要な6ファイルがコピーされます。すでにファイルがある場合は、<code>.bak</code> に退避します。</li>
<li><strong>それ以外の環境で使う人は</strong>、<code>config/</code> の <code>*.example.*</code> をコピーして、自分の環境の値で埋めます。
{snippet('''
cp config/local.example.csh          config/local.csh           # ツールの読み込み・ライブラリのファイル位置
cp config/tech.example.tcl           config/tech.tcl            # 金属層の名前・配線方向
cp config/starrc_layer.example.map   config/starrc_layer.map    # レイアウト層名 → 抽出用の層名
cp config/prep_drc.example.csh       config/prep_drc.csh        # DRCデックの準備
cp config/prep_lvs.example.csh       config/prep_lvs.csh        # LVSデックの準備
cp config/render.example.json        config/render.json         # 画像生成用（GDS の層番号など）
''')}
これらの実体は <code>.gitignore</code> に入っており、<strong>コミットされません</strong>。値は指導教員・先輩から教わってください。</li>
<li>全体を実行する。
{snippet('''
source env.csh      # 任意: ツールが使えるか確認
make all            # sim → syn → fm → pnr → rcx → sta → gls → drc → lvs
make clean          # 生成物を全部消す
''')}
</li>
</ol>
{note("tip","ステップ単体で実行","<code>make syn</code> のようにステップ名を指定できます。上流が済んでいない場合は、先にそのステップを実行してください（例: <code>make sta</code> には <code>make pnr rcx</code> が必要）。")}
<h2>config/local.csh に書く変数（名前だけ）</h2>
<table>
<tr><th>変数</th><th>意味</th></tr>
<tr><td><code>STD_DB_WC / TC / BC</code></td><td>スタンダードセルのタイミングライブラリ（遅い／標準／速いコーナー）</td></tr>
<tr><td><code>STD_NDM</code>, <code>STD_LIBNAME</code></td><td>ICC2 用のセルライブラリ</td></tr>
<tr><td><code>TECH_FILE</code>, <code>TLUP_*</code>, <code>LAYER_MAP</code></td><td>テクノロジファイル・RC モデル</td></tr>
<tr><td><code>GDS_LAYER_MAP</code>, <code>STD_GDS</code></td><td>GDS 出力用の層対応・セルの GDS</td></tr>
<tr><td><code>STD_VERILOG</code>, <code>STD_CDL</code></td><td>ゲートレベルシミュレーション用モデル／LVS 用 SPICE</td></tr>
<tr><td><code>FILLER_CELLS</code></td><td>フィラーセル名（大きい順）</td></tr>
<tr><td><code>DRC_DECK</code>, <code>LVS_DECK</code></td><td>物理検証のルールデック</td></tr>
</table>
"""))

# ---------------------------------------------------------------- 02 RTL / sim
PAGES.append(("02-rtl-sim", "02 RTLとシミュレーション", "題材 MAC4 と、自己チェック付きテストベンチ。", f"""
<h2>題材: 4レーン乗加算器 (MAC4)</h2>
<p>1レーンは <strong>4bit × 4bit の乗算結果を 12bit のアキュムレータに足し込む</strong>回路で、入力にレジスタが付いています。これを4レーン並べ、クロックとリセットを共有します（約90個のフリップフロップ）。小さいですが、<em>クロックツリーが必要になるくらいの数</em>です。</p>
{ARCH_SVG}
<p>図の左が4レーンを並べたトップ、右が1レーンの中身です。データは <strong>入力レジスタ → 乗算 → 加算 → アキュムレータ</strong>と流れ、アキュムレータの値は次のサイクルの加算にフィードバックされます。</p>
{code("rtl/MAC4_LANE.v")}
{code("rtl/MAC4.v")}
<p>シミュレータは <strong>Cadence Xcelium</strong>（<code>xrun</code>）です。</p>
<h2>テストベンチ</h2>
<p>乱数入力を DUT と<strong>振る舞いモデル</strong>に同時に与え、毎サイクル出力を比べます。人が波形を見なくても PASS/FAIL が出ることが重要です。後のゲートレベルシミュレーションでも<strong>同じテストベンチ</strong>を使います。</p>
{code("tb/tb_MAC4.v", "    // reference model", "    `ifdef DUMP")}
{snippet("cd sim && csh run_rtl.csh"+NL+"# ..."+NL+"PASS: 400 cycles, no mismatch", "実行と期待される出力")}
{note("warn","つまずきポイント: リセットの解除タイミング","リセットを<strong>クロックエッジちょうど</strong>で解除すると、ゲートレベルでは recovery 違反になり出力が <code>X</code> になります（RTLでは気づけません）。テストベンチでは <code>@(negedge clk)</code> で解除しています。")}
<h2>演習</h2>
<ol><li><code>MAC4_LANE.v</code> のアキュムレートを <code>acc + a_q*b_q</code> から <code>acc + a_q+b_q</code> に変えて、テストが FAIL になることを確認する。</li>
<li>リセット解除を <code>#23 rst_n = 1;</code> に戻すとどうなるか、<a href="08-gls.html">08章</a>の後で試す。</li></ol>
"""))

# ---------------------------------------------------------------- 03 synthesis
PAGES.append(("03-synthesis", "03 論理合成", "SDC でゴールを決め、DC でゲートに変換する。", f"""
<p>論理合成は「RTL を、<strong>制約を満たす</strong>ゲートの接続に変換する」作業です。ここでは <strong>Synopsys Design Compiler</strong>（<code>dc_shell</code>）を使います。<strong>制約（SDC）こそが仕様書</strong>で、同じ RTL でも制約が違えば別の回路になります。</p>
<h2>1. 制約 (SDC)</h2>
{code("const/MAC4.sdc")}
<table>
<tr><th>コマンド</th><th>意味</th></tr>
<tr><td><code>create_clock</code></td><td>クロック周期 = 2.0 ns（500 MHz）。ここが目標性能。</td></tr>
<tr><td><code>set_clock_uncertainty</code></td><td>スキュー・ジッタの余裕。setup は大きく、hold は小さめに。</td></tr>
<tr><td><code>set_input_delay / set_output_delay</code></td><td>前後のブロックが使う時間。入出力パスの持ち時間は 周期 − delay になる。</td></tr>
<tr><td><code>set_input_transition / set_load</code></td><td>入力の波形のなまりと、出力の負荷。</td></tr>
<tr><td><code>set_false_path -from rst_n</code></td><td>非同期リセットはクロックとの関係を見ない。</td></tr>
</table>
<h2>2. 合成スクリプトの流れ</h2>
{code("dc/dc.tcl", "# 1. read RTL", "# 4. outputs")}
<ul>
<li><code>analyze</code> → <code>elaborate</code> → <code>link</code>: RTL を読み、階層をつなぎ、セルライブラリに結び付ける。</li>
<li><code>check_design</code>: 未接続・多重ドライバがないか。<strong>警告は必ず読む。</strong></li>
<li><code>compile_ultra</code>: 論理の最適化とセルへのマッピング。</li>
</ul>
{note("tip","どのコーナーで合成する？","setup（遅すぎないか）は<strong>遅いコーナー</strong>、hold は<strong>速いコーナー</strong>で見るのが原則です。このスクリプトは <code>CORNER=wc|tc|bc</code> で切り替えます（既定: wc）。数値を書くときは<strong>必ずコーナーを併記</strong>してください。")}
<h2>3. レポートの読み方</h2>
{snippet('''
Startpoint: acc_reg_1_   (rising edge-triggered flip-flop clocked by clk)
Endpoint:   acc_reg_9_
  data arrival time          ← クロック開始から、データが終点に着くまで
  clock period               ← 次のクロックまで
  - clock uncertainty
  - setup time               ← フリップフロップが必要とする準備時間
  data required time
  slack (MET)  +0.xx         ← required − arrival。0 以上なら OK、負なら違反''', "report_timing の読み方（模式）")}
<ul><li><code>MAC4.max.timing.log</code>: 最も厳しい setup パス</li><li><code>MAC4.min.timing.log</code>: hold パス</li><li><code>MAC4.area.log</code>: 面積。</li><li><code>MAC4.qor.log</code>: 全体の要約。</li></ul>
{note("warn","この段階のタイミングは<em>理想値</em>","配線の遅延もクロックツリーもありません。合成で slack に余裕があっても、配置配線後に減ります。<a href='07-sta.html'>07章</a>の signoff が最終判断です。")}
<h2>演習</h2>
<ol><li><code>CLK_PERIOD</code> を 1.5 にして <code>make syn</code>。slack は負になるか？ 面積はどう変わるか？</li>
<li>同じ周期で <code>CORNER=tc</code> と <code>CORNER=wc</code> を比べる。</li>
<li><code>set_false_path</code> を消すと何が変わるか（<code>report_timing</code> の端点を見る）。</li></ol>
"""))

# ---------------------------------------------------------------- 04 formal
PAGES.append(("04-formal", "04 等価性検証", "合成後のネットリストが、RTLと論理的に等価であることを証明する。", f"""
<p>シミュレーションは「テストした入力では正しい」ことしか示せません。<strong>等価性検証 (Formal Equivalence)</strong> は、RTL とネットリストの <em>すべての入力</em> に対して出力が一致することを数学的に確認します。</p>
{code("fm/fm.tcl")}
<p>ツールは <strong>Synopsys Formality</strong>（<code>fm_shell</code>）です。</p>
<h2>流れ</h2>
<ol><li><strong>set_svf</strong>: 合成ツールが行った最適化のヒントを渡す（これがないと、状態の並べ替えなどで失敗しやすい）。</li>
<li><strong>reference</strong> = RTL、<strong>implementation</strong> = ネットリスト（セルの機能はライブラリから読む）。</li>
<li><strong>match</strong>: 両者のレジスタ・ポートを対応づける（比較点を作る）。</li>
<li><strong>verify</strong>: 比較点ごとに組み合わせ論理が等価か証明する。</li></ol>
{snippet("make fm"+NL+"..."+NL+"FORMALITY RESULT: PASS")}
<h2>失敗したら</h2>
<ul><li><code>unmatched.log</code>: 対応づけできなかった点。名前の変化・定数化されたレジスタが典型。</li>
<li><code>failing.log</code>: 等価でなかった点。ここに出たら<strong>本当に論理が変わっています</strong>（合成のバグ、または RTL のシミュレーションと合成の解釈の違い）。</li></ul>
{note("tip","いつ使う？","合成後と、配置配線後の両方で行うのが標準です。物理実装の途中でツールが論理を触る（バッファ挿入・ゲートの置換など）ためです。")}
<h2>演習</h2>
<ol><li>RTL の <code>acc + a_q*b_q</code> を一時的に変えて、<strong>RTL だけ</strong>変更し <code>make fm</code> を実行（ネットリストは古いまま）。FAIL の出力を読む。</li></ol>
"""))

# ---------------------------------------------------------------- 05 pnr
PAGES.append(("05-pnr", "05 配置配線", "フロアプランからクロックツリー合成、配線、GDS出力まで。", f"""
<p>ツールは <strong>Synopsys IC Compiler II</strong>（<code>icc2_shell</code>）です。ネットリストを<strong>実際の形</strong>にします。配置配線で初めて「配線遅延」「クロックツリー」「電源網」が現れます。</p>
<h2>手順の全体像</h2>
<ol>
<li><strong>ライブラリ作成・ネットリスト読み込み</strong>（<code>create_lib</code>, <code>read_verilog</code>, <code>link_block</code>）</li>
<li><strong>RC モデルとシナリオ</strong>: 寄生モデルと、SDC を読み込んだシナリオ（setup と hold を両方解析）</li>
<li><strong>フロアプラン</strong>: コアの大きさと、ピン配置（<code>initialize_floorplan</code>, <code>place_pins</code>）</li>
<li><strong>電源網</strong>: 縦の電源ストラップと、セル列の電源レール、その間をつなぐビア（<code>create_pg_*</code>, <code>compile_pg</code>）</li>
<li><strong>配置</strong>: <code>place_opt</code> — セルを置き、タイミングを見ながら最適化</li>
<li><strong>クロックツリー合成 + hold 修正</strong>: <code>clock_opt</code></li>
<li><strong>配線</strong>: <code>route_auto</code>, <code>route_opt</code>、<code>check_routes</code></li>
<li><strong>フィラー</strong>で隙間を埋める</li>
<li><strong>出力</strong>: ネットリスト（検証用）、GDS、DEF、SDF</li></ol>
<h2>フロアプラン</h2>
{code("icc2/icc2.tcl", "# --- floorplan parameters", "# --- multi-core")}
<p>面積の目安: セル面積の合計 ÷ 目標利用率（ここでは約 50%）≒ コア面積。狭すぎると配線できず、広すぎると配線が長くなります。</p>
<h2>クロックツリー合成 (CTS)</h2>
{code("icc2/icc2.tcl", "# 8. Placement", "# ============================================================================="+NL+"# 10.")}
<p>配置の時点では<strong>クロックは理想</strong>（全フリップフロップに同時に届く）として扱われます。<code>clock_opt</code> でクロックバッファの木を作り、各フリップフロップへの到着時間のばらつき（<strong>スキュー</strong>）を揃えます。同時に、データが早く着きすぎる <strong>hold 違反</strong>を遅延セルの挿入で直します。</p>
{snippet('''
Clock   Sinks  Levels  Repeater  Latency  Skew
clk       88      2         3      ~0.06   ~0.01      ← cts.skew.log (icc2/)''', "CTS 後のクロック QoR（出力の形）")}
{note("warn","小さな回路では CTS が何もしない","フリップフロップが20個ほどなら、クロックポートが全部を直接駆動でき、バッファが入りません。このコースで4レーンにしているのは、ツリーができる様子を見るためです。")}
<h2>できあがったものを見る</h2>
<p>ツールのビューアがなくても結果を確認できるよう、GDS と DEF から画像を作るスクリプト（<code>tools/render_layout.py</code>、<code>python3 tools/render_layout.py</code>）を付けています。</p>
{img("placement.png","配置結果","配置: セルの色は4つのレーンごと。濃いセルがフリップフロップ、赤がクロックバッファ。同じレーンのセルがまとまって置かれる。")}
{img("clock_tree.png","クロックツリー","クロックツリー: 赤い四角がクロックバッファ、青い線がクロック配線、黒い点が88個のフリップフロップ。1本のクロックが枝分かれして全部に届く。")}
{img("power_grid.png","電源網","電源網: 横の線が標準セルの電源レール（最下層の金属）、縦の太い線が上位の金属の電源ストラップ。赤が VDD、青が VSS。交点がビアでつながっている。")}
{img("layout.png","最終レイアウト","最終レイアウト (GDS): セルの輪郭と、金属層ごとの配線。工場に渡すのはこのデータ。")}
<h2>レポートの見どころ</h2>
<table>
<tr><th>ファイル</th><th>見るもの</th></tr>
<tr><td><code>MAC4.pre_cts.timing.log</code></td><td>CTS 前の setup（クロック理想）</td></tr>
<tr><td><code>MAC4.cts.timing.log</code></td><td>CTS 後の setup（クロック伝搬）。<strong>配線遅延が入って slack が減る</strong></td></tr>
<tr><td><code>MAC4.cts.hold.log</code></td><td>CTS 後の hold。<strong>修正前は負になりやすい</strong></td></tr>
<tr><td><code>MAC4.cts.skew.log</code></td><td>スキュー・レイテンシ・バッファ数</td></tr>
<tr><td><code>MAC4.check_routes.log</code></td><td>配線の DRC/オープン/ショート（0 であること）</td></tr>
</table>
{note("warn","電源は「引いた」だけでは足りない","電源レールが上位の電源とビアでつながっていないと、タイミングも DRC も通るのに、<a href='09-physical-verification.html'>LVS だけが落ちます</a>。電源網を作った直後に、ビアが全部のレールに付いたかを確認してください（この教材では実際にそれで一度つまずきました）。")}
{note("tip","ICC2 の結果は暫定","ICC2 内の寄生抽出は簡易です。最終判断は次章以降の <strong>StarRC + PrimeTime</strong> で行います。")}
<h2>演習</h2>
<ol><li><code>core_width</code> を 90 に広げて再実行。配線長（<code>cts.skew.log</code> の Wire Length）はどうなるか。</li>
<li>CTS 前後の setup slack を比べ、なぜ変わるか説明する。</li></ol>
"""))

# ---------------------------------------------------------------- 06 extraction
PAGES.append(("06-extraction", "06 寄生抽出", "レイアウトから配線の抵抗・容量を取り出し、SPEF にする。", f"""
<p>ツールは <strong>Synopsys StarRC</strong> です。配線は「ただの線」ではなく、<strong>抵抗 R と容量 C</strong>を持ち、隣の線とは<strong>結合容量</strong>でつながっています。これを抽出して <strong>SPEF</strong> というテキストにまとめ、STA ツールに渡します。</p>
{code("rcx/run_starrc.csh")}
<h2>入力</h2>
<ul><li><strong>レイアウト</strong>（ICC2 のデータベース）。どの金属がどのネットか。</li>
<li><strong>テクノロジ（RC モデル）</strong>: 各層の厚み・誘電体などから作られた抽出用のデータ。</li>
<li><strong>層の対応表</strong>（<code>config/starrc_layer.map</code>）: レイアウト側の層の名前と、抽出用モデル側の名前を結ぶ。<em>合っていないと「この層は未定義」というエラーで止まります</em>。</li></ul>
<h2>確認ポイント</h2>
<ul><li><code>starrc.log</code> の <code>Errors: 0</code>。</li>
<li>PrimeTime で読み込んだ時の <code>report_annotated_parasitics</code>: <strong>ほぼ全ネットに寄生が付いたか</strong>。付いていない配線は「理想（遅延ゼロ）」扱いで、タイミングが甘く出ます。</li>
<li>抵抗が付いているか（<code>REDUCTION</code> の設定が強すぎると R が消えます）。</li></ul>
{note("tip","コーナー","実際のsignoffでは、容量が大きいコーナー（setup 用）と小さいコーナー（hold 用）でそれぞれ抽出します。この教材は1コーナーの抽出で、遅延ライブラリ側のコーナーを切り替えて解析します。")}
"""))

# ---------------------------------------------------------------- 07 sta
PAGES.append(("07-sta", "07 signoff STA", "実配線の寄生込みで、setup と hold をそれぞれ最悪のコーナーで確認する。", f"""
<p>ツールは <strong>Synopsys PrimeTime</strong>（<code>pt_shell</code>）です。ここが<strong>最終判定</strong>です。合成・ICC2 のタイミングは途中経過で、テープアウト可否は signoff の STA（静的タイミング解析）で決まります。</p>
{code("sta/pt.tcl")}
<h2>なぜ2回走らせるのか</h2>
<table>
<tr><th>チェック</th><th>最悪になる条件</th><th>使うコーナー</th></tr>
<tr><td><strong>setup</strong>（データが遅すぎないか）</td><td>データは遅く、クロックは早く</td><td><strong>遅いコーナー</strong>（低電圧・高温）</td></tr>
<tr><td><strong>hold</strong>（データが早すぎないか）</td><td>データは早く、クロックは遅く</td><td><strong>速いコーナー</strong>（高電圧・低温）</td></tr>
</table>
<p>同じ回路でも、動作条件が変わると遅延が大きく変わります。<code>MODE=setup</code> と <code>MODE=hold</code> で別々に実行します。</p>
<h2>スクリプトの要点</h2>
<ul>
<li><code>read_verilog</code> + <code>link_design</code>: ICC2 が出したネットリスト。</li>
<li><code>source const/MAC4.sdc</code>: <strong>合成と同じ SDC</strong>。制約が途中で変わっていないこと。</li>
<li><code>read_parasitics</code>: SPEF を読む。</li>
<li><code>set_propagated_clock</code>: クロックを<strong>実際の経路</strong>で伝搬させる。</li>
<li><code>check_timing</code>: 制約の抜け（入力に遅延が無い・クロックが来ないレジスタなど）。<strong>slack が良くても、ここに警告があれば信用できません</strong>。</li></ul>
<h2>結果の読み方</h2>
{snippet('''
setup (遅いコーナー):  report_timing -delay_type max  → slack +0.05 ns  (MET)
hold  (速いコーナー):  report_timing -delay_type min  → slack +0.01 ns  (MET)''', "この教材の参考値（コーナーを併記）")}
<ul><li><code>*.max.log</code> / <code>*.min.log</code>: 最悪パスの詳細（<code>-input_pins</code> でセルごとの遅延が見える）。</li>
<li><code>*.violators.log</code>: 違反の一覧。空であること。</li>
<li><code>*.skew.log</code>: クロックスキュー。</li>
<li><code>*.annotated.log</code>: 寄生が付いたネットの割合。</li>
<li><code>*.coverage.log</code>: 解析されたパスの網羅度。</li></ul>
{note("warn","hold の slack が小さいのは普通","hold は周期に依存せず、クロックを遅くしても改善しません。修正は<strong>遅延セルの挿入</strong>しかありません。ICC2 の CTS 段階で直す理由です。")}
<h2>違反したときの打ち手</h2>
<table>
<tr><th>違反</th><th>対策</th></tr>
<tr><td>setup</td><td>周期を延ばす / 論理を浅くする（パイプライン）/ ドライブの強いセルへ / 配置を近づける</td></tr>
<tr><td>hold</td><td>遅延セル挿入 / クロックスキューを調整</td></tr>
</table>
<h2>演習</h2>
<ol><li><code>CLK_PERIOD</code> を 1.0 にして最初から流す（<code>make clean all</code>）。どの段で最初に負の slack が出るか。</li>
<li><code>set_propagated_clock</code> の行を消して結果を比べる。何が変わるか、なぜか。</li></ol>
"""))

# ---------------------------------------------------------------- 08 gls
PAGES.append(("08-gls", "08 ゲートレベルシミュレーション", "遅延情報 (SDF) を使い、実際の遅延でテストをもう一度流す。", f"""
<p>STA は「すべての経路を見る」代わりに論理を見ません。ゲートレベルシミュレーション (GLS) は「<strong>テストした動作が、遅延込みで正しいか</strong>」を見ます。両方そろって安心できます。</p>
<p>ここでも <strong>Cadence Xcelium</strong> を使います（<code>xrun</code>）。</p>
{code("sim/run_gls.csh")}
<ul><li><strong>ネットリスト</strong>: 配置配線後のもの。</li>
<li><strong>セルのシミュレーションモデル</strong>: セルライブラリが提供する Verilog。</li>
<li><strong>SDF</strong>: 各セル・配線の遅延表（PrimeTime が出力）。<code>-sdf_cmd_file</code> で DUT のスコープに当てる。</li>
<li><strong>テストベンチ</strong>: RTL と同じもの。クロック周期だけ <code>+HALF</code> で変える。</li></ul>
{snippet("make gls"+NL+"== setup 2.0 ns: PASS: 400 cycles, no mismatch"+NL+"== hold  2.0 ns: PASS: 400 cycles, no mismatch")}
<h2>よく出る症状</h2>
<table>
<tr><th>症状</th><th>原因</th></tr>
<tr><td>出力が <code>x</code> のまま</td><td>リセット解除がクロックエッジに近すぎる（recovery/removal 違反）。または SDF のスコープ違い。</td></tr>
<tr><td>周期を縮めると不一致</td><td>setup 違反（本物）。STA の結果と照らし合わせる。</td></tr>
<tr><td>SDF 適用ログに大量の警告</td><td>階層名の不一致。<code>sdf_*.log</code> を確認。</td></tr>
</table>
{note("tip","どのSDFで流す？","遅いコーナーの SDF で setup、速いコーナーの SDF で hold を見ます。両方 PASS が望ましい。")}
<h2>演習</h2>
<ol><li><code>make gls</code> の周期を 2.0 → 1.0 に縮めて PASS/FAIL を観察する。</li>
<li>02章の演習（リセットを <code>#23</code> で解除）で、<code>x</code> が出る様子を確認する。</li></ol>
"""))

# ---------------------------------------------------------------- 09 phys verification
PAGES.append(("09-physical-verification", "09 物理検証 (DRC / LVS)", "製造ルールを守っているか、回路図と一致しているか。", f"""
<p>ツールは <strong>Siemens Calibre</strong> です。タイミングが通っても、<strong>製造できる形</strong>か、<strong>ネットリストどおりの回路</strong>かは別問題です。</p>
<h2>DRC (Design Rule Check)</h2>
<p>配線の幅・間隔・密度などの製造ルールを、GDS に対して検査します。</p>
{code("verif/run_drc.csh")}
<table>
<tr><th>見え方</th><th>意味</th></tr>
<tr><td>ルールごとの違反数</td><td><code>*.drc.summary</code> の <code>RULECHECK ... Result Count</code>。0 でないものを読む。</td></tr>
<tr><td><strong>チップ全体向けのルール</strong>（シールリング・境界）</td><td>単体ブロックでは必ず出る。フルチップで解消するため、ブロック段階では除外してよい。</td></tr>
<tr><td><strong>ダミーパターン／密度ルール</strong></td><td>フィルを入れるフェーズで解消する。ブロック単体では残ることが多い。</td></tr>
</table>
<p>この教材では、実際の配線の幾何ルール違反は<strong>無し</strong>で、残るのは密度・ダミー・チップ全体向けのルールです（一覧は <code>verif/drc/drc.nonzero.txt</code>）。</p>
<h2>LVS (Layout Versus Schematic)</h2>
<p>レイアウトからトランジスタと接続を取り出し、ネットリスト（回路図側）と照合します。</p>
{code("verif/run_lvs.csh")}
<ol><li>ネットリストをトランジスタ単位の SPICE に変換（セルの中身はライブラリの SPICE から）。</li>
<li>レイアウトを抽出し、<strong>デバイス数・ネット数・接続</strong>を照合。</li>
<li>レポートの先頭の <code>CORRECT / INCORRECT</code>、続いて <code>INITIAL NUMBERS OF OBJECTS</code>（レイアウトとソースの個数の比較）を見る。</li></ol>
<h3>レポートの読み方</h3>
<table>
<tr><th>見るところ</th><th>意味</th></tr>
<tr><td><code>OVERALL COMPARISON RESULTS</code></td><td><code>CORRECT</code> が合格</td></tr>
<tr><td><code>INITIAL NUMBERS OF OBJECTS</code></td><td>MOS トランジスタ数が一致しているか（デバイスは合っているのに接続が違う、など切り分けに使う）</td></tr>
<tr><td><code>INCORRECT NETS</code> / <code>INCORRECT INSTANCES</code></td><td>どのネット・素子で食い違うか</td></tr>
</table>
{snippet("make lvs"+NL+"...  CORRECT   MAC4   MAC4")}
<h3>実例: LVS が落ちた原因は電源だった</h3>
<p>このコースを作る途中で、LVS が <code>INCORRECT</code> になりました。調べ方は次のとおりです。</p>
<ol>
<li><code>INITIAL NUMBERS OF OBJECTS</code> を見ると、トランジスタ数は<strong>一致</strong>。部品は合っているので、接続の問題。</li>
<li>標準セル1個だけで LVS を実行すると <code>CORRECT</code>。セルの中は正しい。</li>
<li><code>INCORRECT INSTANCES</code> の中身を読むと、トランジスタの基板側（<code>b:</code>）が、回路図では <code>VDD</code>/<code>VSS</code> なのに、レイアウトでは名前のない別のネットになっている。</li>
<li>電源の配線データを調べると、<strong>標準セルの電源レールが、上位の電源ストラップにビアでつながっていないものがあった</strong>（ビアが設計ルールに引っかかって消えていた）。</li>
<li>ストラップを縦方向だけにし、ビアの形を選び直して再実行 → LVS <code>CORRECT</code>、DRC もルール違反なし。</li>
</ol>
{note("tip","学べること","電源が切れていても、タイミング解析（理想的な電源を仮定）と DRC は通ってしまいます。<strong>LVS だけが、配線のつながりを本当に確認する</strong>検査です。")}
{note("tip","ブロック単体とフルチップの違い","電源ピン・シールリング・IOなどがない単体ブロックでは、DRC/LVS 共に特有の違反・不一致が出ます。何がブロック単体の都合で、何が実際の問題かを区別するのが物理検証の腕の見せ所です。")}
<h2>演習</h2>
<ol><li><code>drc.nonzero.txt</code> に並ぶルールを、「配線の幾何」「密度・ダミー」「チップ全体」の3つに分類する。</li>
<li><code>icc2/icc2.tcl</code> のビア指定を一時的にこわして（例: ストラップの層を変える）再実行し、LVS がどう落ちるか、レポートの <code>INCORRECT NETS</code> を読む。</li></ol>
"""))

# ---------------------------------------------------------------- 10 pitfalls
PAGES.append(("10-pitfalls", "10 チェックリストとつまずき集", "signoff前に見る項目と、よくある失敗。", f"""
<h2>signoff 前チェックリスト</h2>
<ul class="check">
<li>RTL シミュレーションが PASS（テストは毎回自己チェック付き）</li>
<li>合成: <code>check_design</code> に警告なし、setup 違反なし</li>
<li>等価性検証（合成後）が PASS</li>
<li>配置配線: <code>check_routes</code> でオープン／ショート 0、CTS 後に hold 違反なし</li>
<li>寄生抽出が <code>Errors: 0</code>、PrimeTime で全ネットに寄生が付いている</li>
<li>STA: setup（遅いコーナー）・hold（速いコーナー）の両方で違反なし、<code>check_timing</code> に警告なし</li>
<li>GLS: SDF 付きで PASS</li>
<li>DRC: 幾何ルールの違反なし（除外理由を説明できる）</li>
<li>LVS: CORRECT（電源が全セルまで届いていることの確認にもなる）</li>
</ul>
<h2>つまずき集</h2>
<table>
<tr><th>症状</th><th>原因</th><th>対処</th></tr>
<tr><td>コマンドが見つからない</td><td>ツールの環境設定が読まれていない</td><td><code>config/local.csh</code> を確認</td></tr>
<tr><td>ライブラリが開けず落ちる</td><td>ツールの版とライブラリの作成版が合わない</td><td>ライブラリを作った版のツールで開く（抽出ツールも同じ版に揃える）</td></tr>
<tr><td>ネットリスト出力後に検証ツールで「セルが無い」</td><td>フィラーなど物理専用セルがネットリストに含まれる</td><td>検証用ネットリストの出力時に除外するか、モデルを用意</td></tr>
<tr><td>抽出が「層が定義されていない」</td><td>層対応表の名前の不一致</td><td>レイアウト側の層名を確認して対応表に書く</td></tr>
<tr><td>GLS で出力が <code>x</code></td><td>リセット解除がクロックエッジと重なる</td><td>クロックと違う位相で解除</td></tr>
<tr><td>STA の slack が ICC2 と違う</td><td>コーナー・RC・クロック設定の違い</td><td>どれが違うかを一つずつ揃えて比べる</td></tr>
<tr><td>LVS だけ落ちる（トランジスタ数は一致）</td><td>電源レールが電源網につながっていない</td><td>電源網のビアが全レールに付いたかを確認（<a href="05-pnr.html">05章</a>、<a href="09-physical-verification.html">09章</a>）</td></tr>
<tr><td>ポートが未配置という警告</td><td>電源ポートを作っていない</td><td>信号ピンは配置済みなら無視してよい。フルチップでは電源ピンを定義</td></tr>
</table>
<h2>もっと学ぶ</h2>
<ul><li>クロックゲーティング、DFT（スキャン）、電力解析、マルチコーナー・マルチモード、ECO。</li>
<li>演習として、<code>MAC4_LANE</code> に<strong>パイプライン段</strong>を追加して周期を 1.5 ns に縮め、全ステップをもう一度通す。</li></ul>
"""))


# ---------------------------------------------------------------- beginner intros and "how to run" boxes
def intro(title, body):
    return f'<section class="intro"><h2>はじめに: {title}</h2>{body}</section>'

def runbox(cmd, direct, inputs, outputs, ok, notes=""):
    return f"""<section class="run"><h2>実行方法</h2>
<table>
<tr><th>いちばん簡単</th><td><code>{cmd}</code>（リポジトリの最上位で実行）</td></tr>
<tr><th>直接実行</th><td><code>{direct}</code></td></tr>
<tr><th>入力</th><td>{inputs}</td></tr>
<tr><th>出力</th><td>{outputs}</td></tr>
<tr><th>成功の確認</th><td><code>{ok}</code></td></tr>
</table>{notes}</section>"""

INTROS = {}
RUNS = {}

INTROS["index"] = intro("デジタルチップはどうやって作るのか", """
<p>スマートフォンの中のCPUのようなデジタル回路は、人がトランジスタを一つずつ描いて作っているわけではありません。<strong>設計者はまず「何をする回路か」を文章のようなコード（RTL）で書き</strong>、あとはツールが段階的に、実際に製造できる図面（レイアウト）まで変換します。</p>
<p>この変換の各段で「ちゃんと元の設計どおりか」「速度は足りるか」「製造ルールを守っているか」を確かめる作業が必要で、それが <strong>signoff（サインオフ）</strong>です。signoff が全部通って初めて、レイアウトのデータ（GDS）を工場に渡せます。</p>
<p>このサイトでは、小さな回路を1つ用意して、この流れを最初から最後まで自分で動かします。</p>""")

INTROS["01-setup"] = intro("リポジトリとコマンドの基本", """
<p><strong>リポジトリ</strong>は、このコースのファイル一式を入れたフォルダです。回路（<code>rtl/</code>）、テスト（<code>tb/</code>）、各ツールの実行スクリプトが入っています。</p>
<p>ツールはすべて<strong>コマンドライン</strong>（黒い画面に文字を打つ方式）で動かします。実行したい内容は「スクリプト」というテキストファイルに書いてあり、<code>make</code> コマンドがそれらを順番に呼び出します。</p>
<p>なお、設計に使うツールとライブラリ（部品の一覧）は、研究室から提供されるものを使います。それらの場所は <code>config/</code> に書いて、スクリプトに教えます。</p>""")

RUNS["01-setup"] = f"""<section class="run"><h2>コマンド早見表</h2>
<table>
<tr><th>やりたいこと</th><th>コマンド</th><th>先に必要なもの</th></tr>
<tr><td>全部まとめて実行</td><td><code>make all</code></td><td>config の設定</td></tr>
<tr><td>RTLシミュレーション</td><td><code>make sim</code></td><td>なし</td></tr>
<tr><td>論理合成</td><td><code>make syn</code></td><td>なし</td></tr>
<tr><td>等価性検証</td><td><code>make fm</code></td><td><code>make syn</code></td></tr>
<tr><td>配置配線</td><td><code>make pnr</code></td><td><code>make syn</code></td></tr>
<tr><td>寄生抽出</td><td><code>make rcx</code></td><td><code>make pnr</code></td></tr>
<tr><td>signoff STA</td><td><code>make sta</code></td><td><code>make pnr rcx</code></td></tr>
<tr><td>ゲートレベルシミュレーション</td><td><code>make gls</code></td><td><code>make sta</code>（SDF を使うため）</td></tr>
<tr><td>DRC</td><td><code>make drc</code></td><td><code>make pnr</code></td></tr>
<tr><td>LVS</td><td><code>make lvs</code></td><td><code>make pnr</code></td></tr>
<tr><td>結果の画像（配置・クロック・電源・GDS）</td><td><code>python3 tools/render_layout.py</code></td><td><code>make pnr</code>、<code>config/render.json</code></td></tr>
<tr><td>生成物を消す</td><td><code>make clean</code></td><td>なし</td></tr>
</table>
<p>各ステップの詳しい実行方法・入出力・成功の確認は、各章の「実行方法」に書いてあります。</p></section>"""

INTROS["02-rtl-sim"] = intro("RTL とは、シミュレーションとは", """
<p><strong>RTL</strong>（Register Transfer Level）は、回路を<strong>「レジスタ（値を覚える部品）」と「レジスタ間で行う計算」</strong>で書く抽象度のことです。「クロックが1回来るたびに、この値とこの値を足して、このレジスタに入れる」といった動作を、Verilog という言語で書きます。</p>
<p>ソフトウェアのプログラムは上から順に実行されますが、<strong>ハードウェアの記述は「全部の部品が同時に動いている」</strong>様子を書いたものです。ここが最初に戸惑うところです。</p>
<p><strong>クロック</strong>は一定の間隔で打たれる合図で、レジスタはクロックの立ち上がりの瞬間にだけ新しい値を取り込みます。デジタル回路はこの合図に合わせて、一歩ずつ進みます。</p>
<p><strong>シミュレーション</strong>は、作った回路の動きをコンピュータ上で再現して確かめることです。<strong>テストベンチ</strong>は、回路に入力を与えて出力を確認する「テスト用の回路」で、実際のチップには入りません。</p>""")
RUNS["02-rtl-sim"] = runbox("make sim", "cd sim; csh run_rtl.csh",
  "<code>rtl/MAC4_LANE.v</code>, <code>rtl/MAC4.v</code>, <code>tb/tb_MAC4.v</code>",
  "<code>sim/rtl.log</code>（実行ログ）、<code>sim/wave.vcd</code>（波形データ）",
  "grep PASS sim/rtl.log   →   PASS: 400 cycles, no mismatch",
  """<ul><li>波形を見たいときは <code>wave.vcd</code> を波形ビューアで開きます（信号が時間とともにどう変わるか見られます）。</li>
<li>RTL を直したら、そのまま <code>make sim</code> をもう一度実行するだけです（毎回コンパイルからやり直します）。</li>
<li>スクリプトの中身: <code>xrun</code>（シミュレータ）に、RTL とテストベンチを渡しています。<code>-access +r</code> は信号を読める状態にする指定、<code>-define DUMP</code> は波形を出力する指定です。</li></ul>""")

INTROS["03-synthesis"] = intro("論理合成とは、制約とは", """
<p>RTL は「何をするか」を書いたもので、そのままでは実際の部品に対応していません。<strong>論理合成</strong>は、これを AND・OR・フリップフロップ（1ビットの記憶）といった<strong>基本部品（スタンダードセル）の接続表</strong>に変換する作業です。変換結果を<strong>ネットリスト</strong>と呼びます。</p>
<p>同じ RTL からでも、部品の選び方で回路は変わります。速くすれば面積が増え、小さくすれば遅くなります（トレードオフ）。そこで<strong>「どれくらいの速さを目指すか」を<em>制約（SDC）</em>として人が与え</strong>、ツールがそれを満たす最小の回路を探します。</p>
<p><strong>スタンダードセルのライブラリ</strong>は、部品の形・面積・遅延の一覧表です。合成ツールは、その遅延の値を使って「間に合うか」を計算します。</p>""")
RUNS["03-synthesis"] = runbox("make syn", "cd dc; dc_shell -f dc.tcl >& dc_run.log",
  "<code>rtl/*.v</code>, <code>const/MAC4.sdc</code>, セルのタイミングライブラリ（config で指定）",
  "<code>dc/MAC4.net.v</code>（ネットリスト）、<code>MAC4.ddc</code>、<code>MAC4.sdc</code>、<code>MAC4.sdf</code>、各種レポート <code>MAC4.*.log</code>",
  "grep slack dc/MAC4.max.timing.log | head -1   →   slack (MET)",
  """<ul><li>周期を変えて試すときは、<code>const/MAC4.sdc</code> の <code>CLK_PERIOD</code> を書き換えて、もう一度 <code>make syn</code>。</li>
<li>コーナーを変えるときは、環境変数 <code>CORNER</code> に wc / tc / bc を指定して直接実行します（例: <code>cd dc; env CORNER=tc dc_shell -f dc.tcl</code>）。</li>
<li>途中で止まったら <code>dc/dc_run.log</code> の <code>Error</code> を探します。</li></ul>""")

INTROS["04-formal"] = intro("等価性検証とは", """
<p>論理合成ツールは、回路を書き換えて最適化します。もしその過程で<strong>機能が変わってしまったら</strong>、後の工程で見つけるのはとても大変です。</p>
<p><strong>等価性検証</strong>は、書き換え前（RTL）と書き換え後（ネットリスト）が<strong>どんな入力でも同じ出力を返す</strong>ことを、数学的に確認します。シミュレーションが「入れた例では合っていた」ことしか言えないのに対し、「全部の場合で合っている」と言えるのが違いです。</p>""")
RUNS["04-formal"] = runbox("make fm", "cd fm; fm_shell -f fm.tcl >& fm_run.log",
  "<code>rtl/*.v</code>、<code>dc/MAC4.net.v</code>、<code>dc/MAC4.svf</code>（合成ツールの最適化の記録）",
  "<code>fm/fm_run.log</code>、<code>unmatched.log</code>、<code>failing.log</code>、<code>passing.log</code>",
  "grep \"FORMALITY RESULT\" fm/fm_run.log   →   FORMALITY RESULT: PASS",
  "<ul><li>先に <code>make syn</code> が済んでいる必要があります。</li><li>FAIL のときは <code>failing.log</code> に、等価でなかった場所が出ます。</li></ul>")

INTROS["05-pnr"] = intro("配置配線とは、クロックツリーとは", """
<p>ネットリストは「どの部品がどの部品につながるか」という<strong>接続表</strong>で、位置の情報がありません。<strong>配置配線</strong>（P&amp;R: Place and Route）は、これをチップの上に実際に並べ、金属の配線でつなぎます。</p>
<ul><li><strong>フロアプラン</strong>: チップ（ブロック）の大きさと、入出力端子の位置を決める。</li>
<li><strong>電源配線</strong>: すべての部品に電気を送る太い配線を張る。</li>
<li><strong>配置</strong>: 部品を並べる。つながりの多いものを近くに置くと配線が短くなります。</li>
<li><strong>クロックツリー合成 (CTS)</strong>: クロックを全レジスタに<strong>ほぼ同時に</strong>届けるための、バッファの木を作る。</li>
<li><strong>配線</strong>: 部品同士を金属でつなぐ。</li></ul>
<p>配線は長いほど遅くなるため、<strong>ここで初めて「実際の遅さ」が見えてきます</strong>。最終的に、工場に渡す図面データ <strong>GDS</strong> が出力されます。</p>""")
RUNS["05-pnr"] = runbox("make pnr", "cd icc2; icc2_shell -f icc2.tcl >& icc2_run.log",
  "<code>dc/MAC4.net.v</code>（ネットリスト）、<code>const/MAC4.sdc</code>、テクノロジ・セルのデータ（config で指定）",
  "<code>icc2/MAC4.gds</code>（レイアウト）、<code>MAC4.icc2.nopg.v</code>・<code>MAC4.icc2.lvs.v</code>（ネットリスト）、<code>MAC4.icc2.sdf</code>、<code>MAC4.def</code>、レポート",
  "grep -E \"^Error\" icc2/icc2_run.log   →   何も出なければ OK ／ grep \"slack (\" icc2/MAC4.cts.timing.log | head -1",
  """<ul><li>先に <code>make syn</code>。実行時間は1分半〜2分ほどです。</li>
<li>コアの大きさを変えるには、<code>icc2/icc2.tcl</code> の <code>core_width</code> / <code>core_height</code> を編集します。</li>
<li>実行のたびに <code>icc2/MAC4.ndm</code> を作り直します（古いものは自動で消えます）。</li></ul>""")

INTROS["06-extraction"] = intro("寄生抽出とは", """
<p>チップ上の配線は、理想的な「ただの線」ではありません。細い金属には<strong>抵抗 (R)</strong> があり、隣の配線や下地との間には<strong>容量 (C)</strong> があります。これらは信号を遅らせる原因で、<strong>寄生素子</strong>と呼ばれます。</p>
<p><strong>寄生抽出</strong>は、完成したレイアウトの形状から、この R と C の値を計算します。結果は <strong>SPEF</strong> というテキストファイルになり、次の signoff STA で使います。</p>""")
RUNS["06-extraction"] = runbox("make rcx", "cd rcx; csh run_starrc.csh",
  "<code>icc2/MAC4.ndm</code>（ICC2 のレイアウトデータ）、抽出用のテクノロジデータ・層対応表（config で指定）",
  "<code>rcx/MAC4.spef</code>、<code>rcx/starrc.log</code>",
  "grep -E \"ERROR\" rcx/starrc.log   →   何も出なければ OK ／ ls -l rcx/MAC4.spef",
  "<ul><li>先に <code>make pnr</code> が必要です。</li></ul>")

INTROS["07-sta"] = intro("signoff STA とは、setup と hold とは", """
<p><strong>STA</strong>（静的タイミング解析）は、シミュレーションを行わずに、<strong>回路内のすべての経路について「間に合うか」を計算</strong>する手法です。入力を考える必要がなく、漏れがありません。</p>
<p>レジスタからレジスタへのデータは、<strong>クロックの1周期のあいだに</strong>届かなければなりません。確認する条件は2つあります。</p>
<ul><li><strong>setup（セットアップ）</strong>: 次のクロックが来る<em>前</em>に、データが届いているか。遅すぎるとだめ。</li>
<li><strong>hold（ホールド）</strong>: クロックが来た<em>後</em>、データが変わるのが早すぎないか。早すぎるとだめ。</li></ul>
<p><strong>slack（スラック）</strong>は「余裕」のことで、<strong>0以上なら合格</strong>、マイナスなら違反です。signoff STA は、配線の抵抗・容量（SPEF）まで含めた<strong>最終判定</strong>です。</p>""")
RUNS["07-sta"] = runbox("make sta", "cd sta; env MODE=setup pt_shell -f pt.tcl   と   env MODE=hold pt_shell -f pt.tcl",
  "<code>icc2/MAC4.icc2.nopg.v</code>、<code>rcx/MAC4.spef</code>、<code>const/MAC4.sdc</code>、セルのタイミングライブラリ（config で指定）",
  "<code>sta/setup.*.log</code>、<code>sta/hold.*.log</code>、<code>MAC4.setup.sdf</code>、<code>MAC4.hold.sdf</code>（次章のシミュレーションで使う遅延ファイル）",
  "grep \"slack (\" sta/setup.max.log | head -1 ／ grep \"slack (\" sta/hold.min.log | head -1   →   どちらも slack (MET)",
  "<ul><li><code>make pnr rcx</code> が済んでいる必要があります。</li><li>setup と hold を別々に（別のコーナーで）実行するため、2回走ります。</li></ul>")

INTROS["08-gls"] = intro("ゲートレベルシミュレーションとは", """
<p>02章のシミュレーションは、遅延のない理想的な RTL で行いました。<strong>ゲートレベルシミュレーション (GLS)</strong> は、完成した回路（ネットリスト）に、<strong>実際の部品と配線の遅延</strong>を載せて、もう一度同じテストを流します。</p>
<p>遅延の情報は <strong>SDF</strong> というファイルに入っています。STA が「すべての経路が間に合うか」を見るのに対し、GLS は「テストした動作が、遅延込みで正しいか」を見ます。両方通れば、安心度が高まります。</p>""")
RUNS["08-gls"] = runbox("make gls", "cd sim; csh run_gls.csh setup 2.0   （使い方: csh run_gls.csh &lt;setup|hold&gt; &lt;周期ns&gt;）",
  "<code>icc2/MAC4.icc2.nopg.v</code>、<code>sta/MAC4.setup.sdf</code> または <code>MAC4.hold.sdf</code>、<code>tb/tb_MAC4.v</code>、セルのシミュレーションモデル（config で指定）",
  "<code>sim/gls_setup_2.0.log</code>、<code>sim/gls_hold_2.0.log</code> など",
  "grep -E \"PASS|FAIL\" sim/gls_setup_2.0.log   →   PASS: 400 cycles, no mismatch",
  """<ul><li>先に <code>make sta</code> で SDF を作ります。</li>
<li>引数1は <code>setup</code>（遅いコーナーの遅延）または <code>hold</code>（速いコーナー）、引数2はクロック周期[ns]です。例: <code>csh run_gls.csh hold 2.0</code>。</li>
<li>周期はテストベンチに <code>+HALF</code>（半周期）として渡されます。</li></ul>""")

INTROS["09-physical-verification"] = intro("DRC と LVS とは", """
<p>工場は、チップを作るときの<strong>守るべき寸法のルール</strong>（配線の最小幅・最小間隔など）を決めています。<strong>DRC</strong>（Design Rule Check）は、完成したレイアウトがそのルールに違反していないかを、図形のレベルで検査します。</p>
<p><strong>LVS</strong>（Layout Versus Schematic）は、レイアウトの図形からトランジスタとつながりを取り出し、<strong>回路図（ネットリスト）と同じ回路か</strong>を照合します。配線の誤接続などを発見できます。</p>
<p>タイミングが合っていても、製造ルール違反や接続ミスがあれば、チップは作れません。そのため、物理検証も signoff の一部です。</p>""")
RUNS["09-physical-verification"] = runbox("make drc   と   make lvs", "cd verif; csh run_drc.csh   と   csh run_lvs.csh",
  "<code>icc2/MAC4.gds</code>、<code>icc2/MAC4.icc2.lvs.v</code>（LVSのみ）、ルールデック（config で指定）",
  "<code>verif/drc/MAC4.drc.summary</code>、<code>verif/drc/drc.nonzero.txt</code>（違反のあるルール一覧）、<code>verif/lvs/MAC4.lvs.report</code>",
  "cat verif/drc/drc.nonzero.txt ／ grep -E \"CORRECT|INCORRECT\" verif/lvs/MAC4.lvs.report",
  "<ul><li>どちらも先に <code>make pnr</code>。DRC は1分ほどです。</li><li>DRC の結果は、ルール名ごとの違反数を読みます。0 でないものを分類してください。</li></ul>")

INTROS["10-pitfalls"] = ""
RUNS["10-pitfalls"] = ""

# ---------------------------------------------------------------- template
CSS = r"""
:root{--bg:#fbfbf9;--fg:#1c1f23;--muted:#5d6670;--line:#dde1e6;--accent:#0b5fff;--accent-soft:#e8f0ff;--code:#f2f4f7;--warn:#fff4e0;--warnb:#e0a030;--tip:#e8f6ee;--tipb:#2a9d5c;--nav:#f3f4f1}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14171a;--fg:#e7eaee;--muted:#9aa5b1;--line:#2b3138;--accent:#7aa7ff;--accent-soft:#1b2640;--code:#1d2228;--warn:#352a14;--warnb:#c58a22;--tip:#16301f;--tipb:#3fb878;--nav:#191d21}}
:root[data-theme=dark]{--bg:#14171a;--fg:#e7eaee;--muted:#9aa5b1;--line:#2b3138;--accent:#7aa7ff;--accent-soft:#1b2640;--code:#1d2228;--warn:#352a14;--warnb:#c58a22;--tip:#16301f;--tipb:#3fb878;--nav:#191d21}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.75 -apple-system,"Hiragino Sans","Noto Sans JP","Yu Gothic UI",system-ui,sans-serif}
a{color:var(--accent)}
.wrap{display:grid;grid-template-columns:250px minmax(0,1fr);max-width:1120px;margin:0 auto}
nav.side{position:sticky;top:0;align-self:start;height:100vh;overflow:auto;padding:24px 16px;background:var(--nav);border-right:1px solid var(--line)}
nav.side .brand{font-weight:700;margin:0 0 4px}nav.side .sub{font-size:13px;color:var(--muted);margin:0 0 18px}
nav.side a{display:block;padding:6px 10px;border-radius:8px;color:var(--fg);text-decoration:none;font-size:14.5px}
nav.side a:hover{background:var(--accent-soft)}nav.side a.cur{background:var(--accent-soft);color:var(--accent);font-weight:600}
main{padding:40px 36px 80px;min-width:0}
h1{font-size:32px;line-height:1.3;margin:0 0 6px}h2{font-size:22px;margin:42px 0 10px;padding-top:6px;border-top:1px solid var(--line)}h3{font-size:17px;margin:26px 0 6px}
.summary{color:var(--muted);margin:0 0 28px;font-size:17px}.lead{font-size:18px}
code{background:var(--code);padding:1px 6px;border-radius:5px;font:13.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
figure.code{margin:16px 0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--code)}
figure.code figcaption{font:12.5px ui-monospace,Menlo,monospace;color:var(--muted);padding:6px 12px;border-bottom:1px solid var(--line)}
figure.code pre{margin:0;padding:12px 14px;overflow:auto;max-height:520px}figure.code code{background:none;padding:0;font-size:13px;line-height:1.6;white-space:pre}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:15px;display:block;overflow-x:auto}th,td{border:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}th{background:var(--nav)}
aside.note{border-left:4px solid;border-radius:8px;padding:12px 16px;margin:18px 0}aside.note strong{display:block;margin-bottom:2px}
aside.tip{background:var(--tip);border-color:var(--tipb)}aside.warn{background:var(--warn);border-color:var(--warnb)}
ul.check{list-style:none;padding-left:0}ul.check li{padding:4px 0 4px 28px;position:relative}ul.check li:before{content:"☐";position:absolute;left:2px;color:var(--accent)}
svg.arch{width:100%;height:auto;margin:18px 0}svg.arch rect.top{fill:none;stroke:var(--line);stroke-width:1.4}svg.arch .lane rect,svg.arch .blk rect{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.2}svg.arch .calc rect{fill:var(--tip);stroke:var(--tipb);stroke-width:1.2}svg.arch .big rect{stroke-width:2}svg.arch text{fill:var(--fg);font-size:14px;text-anchor:middle}svg.arch text.s{font-size:11.5px;fill:var(--muted)}svg.arch text.l{text-anchor:start}svg.arch text.h{font-size:13px;font-weight:700;text-anchor:start}svg.arch path.arr{stroke:var(--muted);stroke-width:1.6;fill:none;marker-end:url(#ah)}svg.arch path.fb{stroke:var(--accent)}svg.arch path.ctl{stroke:var(--warnb);stroke-dasharray:5 4}figure.img{margin:20px 0}figure.img img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:10px;background:#fff}figure.img figcaption{font-size:14px;color:var(--muted);margin-top:6px}
svg.flow{width:100%;height:auto;margin:20px 0}svg.flow .n rect{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.2}svg.flow .n.hl rect{fill:var(--tip);stroke:var(--tipb)}
svg.flow text{fill:var(--fg);font-size:14px;text-anchor:middle}svg.flow text.s{font-size:11.5px;fill:var(--muted)}svg.flow path.a{stroke:var(--muted);stroke-width:1.5;fill:none;marker-end:url(#ar)}
.pager{display:flex;justify-content:space-between;gap:12px;margin-top:56px;padding-top:18px;border-top:1px solid var(--line)}
.pager a{text-decoration:none;border:1px solid var(--line);border-radius:10px;padding:10px 14px;max-width:48%}.pager a span{display:block;font-size:12px;color:var(--muted)}
section.intro{background:var(--accent-soft);border-radius:12px;padding:6px 22px 14px;margin:18px 0 26px}section.intro h2{border-top:0;margin-top:14px}
section.run{border:1px solid var(--line);border-radius:12px;padding:4px 20px 14px;margin:18px 0 8px}section.run h2{border-top:0;margin-top:12px}section.run th{width:7.5em;white-space:nowrap}
footer{margin-top:40px;color:var(--muted);font-size:13px}
@media(max-width:820px){.wrap{display:block}nav.side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}main{padding:24px 16px 60px}}
"""

def render(i, slug, title, summary, body):
    nav = "".join(f'<a href="{s}.html"{" class=cur" if s == slug else ""}>{html.escape(t)}</a>' for s, t, _, _ in PAGES)
    prev = f'<a href="{PAGES[i-1][0]}.html"><span>← 前へ</span>{html.escape(PAGES[i-1][1])}</a>' if i > 0 else "<span></span>"
    nxt = f'<a href="{PAGES[i+1][0]}.html" style="text-align:right"><span>次へ →</span>{html.escape(PAGES[i+1][1])}</a>' if i < len(PAGES) - 1 else "<span></span>"
    return f"""<!doctype html>
<html lang="ja"><head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-R6BS853MB3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-R6BS853MB3');
</script>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title) if slug == "index" else html.escape(title) + "｜デジタル論理合成入門"}</title><meta name="description" content="{html.escape(summary)}">
<link rel="stylesheet" href="style.css"></head><body><div class="wrap">
<nav class="side"><p class="brand">デジタル論理合成入門</p><p class="sub">RTL から signoff まで</p>{nav}</nav>
<main><h1>{html.escape(title)}</h1><p class="summary">{html.escape(summary)}</p>{INTROS.get(slug,"")}{RUNS.get(slug,"")}{body}
<div class="pager">{prev}{nxt}</div>
<footer>教材のソースコードは同じリポジトリにあります。環境依存の情報（ライブラリ・ルールデック・ツールの場所）は含まれていません。</footer></main></div></body></html>"""

(OUT / "style.css").write_text(CSS)
(OUT / ".nojekyll").write_text("")
for i, (slug, title, summary, body) in enumerate(PAGES):
    (OUT / f"{slug}.html").write_text(render(i, slug, title, summary, body))
print(f"wrote {len(PAGES)} pages to docs/")
