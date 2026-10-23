# 查验预览（仅限已在票夹中的发票）

## 什么时候读取

用户要查验**已在票夹中的发票**（已有 `fid`），但没有明确要求把查验结果回写票夹时读取本文件。

## ⚠️ 路由判断

- 如果用户提供的是**文件路径或 URL**（还没上传到票夹），**不要**使用本命令 → 应改用 `invoice.upload-and-validate`（一站式上传+OCR+查验）
- 本命令**仅适用于票夹中已存在的发票**，必须已有 `fid`

## Operation

| Operation | 固定规则 |
| --- | --- |
| `invoice.validate.preview` | 先取详情，固定 `flag=100`、`is_save=1`、`needLog=true`，不回写查验结果 |

## 输入

必须提供 `fid` 和 `scope`。`scope` 只能是 `personal` 或 `enterprise`。

## 示例

Windows PowerShell：

```powershell
weaver-work-cli --json invoice run invoice.validate.preview --input-json '{"fid":"12345","scope":"personal"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json invoice run invoice.validate.preview --input-json '{"fid":"12345","scope":"personal"}'
```

## 注意

`invoice.validate.preview` 只做预览。`saved=false` 表示没有回写票夹；不要把预览结果描述为已更新发票。
