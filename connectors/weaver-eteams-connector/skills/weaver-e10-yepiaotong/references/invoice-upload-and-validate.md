# 一站式上传+OCR+查验

## 什么时候读取

用户要求上传发票附件并完成查验（上传→识别→查验一步到位）时读取本文件。
如果用户只需要单独上传或单独 OCR，请分别参阅 `invoice-file-upload.md` 或 `invoice-import.md`。

## Operation

| Operation | 说明 |
| --- | --- |
| `invoice.upload-and-validate` | 上传发票文件 → OCR 识别 → 逐张查验，合并为单条命令 |

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `file` | string | 与 url 二选一 | 本地文件路径 |
| `url` | string | 与 file 二选一 | 可访问的文件 URL |
| `scope` | string | ✅ | `personal`（个人票夹）或 `enterprise`（企业票夹） |

文件来源支持扩展名：`pdf`、`ofd`、`xml`、`png`、`jpg`、`jpeg`。
本地文件必须存在、非空且不超过 25 MiB。URL 只允许 `http/https`，不能包含账号密码。

## 示例

Windows PowerShell：

```powershell
weaver-work-cli --json invoice run invoice.upload-and-validate --input-json '{"file":"./invoice.pdf","scope":"personal"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json invoice run invoice.upload-and-validate --input-json '{"file":"./invoice.pdf","scope":"personal"}'
```

## 返回

```jsonc
{
  "status": "COMPLETE",
  "data": {
    "upload": { /* upload 对象：id, ids, fileType, fileName, totalPages … */ },
    "ocrCount": 1,           // OCR 识别出的发票数量
    "invoices": [ /* OCR 识别出的发票列表（原始 info） */ ],
    "validations": [         // 每张发票的查验结果
      {
        "fid": "751293486469988353",
        "code": "031001900311",
        "number": "00188205",
        "date": "2024-11-25",
        "total": "200.00",
        "buyer": "...",
        "payer": "...",
        "scope": "personal",
        "validation": 1,      // 查验结果：1=真 0=假/未查验
        "invoiceStatus": 0,
        "saved": false
      }
    ],
    "validationErrors": [],   // 查验失败的发票 [{fid, error}]
    "results": [ /* OCR 原始返回 */ ],
    "workflow": { "workflow": "invoice.upload-and-validate", "version": 1, "state": "COMPLETE" }
  }
}
```

### 部分失败

- 上传失败：直接报错。
- OCR 失败：返回 `partialData`（含 upload 对象），状态为 `OCR_FAILED`。
- 单张查验失败：不中断整体流程，失败项记入 `validationErrors`，其余成功项正常返回 `validations`。

## 与分步操作的关系

本命令等价于依次执行：

1. `invoice.upload`（上传文件获取 upload 对象）
2. `invoice.ocr.preview`（OCR 识别所有页面）
3. `invoice.validate.preview`（逐张查验）

如需更细粒度的控制（例如只上传不查验、或重复 OCR），请使用上述分步命令。

## 注意

上传前必须先提醒用户：发票附件/图片/文件内容可能被上传到 E10 业票通，并可能进入当前大模型上下文用于理解和处理；只有用户明确确认后才执行。用户仅提供文件路径或文件名不等于同意上传。
