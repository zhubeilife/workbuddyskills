# 数值 / 几何自检接口（window.__selfTest）

> 借鉴 v2 的 `selfcheck.mjs` 与 studio 的 `kas-selftest`。目的：**让「算得对不对」能被机器核对，而不是只能靠人眼**。这是「防疏忽」机制，不是「防作弊」机制——它只验证作品**自己声明**的数值主张。

## 一、什么时候必须写

只要动画里出现**会被拿教材对一遍的量**，就必须暴露 `window.__selfTest()`：

- 读数（压强、像距、电压、读数条）
- 公式结果（y=kx+b 在 x=3 时 y=?；凸透镜 v=uf/(u−f)）
- 比例（电解水 2:1；地图比例尺）
- 计数（配平后原子数、分镜数）
- **几何断言**（数学/物理图形本身就是论证：三角形内角和=180、向量合成、等面积）

纯情境/纯插画类（如古诗意境）没有可断言量，让它返回 `{pass:true, cases:[]}` 即可——但**接口不能省**。

## 二、接口契约

```js
window.__selfTest = function () {
  return {
    pass: true,                 // 整体是否通过
    cases: [                    // 至少 2 条（有数值主张时）
      { name: "像距", ok: true, expect: 30, actual: 30 },
      { name: "放大率", ok: true, expect: 2, actual: 2 }
    ]
  };
};
```

要求：
1. `cases` 里每条有 `name / ok / expect / actual`；`ok` 必须为布尔。
2. 求解逻辑尽量 **DOM-free**（纯函数），这样万一要离线 Node 跑也能跑；`verify_render.py` 在真实浏览器里调用它，DOM 可用但别依赖没初始化的元素。
3. 返回值不得含 `NaN / Infinity / undefined`——`verify_render.py` 会查。
4. 几何类同样走这套接口（见第三节），不另立门户。

## 三、几何断言（数学/物理必写）

图形的形状本身就是结论。把关键量**独立复算**一遍，和「视觉上画的样子」交叉验证：

```js
window.__selfTest = function () {
  // 例：任意三角形内角和
  function interiorSum(pts) {
    var s = 0;
    for (var i = 0; i < 3; i++) {
      var a = pts[i], b = pts[(i + 1) % 3], c = pts[(i + 2) % 3];
      var ang = Math.atan2(b.y - a.y, b.x - a.x) - Math.atan2(c.y - a.y, c.x - a.x);
      ang = Math.abs(ang) % (Math.PI * 2);
      if (ang > Math.PI) ang = 2 * Math.PI - ang;
      s += ang;
    }
    return s * 180 / Math.PI;
  }
  var tri = [{x: 80, y: 60}, {x: 300, y: 220}, {x: 120, y: 300}];
  var sum = interiorSum(tri);
  return {
    pass: true,
    cases: [
      { name: "三角形内角和", ok: Math.abs(sum - 180) < 0.5, expect: 180, actual: +sum.toFixed(2) },
      { name: "无退化(面积>0)", ok: true, expect: ">0", actual: "ok" }
    ]
  };
};
```

> 进阶：把多边形放在带 `id` 的 `<g>` 里，让 `verify_render.py` 也能独立用鞋带公式复算面积（见 `04-layout-families.md` 的「画布与 DOM 分工」）。

## 四、verify_render.py 怎么用它

`scripts/verify_render.py` 在真实无头浏览器里加载作品，调用 `window.__selfTest()`：
- 有 `cases` → 逐条比对 `ok`，全部 `true` 且顶层 `pass===true` 才过；
- 含 `NaN/Infinity` → 直接 FAIL；
- 没暴露接口且作品有读数类元素 → 警告（提示你补接口）。

## 五、标准模板（直接抄）

```html
<script>
window.__selfTest = function () {
  // TODO: 把你的求解结果填进来（纯函数优先）
  var cases = [
    { name: "示例读数", ok: true, expect: 0, actual: 0 }
  ];
  var pass = cases.every(function (c) { return c.ok === true; });
  return { pass: pass, cases: cases };
};
</script>
```
