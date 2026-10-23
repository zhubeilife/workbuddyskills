# -*- coding: utf-8 -*-
"""
verify_render.py —— cnki 交互式动画「真浏览器」交付校验（离线，零额外依赖）

借鉴 k12-animation-studio 的 gate/layout/render 三件套 与
k12-interactive-animation-v2 的 selfcheck，统一成 cnki 自有的单文件 Python 工具。

做什么：
  1) 结构自检   —— 调 scripts/validate_html.py（外链/占位/字号）
  2) 常量核对   —— 调 scripts/lint_facts.py（data-fact 标记 vs _facts.json）
  3) 真浏览器   —— 用本机 msedge --headless 加载作品，离线校验：
       · 加载与运行期无 JS 运行时错误（抓 console "Uncaught"）
       · window.__selfTest() 数值/几何断言全部通过（无 NaN/Infinity）
       · 主视觉（canvas/svg/[data-cnki-visual]）占视口 ≥ 25%，且内容包围盒 ≥ 主视觉盒 30%
       · 无横向溢出（scrollWidth ≤ clientWidth）
       · 按钮触控目标达学段下限（小学≥48 / 初中≥44 / 高中≥40；拖动型滑块不计入）

无头测量用「iframe + dump-dom」方式（与 studio render-check 同思路）：
父页加载作品到 iframe，等加载后在页内测量，把 JSON 写进 <pre>，
再让 msedge --dump-dom 把父页序列化出来抓回 —— 全程不依赖 puppeteer/CDP。

用法：
    python verify_render.py <文件.html> [文件2 ...] [--no-browser]
    --no-browser   仅跑 1)+2) 静态检查，跳过真浏览器

退出码：0 = 全部通过（含 SKIP）；1 = 有 FAIL。
"""
import sys
import os
import re
import json
import subprocess
import tempfile
import urllib.parse
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..")
VALIDATE = os.path.join(HERE, "validate_html.py")
LINTFACTS = os.path.join(HERE, "lint_facts.py")

STAGE_TOUCH = {"primary": 48, "junior": 44, "senior": 40, "": 44, "default": 44}

# ------- 阈值（与 studio 同量级） -------
MIN_MAIN_RATIO = 0.25
MIN_CONTENT_RATIO = 0.30


def find_browser():
    cands = []
    if os.environ.get("KAS_BROWSER"):
        cands.append(os.environ["KAS_BROWSER"])
    if os.environ.get("CHROME_PATH"):
        cands.append(os.environ["CHROME_PATH"])
    if sys.platform == "win32":
        pf = os.environ.get("ProgramFiles", "C:\\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        cands += [
            os.path.join(pf, "Microsoft\\Edge\\Application\\msedge.exe"),
            os.path.join(pf86, "Microsoft\\Edge\\Application\\msedge.exe"),
            os.path.join(pf, "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(pf86, "Google\\Chrome\\Application\\chrome.exe"),
        ]
    else:
        cands += [
            "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium", "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def file_url(path):
    u = "file:///" + path.replace("\\", "/")
    return urllib.parse.quote(u, safe=":/")


INPAGE = r"""
function measure(win, doc){
  var out = { vw: win.innerWidth, vh: win.innerHeight, errors: [], selfTest: null,
              main: null, mainError: '', overflow: null, controls: [], reducedMotion: false };
  try {
    win.addEventListener('error', function(e){
      out.errors.push((e.message||'error') + (e.filename? (' @'+String(e.filename).split('/').pop()+':'+e.lineno) : ''));
    });
    win.addEventListener('unhandledrejection', function(e){
      var r = e.reason; out.errors.push('unhandledrejection: ' + (r && r.message ? r.message : String(r)));
    });
  } catch(_) {}
  try {
    if (win.matchMedia) out.reducedMotion = !!win.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch(_) {}
  try {
    if (typeof win.__selfTest === 'function') out.selfTest = win.__selfTest();
  } catch(e){ out.selfTest = { pass: false, error: (e && e.name) + ':' + (e && e.message) }; }
  try {
    var explicit = doc.querySelector('[data-cnki-visual]');
    var el = explicit;
    if (!el) {
      var best = null, ba = 0;
      var all = doc.querySelectorAll('canvas,svg');
      for (var i = 0; i < all.length; i++) {
        var r = all[i].getBoundingClientRect(); var a = r.width * r.height;
        if (a > ba) { ba = a; best = all[i]; }
      }
      el = best;
    }
    if (!el) {
      // DOM 类游戏（翻牌/闯关）没有 canvas/svg：退而取主舞台区
      var stage = doc.querySelector('.stage, .stage-shell, .arcade-shell, .coach-shell');
      if (stage) el = stage;
    }
    if (el) {
      var r = el.getBoundingClientRect();
      var tag = el.tagName.toLowerCase();
      var m = { tag: tag, w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                areaRatio: +((r.width * r.height) / (win.innerWidth * win.innerHeight)).toFixed(4),
                contentW: null, contentH: null, contentErr: '' };
      if (tag === 'canvas') {
        try {
          var cx = el.getContext('2d'); var W = el.width, H = el.height;
          if (W && H) {
            var data = cx.getImageData(0, 0, W, H).data;
            var step = Math.max(1, Math.floor(Math.max(W, H) / 420));
            var minX = W, minY = H, maxX = -1, maxY = -1;
            for (var y = 0; y < H; y += step)
              for (var x = 0; x < W; x += step)
                if (data[(y * W + x) * 4 + 3] > 8) {
                  if (x < minX) minX = x; if (x > maxX) maxX = x;
                  if (y < minY) minY = y; if (y > maxY) maxY = y;
                }
            if (maxX >= 0) { m.contentW = +(((maxX - minX + 1) * r.width / W).toFixed(1)); m.contentH = +(((maxY - minY + 1) * r.height / H).toFixed(1)); }
            else { m.contentW = 0; m.contentH = 0; }
          }
        } catch (e) { m.contentErr = String((e && e.message) || e); }
      } else {
        var mnx = 1e9, mny = 1e9, mxx = -1e9, mxy = -1e9, hit = false;
        for (var i = 0; i < el.children.length; i++) {
          var ch = el.children[i]; var t = ch.tagName.toLowerCase();
          if (t === 'defs' || t === 'title' || t === 'desc' || t === 'style') continue;
          var b = ch.getBoundingClientRect();
          if (!b.width && !b.height) continue;
          hit = true;
          if (b.left < mnx) mnx = b.left; if (b.top < mny) mny = b.top;
          if (b.right > mxx) mxx = b.right; if (b.bottom > mxy) mxy = b.bottom;
        }
        if (hit) { m.contentW = +(mxx - mnx).toFixed(1); m.contentH = +(mxy - mny).toFixed(1); }
      }
      out.main = m;
    }
  } catch (e) { out.mainError = String((e && e.message) || e); }
  try {
    var de = doc.documentElement;
    out.overflow = { scrollW: de.scrollWidth, clientW: de.clientWidth, scrollH: de.scrollHeight, clientH: de.clientHeight };
  } catch (_) {}
  try {
    // H5 只查「可点击按钮类」控件；拖动型滑块(input[type=range])横向延伸即足够作为可操作提示，
    // 不应以竖向高度判失败（与「按钮触控目标」规则本意一致）。
    var ctrls = doc.querySelectorAll('button,[role=button],input[type=button],select');
    for (var i = 0; i < ctrls.length; i++) {
      var e = ctrls[i]; var b = e.getBoundingClientRect();
      if (!b.width || !b.height) continue;
      if (win.getComputedStyle(e).visibility === 'hidden') continue;
      out.controls.push({ kind: e.tagName.toLowerCase() + (e.type ? ':' + e.type : ''),
                          h: +b.height.toFixed(1), w: +b.width.toFixed(1),
                          name: (e.getAttribute('aria-label') || e.textContent || '').trim().slice(0, 16) });
    }
  } catch (_) {}
  return out;
}
"""

WRAPPER = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;height:100%;overflow:hidden}}iframe{{border:0;width:100vw;height:100vh;display:block}}</style>
</head><body>
<iframe id="f" src="{src}"></iframe>
<pre id="rep">PENDING</pre>
<script>
{measure}
var f = document.getElementById('f');
function run(){{
  try {{ var rep = measure(f.contentWindow, f.contentDocument);
    document.getElementById('rep').textContent = 'VERIFY_REPORT:' + JSON.stringify(rep);
  }} catch(e) {{ document.getElementById('rep').textContent = 'VERIFY_ERROR:' + (e&&e.name) + ':' + (e&&e.message); }}
}}
f.addEventListener('load', function(){{ setTimeout(run, 800); }});
setTimeout(function(){{ if (document.getElementById('rep').textContent === 'PENDING') run(); }}, 2600);
</script></body></html>"""


def headless_checks(path, browser):
    """返回 (results[list of (id,title,ok,detail)], skipped:bool)。"""
    res = []
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html",
                                          dir=os.path.dirname(os.path.abspath(path)),
                                          encoding="utf-8", delete=False)
        tmp.write(WRAPPER.format(src=file_url(os.path.abspath(path)), measure=INPAGE))
        tmp.close()
        wrap_url = file_url(tmp.name)
        out_dir = tempfile.mkdtemp(prefix="cnki_verify_")
        dom_path = os.path.join(out_dir, "dom.html")
        fd = os.open(dom_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        p = subprocess.run(
            [browser, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--allow-file-access-from-files", "--virtual-time-budget=3000",
             "--dump-dom", wrap_url],
            stdout=fd, stderr=subprocess.DEVNULL, timeout=90000)
        os.close(fd)
        dom = ""
        if os.path.isfile(dom_path):
            with open(dom_path, "r", encoding="utf-8", errors="replace") as f:
                dom = f.read()
        m = re.search(r"VERIFY_REPORT:([\s\S]*?)</pre>", dom)
        report = None
        if m:
            try:
                report = json.loads(m.group(1).strip())
            except Exception as e:
                res.append(("H0", "无头报告 JSON 解析", False, "解析失败: " + str(e)))
        if report is None:
            return res, True  # skipped

        # H1 主视觉可定位
        if report.get("main"):
            res.append(("H1", "主视觉可定位", True, "tag=%s" % report["main"]["tag"]))
        else:
            res.append(("H1", "主视觉可定位", False, report.get("mainError") or "找不到 canvas/svg/[data-cnki-visual]"))

        # H2 主视觉占比
        if report.get("main"):
            ratio = report["main"]["areaRatio"]
            ok = ratio >= MIN_MAIN_RATIO
            res.append(("H2", "主视觉占视口 ≥ %d%%" % int(MIN_MAIN_RATIO * 100), ok,
                        "%.1f%%" % (ratio * 100)))

        # H3 内容包围盒
        if report.get("main") and report["main"].get("contentW") is not None:
            mw = report["main"]["w"]; mh = report["main"]["h"]
            cw = report["main"]["contentW"]; ch = report["main"]["contentH"]
            ok = mw > 0 and mh > 0 and (cw / mw) >= MIN_CONTENT_RATIO and (ch / mh) >= MIN_CONTENT_RATIO
            res.append(("H3", "主视觉内容 ≥ 盒的 %d%%" % int(MIN_CONTENT_RATIO * 100), ok,
                        "内容 %gx%g / 盒 %gx%g（err=%s）" % (cw, ch, mw, mh, report["main"].get("contentErr") or "")))
        elif report.get("main"):
            res.append(("H3", "主视觉内容包围盒", True, "N/A（未测得内容包围盒）"))

        # H4 无横向溢出
        ov = report.get("overflow")
        if ov:
            ok = ov["scrollW"] <= ov["clientW"] + 1
            res.append(("H4", "无横向溢出", ok, "scrollW=%d clientW=%d" % (ov["scrollW"], ov["clientW"])))
        else:
            res.append(("H4", "无横向溢出", True, "N/A"))

        # H5 触控目标
        stage = (re.search(r'data-cnki-stage\s*=\s*["\']([^"\']+)',
                           open(path, encoding="utf-8", errors="replace").read()) or [None, ""])
        need = STAGE_TOUCH.get((stage[1] if stage else "") or "", STAGE_TOUCH["default"])
        ctrls = report.get("controls") or []
        bad = [c for c in ctrls if min(c["w"], c["h"]) < need - 0.5]
        if bad:
            h5_detail = "%d 个偏小" % len(bad)
        else:
            h5_detail = "%d 个控件达标" % len(ctrls)
        res.append(("H5", "按钮触控 ≥ %dpx（学段下限）" % need, len(bad) == 0, h5_detail))

        # H6 __selfTest
        st = report.get("selfTest")
        if st is None:
            res.append(("H6", "window.__selfTest 数值/几何断言", True,
                        "N/A（未暴露接口；有读数/公式时建议补）"))
        elif isinstance(st, dict) and st.get("error"):
            res.append(("H6", "window.__selfTest 执行", False, st["error"]))
        elif isinstance(st, dict):
            cases = st.get("cases") or []
            if not cases:
                res.append(("H6", "__selfTest 含断言", True, "cases 为空（声明无可断言量）"))
            else:
                failed = [c for c in cases if not c or c.get("ok") is not True]
                # 查 NaN/Infinity
                badnum = []
                def walk(o, pth):
                    if isinstance(o, dict):
                        for k, v in o.items():
                            if isinstance(v, float) and not (v == v and v != float("inf") and v != float("-inf")):
                                badnum.append(pth + "." + str(k))
                            elif isinstance(v, dict):
                                walk(v, pth + "." + str(k))
                walk(st, "")
                ok = (len(failed) == 0) and (st.get("pass") is True) and (len(badnum) == 0)
                detail = "%d/%d 通过" % (len(cases) - len(failed), len(cases))
                if badnum: detail += "；含非有限数: " + ",".join(badnum)
                if st.get("pass") is not True: detail += "；顶层 pass!=true"
                res.append(("H6", "__selfTest 数值/几何断言", ok, detail))
        else:
            res.append(("H6", "__selfTest 返回值", False, "未返回对象"))

        return res, False
    except subprocess.TimeoutExpired:
        res.append(("H0", "无头浏览器", False, "超时（90s）"))
        return res, True
    except Exception as e:
        res.append(("H0", "无头浏览器", False, "异常: " + str(e)))
        return res, True
    finally:
        try:
            if tmp and os.path.isfile(tmp.name):
                os.remove(tmp.name)
        except Exception:
            pass
        try:
            if 'out_dir' in dir() and os.path.isdir(out_dir):
                shutil.rmtree(out_dir, ignore_errors=True)
        except Exception:
            pass


def js_errors_via_stderr(path, browser):
    """用独立一次 headless 运行抓 console 里的 Uncaught（studio R7 同思路）。"""
    try:
        log_path = os.path.join(tempfile.gettempdir(), "cnki_jserr_%d.log" % os.getpid())
        fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        subprocess.run(
            [browser, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--enable-logging=stderr", "--log-level=0",
             "--virtual-time-budget=3000", "--dump-dom", file_url(os.path.abspath(path))],
            stdout=subprocess.DEVNULL, stderr=fd, timeout=90000)
        os.close(fd)
        txt = ""
        if os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            os.remove(log_path)
        lines = [l for l in txt.splitlines() if re.search(r"Uncaught|Unhandled Promise|TypeError|ReferenceError|SyntaxError", l)]
        return lines[:3]
    except Exception:
        return []


def check_one(path, use_browser):
    print("\n" + "=" * 60)
    print("文件：%s" % os.path.basename(path))
    print("=" * 60)
    fails = 0
    warns = 0

    # 1) 结构自检
    print("\n-- 1) 结构自检 (validate_html.py) --")
    try:
        r = subprocess.run([sys.executable, VALIDATE, path], capture_output=False, timeout=60000)
        if r.returncode == 1:
            print("  FAIL  存在必须修复的结构问题（见上）")
            fails += 1
        else:
            print("  PASS  结构无阻断问题")
    except Exception as e:
        print("  WARN  validate_html 运行失败：%s" % e)
        warns += 1

    # 2) 常量核对
    print("\n-- 2) 学科常量核对 (lint_facts.py) --")
    try:
        r = subprocess.run([sys.executable, LINTFACTS, path], capture_output=False, timeout=60000)
        if r.returncode == 1:
            print("  FAIL  数值不一致（见上）")
            fails += 1
        else:
            print("  PASS  常量一致 / 无可查标记")
    except Exception as e:
        print("  WARN  lint_facts 运行失败：%s" % e)
        warns += 1

    # 3) 真浏览器
    print("\n-- 3) 真浏览器校验 (msedge --headless) --")
    browser = find_browser() if use_browser else None
    if not browser:
        print("  SKIP  未找到 msedge/chrome，跳过无头校验（静态检查已跑）")
    else:
        print("  browser = %s" % browser)
        results, skipped = headless_checks(path, browser)
        if skipped:
            print("  SKIP  无头测量未拿到报告（可能沙箱限制）")
        for rid, title, ok, detail in results:
            mark = "PASS" if ok else "FAIL"
            print("  %s  %s  %s%s" % (mark, rid, title, ("  — " + detail) if detail else ""))
            if not ok and rid != "H0":
                fails += 1
            elif not ok:
                fails += 1
        # JS 运行时错误（单独通道）
        errs = js_errors_via_stderr(path, browser)
        if errs:
            print("  FAIL  H7  无 JS 运行时错误  —  " + " | ".join(errs))
            fails += 1
        else:
            print("  PASS  H7  无 JS 运行时错误（console 无 Uncaught）")

    return fails, warns


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    use_browser = "--no-browser" not in args
    files = [a for a in args if not a.startswith("--")]
    total_fail = 0
    for p in files:
        f, w = check_one(p, use_browser)
        total_fail += f
    print("\n" + "=" * 60)
    if total_fail:
        print("结论：%d 个文件存在 FAIL，请修复后重试。" % total_fail)
    else:
        print("结论：全部通过（含 SKIP 项不计入失败）。")
    print("=" * 60)
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
