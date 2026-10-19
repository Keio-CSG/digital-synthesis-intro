#!/usr/bin/env python3
"""English version of the course website -> docs/en/.
Shares helpers, styles, figures and embedded repo files with build_site.py (Japanese).
Usage: python3 tools/build_site_en.py"""
import html, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as ja
from build_site import code, snippet, note, NL, CSS, ROOT

OUT = ROOT / "docs" / "en"
OUT.mkdir(parents=True, exist_ok=True)

def img(name, alt, cap):
    return f'<figure class="img"><img src="../img/{name}" alt="{html.escape(alt)}" loading="lazy"><figcaption>{html.escape(cap)}</figcaption></figure>'

def intro(title, body):
    return f'<section class="intro"><h2>Background: {title}</h2>{body}</section>'

def runbox(cmd, direct, inputs, outputs, ok, notes=""):
    return f"""<section class="run"><h2>How to run</h2>
<table>
<tr><th>Easiest</th><td><code>{cmd}</code> (from the top of the repository)</td></tr>
<tr><th>Directly</th><td><code>{direct}</code></td></tr>
<tr><th>Inputs</th><td>{inputs}</td></tr>
<tr><th>Outputs</th><td>{outputs}</td></tr>
<tr><th>Check success</th><td><code>{ok}</code></td></tr>
</table>{notes}</section>"""

def translate_svg(svg, table):
    for a, b in table.items():
        assert a in svg, a
        svg = svg.replace(a, b)
    return svg

FLOW_SVG = translate_svg(ja.FLOW_SVG, {
    'aria-label="RTLからsignoffまでのフロー"': 'aria-label="Flow from RTL to signoff"',
    "02 シミュレーション": "02 Simulation", "論理合成": "Synthesis", "03 DC": "03 DC",
    "等価性検証": "Equivalence", "04 Formality": "04 Formality", "配置配線": "Place &amp; route",
    "05 P&amp;R": "05 P&amp;R", "寄生抽出": "Extraction", "06 StarRC": "06 StarRC",
    "signoff STA": "Signoff STA", "07 PrimeTime": "07 PrimeTime", "SDF付き GLS": "Gate-level sim",
    "08 論理シミュレーション": "08 with SDF delays", "DRC / LVS": "DRC / LVS", "09 物理検証": "09 Physical check",
    "テープアウト": "Tape-out", "GDS を渡す": "hand over GDS", "ネットリスト・GDS・SPEF・SDF": "netlist, GDS, SPEF, SDF",
})
ARCH_SVG = translate_svg(ja.ARCH_SVG, {
    'aria-label="MAC4 のアーキテクチャ図"': 'aria-label="MAC4 architecture"',
    "MAC4（トップ）": "MAC4 (top level)", "共通の入力: clk, rst_n, clr, en": "Shared inputs: clk, rst_n, clr, en",
    "各レーンは同じ回路（MAC4_LANE）": "Every lane is the same circuit (MAC4_LANE)",
    "1レーン（MAC4_LANE）の中身": "Inside one lane (MAC4_LANE)",
    "4bit レジスタ": "4-bit register", "制御レジスタ": "control registers",
    "乗算": "multiply", "4bit × 4bit": "4 bit × 4 bit", "→ 8bit": "→ 8 bit",
    "加算": "add", "acc + 積": "acc + product", "12bit レジスタ": "12-bit register", "12bit": "12 bit", "= 出力 acc": "= output acc",
    "前の値に足し込む（フィードバック）": "add to the previous value (feedback)",
    "clr_q = 1 でゼロに戻す / en_q = 1 のときだけ更新": "clr_q = 1 resets to zero / update only when en_q = 1",
    "入力 a, b, en, clr（1クロック遅れて取り込み）": "inputs a, b, en, clr (captured one clock later)",
    "すべてのレジスタは同じクロック clk で動く。rst_n（非同期リセット）で 0 に戻る。": "All registers run on the same clock clk. rst_n (asynchronous reset) clears them to 0.",
})

PAGES, INTROS, RUNS = [], {}, {}

# ================================================================ index
PAGES.append(("index", "Introduction to Digital Logic Synthesis", "Go from RTL to signoff with a repository that really runs.", f"""
<p class="lead">Logic synthesis (RTL → gates) is only the beginning. In this course you take a small circuit through <strong>place and route, parasitic extraction, signoff timing, gate-level simulation and physical verification</strong>. Every step runs with one command, and you learn how to read its logs.</p>
{FLOW_SVG}
{img("layout.png","Final layout","What you end up with: the layout (GDS) after place and route. Colours are metal layers; the thick vertical lines are power.")}
<h2>Tools used</h2>
<table>
<tr><th>Step</th><th>Tool</th></tr>
<tr><td>RTL and gate-level simulation</td><td>Cadence Xcelium</td></tr>
<tr><td>Logic synthesis</td><td>Synopsys Design Compiler (<code>dc_shell</code>)</td></tr>
<tr><td>Equivalence checking</td><td>Synopsys Formality (<code>fm_shell</code>)</td></tr>
<tr><td>Place and route</td><td>Synopsys IC Compiler II (<code>icc2_shell</code>)</td></tr>
<tr><td>Parasitic extraction</td><td>Synopsys StarRC (<code>StarXtract</code>)</td></tr>
<tr><td>Signoff STA</td><td>Synopsys PrimeTime (<code>pt_shell</code>)</td></tr>
<tr><td>DRC / LVS</td><td>Siemens Calibre</td></tr>
</table>
<h2>Questions you will be able to answer</h2>
<table>
<tr><th>Step</th><th>Question</th><th>Input → output</th></tr>
<tr><td><a href="02-rtl-sim.html">02 RTL simulation</a></td><td>Does the RTL behave as specified?</td><td>RTL, testbench → PASS/FAIL (Xcelium)</td></tr>
<tr><td><a href="03-synthesis.html">03 Synthesis</a></td><td>Can it become gates that meet the target speed?</td><td>RTL, SDC → netlist (Design Compiler)</td></tr>
<tr><td><a href="04-formal.html">04 Equivalence checking</a></td><td>Is the logic unchanged by synthesis?</td><td>RTL, netlist → equivalent / not (Formality)</td></tr>
<tr><td><a href="05-pnr.html">05 Place and route</a></td><td>Can it become a real layout, clock tree included?</td><td>netlist → GDS (IC Compiler II)</td></tr>
<tr><td><a href="06-extraction.html">06 Parasitic extraction</a></td><td>What are the resistance and capacitance of the wires?</td><td>layout → SPEF (StarRC)</td></tr>
<tr><td><a href="07-sta.html">07 Signoff STA</a></td><td>Are setup and hold met at every corner?</td><td>netlist, SPEF, SDC → slack (PrimeTime)</td></tr>
<tr><td><a href="08-gls.html">08 Gate-level simulation</a></td><td>Does it still work with real delays?</td><td>netlist, SDF → PASS/FAIL (Xcelium)</td></tr>
<tr><td><a href="09-physical-verification.html">09 Physical verification</a></td><td>Does it follow the manufacturing rules and match the netlist?</td><td>GDS → DRC/LVS reports (Calibre)</td></tr>
</table>
{note("tip","How to proceed","Prepare the repository in <a href='01-setup.html'>01 Setup</a>, run <code>make all</code> once, then read each chapter with its logs open. Every chapter ends with exercises.")}
{note("warn","About this site","Process-specific files (libraries, rule decks, tool locations) are not included. Each lab or person provides them and puts them in <code>config/</code> (see <a href='01-setup.html'>01 Setup</a>).")}
"""))
INTROS["index"] = intro("how is a digital chip made?", """
<p>The CPU in a phone is not drawn transistor by transistor. <strong>A designer first describes what the circuit should do in a text-like code (RTL)</strong>, and tools then convert it step by step into a drawing that a factory can manufacture (the layout).</p>
<p>After each conversion we have to check that the result still matches the original design, is fast enough, and obeys the manufacturing rules. This checking is called <strong>signoff</strong>. Only when all of it passes can the layout data (GDS) be sent to the factory.</p>
<p>On this site you run the whole flow yourself on one small circuit.</p>""")
PAGES[-1] = PAGES[-1]

# ================================================================ 01
PAGES.append(("01-setup", "01 Setup", "Repository layout, and how environment-specific files are kept apart.", f"""
<p>This repository keeps <strong>everything that depends on your environment inside <code>config/</code></strong>. The scripts themselves contain no paths and no library names.</p>
<h2>Directory layout</h2>
{snippet('''
rtl/      RTL (MAC4_LANE.v = one lane, MAC4.v = four-lane top)
tb/       self-checking testbench
const/    SDC (shared by DC, ICC2 and PrimeTime)
sim/      RTL simulation / gate-level simulation
dc/       synthesis       fm/   equivalence checking
icc2/     place and route rcx/  parasitic extraction
sta/      signoff STA     verif/ DRC and LVS
config/   environment-specific files (copy the local.example.* ones)
docs/     this website (generated by tools/build_site.py)
Makefile  make all runs every step
''')}
<h2>Steps</h2>
<ol>
<li>Get the repository (<code>git clone https://github.com/Keio-CSG/digital-synthesis-intro.git</code>).</li>
<li><strong>Lab members copy the ready-made config.</strong> On the lab server it is kept in the folder below (if you cannot open it, ask your supervisor or a senior student).
{snippet('''
csh tools/setup_config.csh /home/ylab/yoshioka/digital-synthesis-intro-config
make sim            # if this works, the setup is fine
''')}
The six files that <code>config/</code> needs are copied. Existing files are saved as <code>.bak</code>.</li>
<li><strong>Everyone else</strong> copies the <code>*.example.*</code> files in <code>config/</code> and fills in the values for their own environment.
{snippet('''
cp config/local.example.csh          config/local.csh           # tool setup and library file locations
cp config/tech.example.tcl           config/tech.tcl            # metal layer names and routing directions
cp config/starrc_layer.example.map   config/starrc_layer.map    # layout layer names -> extraction layer names
cp config/prep_drc.example.csh       config/prep_drc.csh        # DRC deck preparation
cp config/prep_lvs.example.csh       config/prep_lvs.csh        # LVS deck preparation
cp config/render.example.json        config/render.json         # for the pictures (GDS layer numbers etc.)
''')}
These files are listed in <code>.gitignore</code> and are <strong>never committed</strong>.</li>
<li>Run everything.
{snippet('''
make all            # sim → syn → fm → pnr → rcx → sta → gls → drc → lvs
make clean          # remove all generated files
''')}
</li>
</ol>
{note("tip","Running one step","Name the step: <code>make syn</code>. If the upstream steps have not been run yet, run them first (for example <code>make sta</code> needs <code>make pnr rcx</code>).")}
<h2>Variables in config/local.csh (names only)</h2>
<table>
<tr><th>Variable</th><th>Meaning</th></tr>
<tr><td><code>STD_DB_WC / TC / BC</code></td><td>Standard-cell timing libraries (slow / typical / fast corner)</td></tr>
<tr><td><code>STD_NDM</code>, <code>STD_LIBNAME</code></td><td>Cell library for ICC2</td></tr>
<tr><td><code>TECH_FILE</code>, <code>TLUP_*</code>, <code>LAYER_MAP</code></td><td>Technology file and RC models</td></tr>
<tr><td><code>GDS_LAYER_MAP</code>, <code>STD_GDS</code></td><td>Layer map for GDS output; GDS of the cells</td></tr>
<tr><td><code>STD_VERILOG</code>, <code>STD_CDL</code></td><td>Simulation models for gate-level simulation; SPICE for LVS</td></tr>
<tr><td><code>FILLER_CELLS</code></td><td>Filler cell names (largest first)</td></tr>
<tr><td><code>DRC_DECK</code>, <code>LVS_DECK</code></td><td>Rule decks for physical verification</td></tr>
</table>
"""))
INTROS["01-setup"] = intro("repository and command-line basics", """
<p>A <strong>repository</strong> is a folder that holds all the files of this course: the circuit (<code>rtl/</code>), the test (<code>tb/</code>) and the run scripts for each tool.</p>
<p>All tools are used from the <strong>command line</strong> (typing in a terminal). What each tool should do is written in a <strong>script</strong>, a text file, and the <code>make</code> command calls those scripts in order.</p>
<p>The tools and the libraries (the catalogue of parts) are the ones your lab provides. Their locations are written in <code>config/</code>, which tells the scripts where to look.</p>""")
RUNS["01-setup"] = """<section class="run"><h2>Command cheat sheet</h2>
<table>
<tr><th>What you want</th><th>Command</th><th>Needs first</th></tr>
<tr><td>Run everything</td><td><code>make all</code></td><td>config set up</td></tr>
<tr><td>RTL simulation</td><td><code>make sim</code></td><td>nothing</td></tr>
<tr><td>Logic synthesis</td><td><code>make syn</code></td><td>nothing</td></tr>
<tr><td>Equivalence checking</td><td><code>make fm</code></td><td><code>make syn</code></td></tr>
<tr><td>Place and route</td><td><code>make pnr</code></td><td><code>make syn</code></td></tr>
<tr><td>Parasitic extraction</td><td><code>make rcx</code></td><td><code>make pnr</code></td></tr>
<tr><td>Signoff STA</td><td><code>make sta</code></td><td><code>make pnr rcx</code></td></tr>
<tr><td>Gate-level simulation</td><td><code>make gls</code></td><td><code>make sta</code> (it provides the SDF)</td></tr>
<tr><td>DRC</td><td><code>make drc</code></td><td><code>make pnr</code></td></tr>
<tr><td>LVS</td><td><code>make lvs</code></td><td><code>make pnr</code></td></tr>
<tr><td>Pictures of the result (placement, clock, power, GDS)</td><td><code>python3 tools/render_layout.py</code></td><td><code>make pnr</code>, <code>config/render.json</code></td></tr>
<tr><td>Delete generated files</td><td><code>make clean</code></td><td>nothing</td></tr>
</table>
<p>Each chapter has a "How to run" box with the inputs, outputs and how to check success for its step.</p></section>"""

# ================================================================ 02
PAGES.append(("02-rtl-sim", "02 RTL and Simulation", "The example MAC4 and a self-checking testbench.", f"""
<h2>Example: four-lane multiply-accumulate (MAC4)</h2>
<p>One lane <strong>multiplies two 4-bit numbers and adds the product to a 12-bit accumulator</strong>; its inputs are registered. Four lanes are placed side by side and share the clock and reset (about 90 flip-flops). It is small, yet <em>large enough to need a clock tree</em>.</p>
{ARCH_SVG}
<p>The left side is the top level with four lanes; the right side is the inside of one lane. Data flows <strong>input registers → multiply → add → accumulator</strong>, and the accumulator value is fed back into the next cycle's addition.</p>
{code("rtl/MAC4_LANE.v")}
{code("rtl/MAC4.v")}
<h2>Testbench</h2>
<p>Random inputs go to the DUT and to a <strong>behavioural model</strong> at the same time, and the outputs are compared every cycle. A PASS/FAIL result without looking at waveforms is important. The same testbench is reused for the gate-level simulation later.</p>
{code("tb/tb_MAC4.v", "    // reference model", "    `ifdef DUMP")}
{snippet("cd sim && csh run_rtl.csh"+NL+"# ..."+NL+"PASS: 400 cycles, no mismatch", "Run and expected output")}
{note("warn","Pitfall: when reset is released","If reset is released <strong>exactly on a clock edge</strong>, the gate-level model reports a recovery violation and the outputs become <code>X</code> (RTL does not show this). The testbench releases reset at <code>@(negedge clk)</code>.")}
<h2>Exercises</h2>
<ol><li>Change the accumulate in <code>MAC4_LANE.v</code> from <code>acc + a_q*b_q</code> to <code>acc + a_q+b_q</code> and confirm the test FAILs.</li>
<li>After <a href="08-gls.html">chapter 08</a>, change the reset release back to <code>#23 rst_n = 1;</code> and see what happens.</li></ol>
"""))
INTROS["02-rtl-sim"] = intro("what are RTL and simulation?", """
<p><strong>RTL</strong> (Register Transfer Level) is a level of abstraction where a circuit is written as <strong>"registers (parts that remember a value) and the calculations between them"</strong>. You write things like "at every clock, add these two values and store the result in this register" in a language called Verilog.</p>
<p>A software program runs from top to bottom, but <strong>a hardware description says "all the parts are working at the same time"</strong>. This is the first thing that confuses newcomers.</p>
<p>The <strong>clock</strong> is a signal ticking at a fixed interval. A register takes in a new value only at the rising edge of the clock. A digital circuit advances one step at a time to this beat.</p>
<p><strong>Simulation</strong> reproduces the behaviour of the circuit on a computer. A <strong>testbench</strong> is a "circuit for testing" that feeds inputs to your circuit and checks the outputs. It does not go into the real chip.</p>""")
RUNS["02-rtl-sim"] = runbox("make sim", "cd sim; csh run_rtl.csh",
  "<code>rtl/MAC4_LANE.v</code>, <code>rtl/MAC4.v</code>, <code>tb/tb_MAC4.v</code>",
  "<code>sim/rtl.log</code> (run log), <code>sim/wave.vcd</code> (waveform data)",
  "grep PASS sim/rtl.log   →   PASS: 400 cycles, no mismatch",
  """<ul><li>To look at waveforms, open <code>wave.vcd</code> in a waveform viewer (you can see how each signal changes over time).</li>
<li>After editing the RTL just run <code>make sim</code> again (it recompiles every time).</li>
<li>What the script does: it gives the RTL and the testbench to <code>xrun</code> (the simulator). <code>-access +r</code> makes signals readable and <code>-define DUMP</code> writes the waveform.</li></ul>""")

# ================================================================ 03
PAGES.append(("03-synthesis", "03 Logic Synthesis", "Set the goal with SDC and convert to gates with DC.", f"""
<p>Logic synthesis turns RTL into a connection of gates that <strong>meets the constraints</strong>. <strong>The constraints (SDC) are the specification</strong>: the same RTL gives a different circuit under different constraints.</p>
<h2>1. Constraints (SDC)</h2>
{code("const/MAC4.sdc")}
<table>
<tr><th>Command</th><th>Meaning</th></tr>
<tr><td><code>create_clock</code></td><td>Clock period = 2.0 ns (500 MHz). This is the target performance.</td></tr>
<tr><td><code>set_clock_uncertainty</code></td><td>Margin for skew and jitter. Larger for setup, smaller for hold.</td></tr>
<tr><td><code>set_input_delay / set_output_delay</code></td><td>Time used by the neighbouring blocks. The time left for an input/output path is the period minus the delay.</td></tr>
<tr><td><code>set_input_transition / set_load</code></td><td>Slope of the input waveform and the load on the outputs.</td></tr>
<tr><td><code>set_false_path -from rst_n</code></td><td>The asynchronous reset is not timed against the clock.</td></tr>
</table>
<h2>2. Flow of the synthesis script</h2>
{code("dc/dc.tcl", "# 1. read RTL", "# 4. outputs")}
<ul>
<li><code>analyze</code> → <code>elaborate</code> → <code>link</code>: read the RTL, connect the hierarchy and bind it to the cell library.</li>
<li><code>check_design</code>: any unconnected pins or multiple drivers? <strong>Always read the warnings.</strong></li>
<li><code>compile_ultra</code>: optimise the logic and map it to cells.</li>
</ul>
{note("tip","Which corner do we synthesise at?","The rule is: check setup (is it too slow?) at the <strong>slow corner</strong> and hold at the <strong>fast corner</strong>. This script switches with <code>CORNER=wc|tc|bc</code> (default: wc). When you quote a number, <strong>always state the corner</strong>.")}
<h2>3. How to read the reports</h2>
{snippet('''
Startpoint: acc_reg_1_   (rising edge-triggered flip-flop clocked by clk)
Endpoint:   acc_reg_9_
  data arrival time          ← time from the clock start until the data reaches the endpoint
  clock period               ← until the next clock
  - clock uncertainty
  - setup time               ← preparation time the flip-flop needs
  data required time
  slack (MET)  +0.xx         ← required − arrival. 0 or more is OK, negative is a violation''', "How to read report_timing (schematic)")}
<ul><li><code>MAC4.max.timing.log</code>: the tightest setup paths</li><li><code>MAC4.min.timing.log</code>: hold paths</li><li><code>MAC4.area.log</code>: area.</li><li><code>MAC4.qor.log</code>: overall summary.</li></ul>
{note("warn","Timing at this stage is <em>ideal</em>","There is no wire delay and no clock tree yet. Even with margin after synthesis, the slack shrinks after place and route. The signoff in <a href='07-sta.html'>chapter 07</a> is the final judge.")}
<h2>Exercises</h2>
<ol><li>Set <code>CLK_PERIOD</code> to 1.5 and run <code>make syn</code>. Does the slack become negative? How does the area change?</li>
<li>Compare <code>CORNER=tc</code> and <code>CORNER=wc</code> at the same period.</li>
<li>Remove <code>set_false_path</code>. What changes (look at the endpoints in <code>report_timing</code>)?</li></ol>
"""))
INTROS["03-synthesis"] = intro("what are logic synthesis and constraints?", """
<p>RTL says "what to do", but it does not correspond to real parts yet. <strong>Logic synthesis</strong> converts it into <strong>a connection table of basic parts (standard cells)</strong> such as AND, OR and flip-flops (1-bit memory). The result is called a <strong>netlist</strong>.</p>
<p>The same RTL can become different circuits depending on the parts chosen. Faster means larger, smaller means slower (a trade-off). So <strong>a person gives "how fast should it be" as <em>constraints (SDC)</em></strong>, and the tool looks for the smallest circuit that meets them.</p>
<p>The <strong>standard-cell library</strong> is a catalogue of the parts' shape, area and delay. The synthesis tool uses the delay values to calculate "will it make it in time?".</p>""")
RUNS["03-synthesis"] = runbox("make syn", "cd dc; dc_shell -f dc.tcl >& dc_run.log",
  "<code>rtl/*.v</code>, <code>const/MAC4.sdc</code>, the cell timing library (set in config)",
  "<code>dc/MAC4.net.v</code> (netlist), <code>MAC4.ddc</code>, <code>MAC4.sdc</code>, <code>MAC4.sdf</code>, reports <code>MAC4.*.log</code>",
  "grep slack dc/MAC4.max.timing.log | head -1   →   slack (MET)",
  """<ul><li>To try another period, edit <code>CLK_PERIOD</code> in <code>const/MAC4.sdc</code> and run <code>make syn</code> again.</li>
<li>To change the corner, set the environment variable <code>CORNER</code> to wc / tc / bc and run directly (for example <code>cd dc; env CORNER=tc dc_shell -f dc.tcl</code>).</li>
<li>If it stops midway, look for <code>Error</code> in <code>dc/dc_run.log</code>.</li></ul>""")

# ================================================================ 04
PAGES.append(("04-formal", "04 Equivalence Checking", "Prove that the synthesised netlist is logically equivalent to the RTL.", f"""
<p>Simulation can only show "it is correct for the inputs we tried". <strong>Formal equivalence checking</strong> shows mathematically that the outputs agree for <em>all inputs</em>.</p>
{code("fm/fm.tcl")}
<p>The tool is <strong>Synopsys Formality</strong> (<code>fm_shell</code>).</p>
<h2>Flow</h2>
<ol><li><strong>set_svf</strong>: pass the hints of the optimisations done by the synthesis tool (without them, things like state re-ordering often fail).</li>
<li><strong>reference</strong> = RTL, <strong>implementation</strong> = netlist (the cell functions are read from the library).</li>
<li><strong>match</strong>: pair up the registers and ports of both (create compare points).</li>
<li><strong>verify</strong>: prove, for each compare point, that the combinational logic is equivalent.</li></ol>
{snippet("make fm"+NL+"..."+NL+"FORMALITY RESULT: PASS")}
<h2>If it fails</h2>
<ul><li><code>unmatched.log</code>: points that could not be paired. Renamed or constant-propagated registers are typical.</li>
<li><code>failing.log</code>: points that were not equivalent. If something is here, <strong>the logic really changed</strong> (a synthesis bug, or a difference in how simulation and synthesis interpret the RTL).</li></ul>
{note("tip","When to use it","The standard practice is to run it after synthesis and again after place and route, because the tools touch the logic during physical implementation (buffer insertion, gate swapping and so on).")}
<h2>Exercise</h2>
<ol><li>Temporarily change <code>acc + a_q*b_q</code> in the RTL, change <strong>only the RTL</strong> and run <code>make fm</code> (the netlist stays old). Read the FAIL output.</li></ol>
"""))
INTROS["04-formal"] = intro("what is equivalence checking?", """
<p>A logic synthesis tool rewrites and optimises the circuit. If <strong>the function changed</strong> during this, it is very hard to find in later stages.</p>
<p><strong>Equivalence checking</strong> confirms mathematically that the circuit before the rewrite (RTL) and after it (netlist) <strong>return the same output for any input</strong>. Simulation can only say "it was right for the examples we tried"; this says "it is right in every case".</p>""")
RUNS["04-formal"] = runbox("make fm", "cd fm; fm_shell -f fm.tcl >& fm_run.log",
  "<code>rtl/*.v</code>, <code>dc/MAC4.net.v</code>, <code>dc/MAC4.svf</code> (record of the synthesis optimisations)",
  "<code>fm/fm_run.log</code>, <code>unmatched.log</code>, <code>failing.log</code>, <code>passing.log</code>",
  "grep \"FORMALITY RESULT\" fm/fm_run.log   →   FORMALITY RESULT: PASS",
  "<ul><li><code>make syn</code> must have been run first.</li><li>On FAIL, <code>failing.log</code> lists the places that were not equivalent.</li></ul>")

# ================================================================ 05
PAGES.append(("05-pnr", "05 Place and Route", "From floorplan to clock tree synthesis, routing and GDS output.", f"""
<p>The tool is <strong>Synopsys IC Compiler II</strong> (<code>icc2_shell</code>). It gives the netlist its <strong>real shape</strong>. Only with place and route do wire delay, the clock tree and the power grid appear.</p>
<h2>Overview of the steps</h2>
<ol>
<li><strong>Create the library and read the netlist</strong> (<code>create_lib</code>, <code>read_verilog</code>, <code>link_block</code>)</li>
<li><strong>RC models and scenario</strong>: parasitic models, and a scenario that reads the SDC (setup and hold are both analysed)</li>
<li><strong>Floorplan</strong>: core size and pin placement (<code>initialize_floorplan</code>, <code>place_pins</code>)</li>
<li><strong>Power grid</strong>: vertical power straps, the cell-row power rails and the vias between them (<code>create_pg_*</code>, <code>compile_pg</code>)</li>
<li><strong>Placement</strong>: <code>place_opt</code> places the cells and optimises while watching timing</li>
<li><strong>Clock tree synthesis + hold fixing</strong>: <code>clock_opt</code></li>
<li><strong>Routing</strong>: <code>route_auto</code>, <code>route_opt</code>, <code>check_routes</code></li>
<li><strong>Fillers</strong> fill the gaps</li>
<li><strong>Output</strong>: netlists (for verification), GDS, DEF, SDF</li></ol>
<h2>Floorplan</h2>
{code("icc2/icc2.tcl", "# --- floorplan parameters", "# --- multi-core")}
<p>Rule of thumb: total cell area ÷ target utilisation (about 50% here) ≈ core area. Too small and it cannot be routed; too large and the wires get long.</p>
<h2>Clock tree synthesis (CTS)</h2>
{code("icc2/icc2.tcl", "# 8. Placement", "# ============================================================================="+NL+"# 10.")}
<p>At placement time <strong>the clock is ideal</strong> (it reaches every flip-flop at the same moment). <code>clock_opt</code> builds a tree of clock buffers and evens out the arrival times at the flip-flops (the <strong>skew</strong>). At the same time it fixes <strong>hold violations</strong>, where data arrives too early, by inserting delay cells.</p>
{snippet('''
Clock   Sinks  Levels  Repeater  Latency  Skew
clk       88      2         3      ~0.06   ~0.01      ← cts.skew.log (icc2/)''', "Clock QoR after CTS (shape of the output)")}
{note("warn","With a tiny circuit, CTS does nothing","With about 20 flip-flops the clock port can drive them all directly and no buffers are inserted. This course uses four lanes so that you can see a tree being built.")}
<h2>Look at the result</h2>
<p>So that you can check the result without a layout viewer, there is a script that draws pictures from the GDS and DEF (<code>tools/render_layout.py</code>, run <code>python3 tools/render_layout.py</code>).</p>
{img("placement.png","Placement","Placement: cells are coloured by the four lanes. Dark cells are flip-flops, red ones are clock buffers. Cells of the same lane are placed together.")}
{img("clock_tree.png","Clock tree","Clock tree: red squares are clock buffers, blue lines are clock wires, black dots are the 88 flip-flops. One clock branches out and reaches them all.")}
{img("power_grid.png","Power grid","Power grid: horizontal lines are the standard-cell power rails (lowest metal), thick vertical lines are the power straps on a top metal. Red is VDD, blue is VSS. They are connected by vias where they cross.")}
{img("layout.png","Final layout","Final layout (GDS): cell outlines and the routing of each metal layer. This is the data handed to the factory.")}
<h2>What to look at in the reports</h2>
<table>
<tr><th>File</th><th>What to check</th></tr>
<tr><td><code>MAC4.pre_cts.timing.log</code></td><td>Setup before CTS (clock ideal)</td></tr>
<tr><td><code>MAC4.cts.timing.log</code></td><td>Setup after CTS (clock propagated). <strong>Wire delay is now included, so the slack shrinks</strong></td></tr>
<tr><td><code>MAC4.cts.hold.log</code></td><td>Hold after CTS. <strong>Before fixing it tends to be negative</strong></td></tr>
<tr><td><code>MAC4.cts.skew.log</code></td><td>Skew, latency and number of buffers</td></tr>
<tr><td><code>MAC4.check_routes.log</code></td><td>DRC / opens / shorts of the routing (should be 0)</td></tr>
</table>
{note("warn","Drawing power is not enough","If the power rails are not connected to the upper power straps by vias, timing and DRC still pass, <a href='09-physical-verification.html'>but only LVS fails</a>. Right after building the power grid, check that vias were added to every rail (in this course we really tripped over exactly this).")}
{note("tip","ICC2 results are provisional","The parasitic extraction inside ICC2 is simple. The final judgement is made in the following chapters with <strong>StarRC + PrimeTime</strong>.")}
<h2>Exercises</h2>
<ol><li>Widen <code>core_width</code> to 90 and run again. What happens to the wire length (Wire Length in <code>cts.skew.log</code>)?</li>
<li>Compare the setup slack before and after CTS and explain why it changes.</li></ol>
"""))
INTROS["05-pnr"] = intro("what are place and route and a clock tree?", """
<p>A netlist is a <strong>connection table</strong> saying which part connects to which; it has no position information. <strong>Place and route</strong> (P&amp;R) puts the parts on the chip and connects them with metal wires.</p>
<ul><li><strong>Floorplan</strong>: decide the size of the chip (block) and the positions of the pins.</li>
<li><strong>Power wiring</strong>: lay thick wires that bring electricity to every part.</li>
<li><strong>Placement</strong>: put the parts down. Parts that are strongly connected are placed close, which shortens wires.</li>
<li><strong>Clock tree synthesis (CTS)</strong>: build a tree of buffers that delivers the clock to all registers <strong>at almost the same time</strong>.</li>
<li><strong>Routing</strong>: connect the parts with metal.</li></ul>
<p>The longer a wire, the slower it is, so <strong>this is where the real speed first becomes visible</strong>. In the end, <strong>GDS</strong>, the drawing data to hand to the factory, is written out.</p>""")
RUNS["05-pnr"] = runbox("make pnr", "cd icc2; icc2_shell -f icc2.tcl >& icc2_run.log",
  "<code>dc/MAC4.net.v</code> (netlist), <code>const/MAC4.sdc</code>, technology and cell data (set in config)",
  "<code>icc2/MAC4.gds</code> (layout), <code>MAC4.icc2.nopg.v</code> and <code>MAC4.icc2.lvs.v</code> (netlists), <code>MAC4.icc2.sdf</code>, <code>MAC4.def</code>, reports",
  "grep -E \"^Error\" icc2/icc2_run.log   →   nothing printed is OK  /  grep \"slack (\" icc2/MAC4.cts.timing.log | head -1",
  """<ul><li>Run <code>make syn</code> first. It takes about one and a half to two minutes.</li>
<li>To change the core size, edit <code>core_width</code> / <code>core_height</code> in <code>icc2/icc2.tcl</code>.</li>
<li>Every run rebuilds <code>icc2/MAC4.ndm</code> (the old one is removed automatically).</li></ul>""")

# ================================================================ 06
PAGES.append(("06-extraction", "06 Parasitic Extraction", "Take the wire resistance and capacitance out of the layout and write them as SPEF.", f"""
<p>The tool is <strong>Synopsys StarRC</strong>. A wire is not "just a line": it has <strong>resistance R and capacitance C</strong>, and it is coupled to its neighbours by <strong>coupling capacitance</strong>. We extract these, collect them in a text file called <strong>SPEF</strong>, and give it to the STA tool.</p>
{code("rcx/run_starrc.csh")}
<h2>Inputs</h2>
<ul><li><strong>The layout</strong> (the ICC2 database): which metal belongs to which net.</li>
<li><strong>The technology (RC model)</strong>: extraction data built from the thickness of each layer, the dielectrics and so on.</li>
<li><strong>The layer map</strong> (<code>config/starrc_layer.map</code>): connects the layer names of the layout to the names in the extraction model. <em>If it is wrong, the run stops with "this layer is not defined".</em></li></ul>
<h2>What to check</h2>
<ul><li><code>Errors: 0</code> in <code>starrc.log</code>.</li>
<li>In PrimeTime, <code>report_annotated_parasitics</code>: <strong>did almost all nets get parasitics?</strong> A wire without parasitics is treated as ideal (zero delay), which makes timing look better than it is.</li>
<li>Are resistances present? (A too aggressive <code>REDUCTION</code> setting removes R.)</li></ul>
{note("tip","Corners","In real signoff you extract at a high-capacitance corner (for setup) and a low-capacitance corner (for hold). This course extracts at one corner and switches the corner on the delay-library side.")}
"""))
INTROS["06-extraction"] = intro("what is parasitic extraction?", """
<p>A wire on the chip is not an ideal "just a line". A thin metal wire has <strong>resistance (R)</strong>, and between neighbouring wires and the ground below there is <strong>capacitance (C)</strong>. These slow the signal down and are called <strong>parasitic elements</strong>.</p>
<p><strong>Parasitic extraction</strong> calculates these R and C values from the shapes of the finished layout. The result is a text file called <strong>SPEF</strong>, used by the signoff STA in the next chapter.</p>""")
RUNS["06-extraction"] = runbox("make rcx", "cd rcx; csh run_starrc.csh",
  "<code>icc2/MAC4.ndm</code> (ICC2 layout data), the technology data and layer map for extraction (set in config)",
  "<code>rcx/MAC4.spef</code>, <code>rcx/starrc.log</code>",
  "grep -E \"ERROR\" rcx/starrc.log   →   nothing printed is OK  /  ls -l rcx/MAC4.spef",
  "<ul><li><code>make pnr</code> must have been run first.</li></ul>")

# ================================================================ 07
PAGES.append(("07-sta", "07 Signoff STA", "With the real wire parasitics, check setup and hold, each at its worst corner.", f"""
<p>The tool is <strong>Synopsys PrimeTime</strong> (<code>pt_shell</code>). This is the <strong>final judgement</strong>. The timing in synthesis and ICC2 is only progress; whether you can tape out is decided by signoff static timing analysis.</p>
{code("sta/pt.tcl")}
<h2>Why run it twice?</h2>
<table>
<tr><th>Check</th><th>Worst when</th><th>Corner used</th></tr>
<tr><td><strong>setup</strong> (is the data too late?)</td><td>data slow, clock early</td><td><strong>slow corner</strong> (low voltage, high temperature)</td></tr>
<tr><td><strong>hold</strong> (is the data too early?)</td><td>data early, clock late</td><td><strong>fast corner</strong> (high voltage, low temperature)</td></tr>
</table>
<p>Even for the same circuit, delays change a lot with the operating condition. Run <code>MODE=setup</code> and <code>MODE=hold</code> separately.</p>
<h2>Key points of the script</h2>
<ul>
<li><code>read_verilog</code> + <code>link_design</code>: the netlist written by ICC2.</li>
<li><code>source const/MAC4.sdc</code>: <strong>the same SDC as synthesis</strong>. The constraints must not change along the way.</li>
<li><code>read_parasitics</code>: read the SPEF.</li>
<li><code>set_propagated_clock</code>: propagate the clock through its <strong>real paths</strong>.</li>
<li><code>check_timing</code>: gaps in the constraints (inputs without delay, registers the clock does not reach). <strong>Even with good slack, you cannot trust the result if there are warnings here</strong>.</li></ul>
<h2>Reading the result</h2>
{snippet('''
setup (slow corner):  report_timing -delay_type max  → slack +0.05 ns  (MET)
hold  (fast corner):  report_timing -delay_type min  → slack +0.01 ns  (MET)''', "Reference values for this course (corner stated)")}
<ul><li><code>*.max.log</code> / <code>*.min.log</code>: details of the worst paths (<code>-input_pins</code> shows the delay of every cell).</li>
<li><code>*.violators.log</code>: list of violations. It should be empty.</li>
<li><code>*.skew.log</code>: clock skew.</li>
<li><code>*.annotated.log</code>: the share of nets that got parasitics.</li>
<li><code>*.coverage.log</code>: how completely the paths were analysed.</li></ul>
{note("warn","A small hold slack is normal","Hold does not depend on the period; slowing the clock does not help. The only fix is <strong>inserting delay cells</strong>. That is why ICC2 fixes it at the CTS stage.")}
<h2>What to do on a violation</h2>
<table>
<tr><th>Violation</th><th>Remedy</th></tr>
<tr><td>setup</td><td>Lengthen the period / make the logic shallower (pipelining) / use cells with stronger drive / place things closer</td></tr>
<tr><td>hold</td><td>Insert delay cells / adjust the clock skew</td></tr>
</table>
<h2>Exercises</h2>
<ol><li>Set <code>CLK_PERIOD</code> to 1.0 and run from scratch (<code>make clean all</code>). At which step does a negative slack first appear?</li>
<li>Delete the <code>set_propagated_clock</code> line and compare the results. What changes, and why?</li></ol>
"""))
INTROS["07-sta"] = intro("what are signoff STA, setup and hold?", """
<p><strong>STA</strong> (static timing analysis) <strong>calculates, for every path in the circuit, "does it make it in time?"</strong> without running a simulation. You do not have to think up inputs, and nothing is missed.</p>
<p>Data going from one register to another has to arrive <strong>within one clock cycle</strong>. There are two conditions to check.</p>
<ul><li><strong>setup</strong>: has the data arrived <em>before</em> the next clock? Too late is bad.</li>
<li><strong>hold</strong>: after the clock, does the data change <em>too early</em>? Too early is bad.</li></ul>
<p><strong>slack</strong> is the margin: <strong>0 or more passes</strong>, negative is a violation. Signoff STA is the <strong>final judgement</strong> including the wire resistance and capacitance (SPEF).</p>""")
RUNS["07-sta"] = runbox("make sta", "cd sta; env MODE=setup pt_shell -f pt.tcl   and   env MODE=hold pt_shell -f pt.tcl",
  "<code>icc2/MAC4.icc2.nopg.v</code>, <code>rcx/MAC4.spef</code>, <code>const/MAC4.sdc</code>, the cell timing library (set in config)",
  "<code>sta/setup.*.log</code>, <code>sta/hold.*.log</code>, <code>MAC4.setup.sdf</code>, <code>MAC4.hold.sdf</code> (delay files used in the next chapter's simulation)",
  "grep \"slack (\" sta/setup.max.log | head -1  /  grep \"slack (\" sta/hold.min.log | head -1   →   both slack (MET)",
  "<ul><li><code>make pnr rcx</code> must have been run.</li><li>It runs twice because setup and hold are checked separately, at different corners.</li></ul>")

# ================================================================ 08
PAGES.append(("08-gls", "08 Gate-Level Simulation", "Use the delay information (SDF) and run the test again with real delays.", f"""
<p>STA looks at all paths but does not look at the logic. Gate-level simulation (GLS) checks that <strong>the behaviour you tested is correct with the delays included</strong>. You feel safe only when both agree.</p>
<p>The simulator is <strong>Cadence Xcelium</strong> again (<code>xrun</code>).</p>
{code("sim/run_gls.csh")}
<ul><li><strong>Netlist</strong>: the one after place and route.</li>
<li><strong>Simulation models of the cells</strong>: Verilog provided with the cell library.</li>
<li><strong>SDF</strong>: the delay table of every cell and wire (written by PrimeTime). It is applied to the DUT scope with <code>-sdf_cmd_file</code>.</li>
<li><strong>Testbench</strong>: the same as for RTL. Only the clock period is changed with <code>+HALF</code>.</li></ul>
{snippet("make gls"+NL+"== setup 2.0 ns: PASS: 400 cycles, no mismatch"+NL+"== hold  2.0 ns: PASS: 400 cycles, no mismatch")}
<h2>Common symptoms</h2>
<table>
<tr><th>Symptom</th><th>Cause</th></tr>
<tr><td>Outputs stay <code>x</code></td><td>Reset released too close to the clock edge (recovery/removal violation), or the wrong SDF scope.</td></tr>
<tr><td>Mismatch when the period is shortened</td><td>A setup violation (real). Compare with the STA result.</td></tr>
<tr><td>Many warnings when the SDF is applied</td><td>Hierarchy names do not match. Check <code>sdf_*.log</code>.</td></tr>
</table>
{note("tip","Which SDF to use?","Check setup with the SDF of the slow corner and hold with the SDF of the fast corner. Both should PASS.")}
<h2>Exercises</h2>
<ol><li>Shorten the period of <code>make gls</code> from 2.0 to 1.0 and watch PASS/FAIL.</li>
<li>With the exercise of chapter 02 (releasing reset at <code>#23</code>), see how <code>x</code> appears.</li></ol>
"""))
INTROS["08-gls"] = intro("what is gate-level simulation?", """
<p>The simulation in chapter 02 used ideal RTL without delays. <strong>Gate-level simulation (GLS)</strong> takes the finished circuit (the netlist), adds the <strong>real delays of parts and wires</strong>, and runs the same test again.</p>
<p>The delay information is in a file called <strong>SDF</strong>. STA asks "does every path make it in time?", while GLS asks "is the behaviour we tested correct with the delays?". If both pass, confidence is high.</p>""")
RUNS["08-gls"] = runbox("make gls", "cd sim; csh run_gls.csh setup 2.0   (usage: csh run_gls.csh &lt;setup|hold&gt; &lt;period in ns&gt;)",
  "<code>icc2/MAC4.icc2.nopg.v</code>, <code>sta/MAC4.setup.sdf</code> or <code>MAC4.hold.sdf</code>, <code>tb/tb_MAC4.v</code>, the cell simulation models (set in config)",
  "<code>sim/gls_setup_2.0.log</code>, <code>sim/gls_hold_2.0.log</code> and so on",
  "grep -E \"PASS|FAIL\" sim/gls_setup_2.0.log   →   PASS: 400 cycles, no mismatch",
  """<ul><li>Run <code>make sta</code> first to produce the SDF.</li>
<li>Argument 1 is <code>setup</code> (delays of the slow corner) or <code>hold</code> (fast corner); argument 2 is the clock period in ns. Example: <code>csh run_gls.csh hold 2.0</code>.</li>
<li>The period is passed to the testbench as <code>+HALF</code> (half period).</li></ul>""")

# ================================================================ 09
PAGES.append(("09-physical-verification", "09 Physical Verification (DRC / LVS)", "Does it follow the manufacturing rules, and does it match the netlist?", f"""
<p>The tool is <strong>Siemens Calibre</strong>. Even if timing is met, <strong>whether it can be manufactured</strong> and <strong>whether it is the circuit of the netlist</strong> are separate questions.</p>
<h2>DRC (Design Rule Check)</h2>
<p>It checks the GDS against manufacturing rules such as minimum wire width, spacing and density.</p>
{code("verif/run_drc.csh")}
<table>
<tr><th>What you see</th><th>Meaning</th></tr>
<tr><td>Violations per rule</td><td><code>RULECHECK ... Result Count</code> in <code>*.drc.summary</code>. Read the ones that are not 0.</td></tr>
<tr><td><strong>Rules meant for the whole chip</strong> (seal ring, boundary)</td><td>Always appear for a stand-alone block. They are resolved at full-chip level, so they may be excluded at block level.</td></tr>
<tr><td><strong>Dummy-pattern / density rules</strong></td><td>Resolved in the fill phase. They often remain on a stand-alone block.</td></tr>
</table>
<p>In this course there are <strong>no</strong> real geometric rule violations in the wiring; what remains are density, dummy and whole-chip rules (the list is in <code>verif/drc/drc.nonzero.txt</code>).</p>
<h2>LVS (Layout Versus Schematic)</h2>
<p>It extracts the transistors and connections from the layout and compares them with the netlist (the schematic side).</p>
{code("verif/run_lvs.csh")}
<ol><li>Convert the netlist to a transistor-level SPICE (the contents of the cells come from the library's SPICE).</li>
<li>Extract the layout and compare <strong>device counts, net counts and connections</strong>.</li>
<li>Read <code>CORRECT / INCORRECT</code> at the top of the report, then <code>INITIAL NUMBERS OF OBJECTS</code> (layout vs source counts).</li></ol>
<h3>How to read the report</h3>
<table>
<tr><th>Where</th><th>Meaning</th></tr>
<tr><td><code>OVERALL COMPARISON RESULTS</code></td><td><code>CORRECT</code> means pass</td></tr>
<tr><td><code>INITIAL NUMBERS OF OBJECTS</code></td><td>Do the MOS transistor counts match? (used to separate "devices match but connections differ")</td></tr>
<tr><td><code>INCORRECT NETS</code> / <code>INCORRECT INSTANCES</code></td><td>Which nets and devices disagree</td></tr>
</table>
{snippet("make lvs"+NL+"...  CORRECT   MAC4   MAC4")}
<h3>A real example: LVS failed because of power</h3>
<p>While building this course, LVS became <code>INCORRECT</code>. This is how it was investigated.</p>
<ol>
<li><code>INITIAL NUMBERS OF OBJECTS</code> showed that the transistor counts <strong>matched</strong>. The parts are right, so it is a connection problem.</li>
<li>LVS on a single standard cell gave <code>CORRECT</code>. The inside of the cell is fine.</li>
<li>Reading <code>INCORRECT INSTANCES</code>: the bulk side of the transistors (<code>b:</code>) was <code>VDD</code>/<code>VSS</code> in the schematic but an unnamed separate net in the layout.</li>
<li>Looking at the power wiring data: <strong>some standard-cell power rails were not connected to the upper power straps by vias</strong> (the vias had been deleted because they violated design rules).</li>
<li>Using vertical straps only and choosing the via shape again, then re-running: LVS <code>CORRECT</code>, and DRC shows no rule violation.</li>
</ol>
{note("tip","What you learn","Even with a broken power connection, timing analysis (which assumes ideal power) and DRC pass. <strong>Only LVS really checks that the wires are connected.</strong>")}
{note("tip","Block alone versus full chip","A stand-alone block without power pins, seal ring or I/O produces its own violations and mismatches in both DRC and LVS. Telling apart what is just a result of being a block and what is a real problem is the skill of physical verification.")}
<h2>Exercises</h2>
<ol><li>Classify the rules in <code>drc.nonzero.txt</code> into "wiring geometry", "density / dummy" and "whole chip".</li>
<li>Temporarily break the via specification in <code>icc2/icc2.tcl</code> (for example change the strap layer), run again, and read <code>INCORRECT NETS</code> to see how LVS fails.</li></ol>
"""))
INTROS["09-physical-verification"] = intro("what are DRC and LVS?", """
<p>The factory defines <strong>dimension rules that must be obeyed</strong> when making a chip (minimum wire width, minimum spacing and so on). <strong>DRC</strong> (Design Rule Check) checks, at the level of shapes, that the finished layout does not break these rules.</p>
<p><strong>LVS</strong> (Layout Versus Schematic) extracts the transistors and connections from the layout shapes and compares them with the schematic (the netlist) to see <strong>whether they are the same circuit</strong>. It can find wrong connections and the like.</p>
<p>Even with correct timing, a chip that breaks a manufacturing rule or has a wrong connection cannot be made. So physical verification is also part of signoff.</p>""")
RUNS["09-physical-verification"] = runbox("make drc   and   make lvs", "cd verif; csh run_drc.csh   and   csh run_lvs.csh",
  "<code>icc2/MAC4.gds</code>, <code>icc2/MAC4.icc2.lvs.v</code> (LVS only), the rule decks (set in config)",
  "<code>verif/drc/MAC4.drc.summary</code>, <code>verif/drc/drc.nonzero.txt</code> (rules with violations), <code>verif/lvs/MAC4.lvs.report</code>",
  "cat verif/drc/drc.nonzero.txt  /  grep -E \"CORRECT|INCORRECT\" verif/lvs/MAC4.lvs.report",
  "<ul><li>Run <code>make pnr</code> first for both. DRC takes about a minute.</li><li>Read the DRC result as violations per rule name. Classify the ones that are not 0.</li></ul>")

# ================================================================ 10
PAGES.append(("10-pitfalls", "10 Checklist and Common Pitfalls", "What to check before signoff, and common failures.", f"""
<h2>Checklist before signoff</h2>
<ul class="check">
<li>RTL simulation PASS (the test is self-checking every time)</li>
<li>Synthesis: no warnings in <code>check_design</code>, no setup violations</li>
<li>Equivalence checking (after synthesis) PASS</li>
<li>Place and route: 0 opens/shorts in <code>check_routes</code>, no hold violations after CTS</li>
<li>Extraction has <code>Errors: 0</code>, and every net has parasitics in PrimeTime</li>
<li>STA: no violations for setup (slow corner) and hold (fast corner), no warnings in <code>check_timing</code></li>
<li>GLS: PASS with SDF</li>
<li>DRC: no geometric rule violations (you can explain every exclusion)</li>
<li>LVS: CORRECT (it also confirms that power reaches every cell)</li>
</ul>
<h2>Common pitfalls</h2>
<table>
<tr><th>Symptom</th><th>Cause</th><th>Remedy</th></tr>
<tr><td>Command not found</td><td>The tool environment was not loaded</td><td>Check <code>config/local.csh</code></td></tr>
<tr><td>The library cannot be opened and the tool crashes</td><td>The tool version does not match the version that created the library</td><td>Open the library with the version that created it (use the same version for the extraction tool)</td></tr>
<tr><td>"Cell not found" in a verification tool after netlist output</td><td>Physical-only cells such as fillers are in the netlist</td><td>Exclude them when writing the verification netlist, or provide models</td></tr>
<tr><td>Extraction says "layer not defined"</td><td>Names in the layer map do not match</td><td>Check the layer names of the layout and write them in the map</td></tr>
<tr><td>GLS outputs are <code>x</code></td><td>Reset release overlaps the clock edge</td><td>Release reset at a different clock phase</td></tr>
<tr><td>STA slack differs from ICC2</td><td>Different corner, RC or clock settings</td><td>Align them one by one and compare</td></tr>
<tr><td>Only LVS fails (transistor counts match)</td><td>Power rails are not connected to the power grid</td><td>Check that the vias of the power grid reach every rail (<a href="05-pnr.html">chapter 05</a>, <a href="09-physical-verification.html">chapter 09</a>)</td></tr>
<tr><td>Warning that ports are unplaced</td><td>Power ports were not created</td><td>If the signal pins are placed you can ignore it. For a full chip, define the power pins</td></tr>
</table>
<h2>Going further</h2>
<ul><li>Clock gating, DFT (scan), power analysis, multi-corner multi-mode, ECO.</li>
<li>As an exercise, add a <strong>pipeline stage</strong> to <code>MAC4_LANE</code>, shorten the period to 1.5 ns and run all steps again.</li></ul>
"""))

# ================================================================ render
LABELS = dict(brand="Introduction to Digital Logic Synthesis", sub="From RTL to signoff", prev="← Previous", nxt="Next →",
              foot="The source code of this course is in the same repository. No environment-specific information (libraries, rule decks, tool locations) is included.")
def render(i, slug, title, summary, body):
    nav = "".join(f'<a href="{s}.html"{" class=cur" if s == slug else ""}>{html.escape(t)}</a>' for s, t, _, _ in PAGES)
    prev = f'<a href="{PAGES[i-1][0]}.html"><span>{LABELS["prev"]}</span>{html.escape(PAGES[i-1][1])}</a>' if i > 0 else "<span></span>"
    nxt = f'<a href="{PAGES[i+1][0]}.html" style="text-align:right"><span>{LABELS["nxt"]}</span>{html.escape(PAGES[i+1][1])}</a>' if i < len(PAGES) - 1 else "<span></span>"
    ttl = html.escape(title) if slug == "index" else html.escape(title) + " | Digital Logic Synthesis"
    return f"""<!doctype html>
<html lang="en"><head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-R6BS853MB3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-R6BS853MB3');
</script>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{ttl}</title><meta name="description" content="{html.escape(summary)}">
<link rel="stylesheet" href="../style.css"></head><body><div class="wrap">
<nav class="side"><p class="brand">{LABELS["brand"]}</p><p class="sub">{LABELS["sub"]}</p>{nav}<p class="lang"><a href="../{slug}.html" hreflang="ja">日本語</a></p></nav>
<main><h1>{html.escape(title)}</h1><p class="summary">{html.escape(summary)}</p>{INTROS.get(slug,"")}{RUNS.get(slug,"")}{body}
<div class="pager">{prev}{nxt}</div>
<footer>{LABELS["foot"]}</footer></main></div></body></html>"""

if __name__ == "__main__":
    assert [p[0] for p in PAGES] == [p[0] for p in ja.PAGES], "page lists differ"
    for i, (slug, title, summary, body) in enumerate(PAGES):
        (OUT / f"{slug}.html").write_text(render(i, slug, title, summary, body))
    print(f"wrote {len(PAGES)} pages to docs/en/")
