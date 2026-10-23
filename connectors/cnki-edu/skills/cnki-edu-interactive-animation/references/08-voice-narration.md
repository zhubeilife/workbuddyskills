# 语音朗读 / 讲解（可选增强）

> 背景：三个 skill 现状都不把「语音」当作能力。cnki 原本只有「可点读发音」的诉求却没落地。本文件给出**离线、点击触发、不引外部音频**的可选方案，补齐这一短板。

## 一、红线（不可破）

1. **绝不直接 / 间接引外部音频文件**（`<audio src=...>`、网络音频、CDN 语音包都禁止）——离线单文件要求。
2. 用浏览器原生 **`speechSynthesis`**（Web Speech API）。它调用系统已装语音引擎，**不下载、不联网、不引文件**，符合「无外部音频」红线。
3. **必须点击触发**（按钮）。浏览器自动播放策略禁止页面一打开就朗读；且「一打开就念」对课堂是干扰。
4. **可选、非必需**：作品没有朗读按钮也完全合规。朗读是锦上添花，绝不能做成像 studio 否掉的「听力陷阱」——**不看字、不听声就该能懂**。
5. 中文音色依赖用户系统是否装了中文 TTS（Windows 自带 Microsoft 语音，但部分神经音色需联网下载）；英语同理。**无头校验测不到声音**，故仅做「按钮存在 + 调用不抛错」的可用性检测。

## 二、何时加

- 英语：单词 / 句子点读发音、对话场景「朗读示范」。
- 语文：古诗 / 课文「听读」、拼音 / 生字点读。
- 其他学科：关键结论「讲解一遍」（可选）。

## 三、标准实现（直接抄）

```html
<button class="btn" id="readBtn" aria-label="朗读讲解">🔊 朗读</button>
<script>
(function () {
  var btn = document.getElementById('readBtn');
  if (!('speechSynthesis' in window)) {
    btn.style.display = 'none';           // 环境不支持就优雅隐藏，不报错
    return;
  }
  var text = "黄赤交角约为23.44度，地球因此产生四季更替。"; // 取自主视觉讲解文案
  btn.addEventListener('click', function () {
    try {
      window.speechSynthesis.cancel();     // 先停掉上一段，避免叠读
      var u = new SpeechSynthesisUtterance(text);
      u.lang = 'zh-CN';                     // 英语用 'en-US'
      u.rate = 0.95; u.pitch = 1;
      window.speechSynthesis.speak(u);
    } catch (e) { /* 忽略：语音失败不影响教学 */ }
  });
})();
</script>
```

要点：
- `text` 从作品自身的讲解文案取，**不要**在生图里烤语音。
- `u.lang` 与学科一致；可让用户切换中/英。
- 多个朗读点：给每段一个 `Speak(text)`，复用同一个按钮或每个点一个喇叭图标。
- 关闭页面前 `speechSynthesis.cancel()` 免得残留朗读（可选）。

## 四、与 v2 / studio 的关系

- v2：明确「不依赖外部音频；用音标+口型替代」——我们比它多走了一步，提供**真能出声**的可选按钮。
- studio：`gate-check.mjs` 直接**拒绝 `<audio>/<video>/<source>`**；我们的 `speechSynthesis` 方案完全绕开被拒标签，合规。
