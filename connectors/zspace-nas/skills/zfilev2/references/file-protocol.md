# 文件上传 / 下载协议（zfilev2）

> 本文件由 `scripts/gen-skills.mjs` 复制到 `skills/zfilev2/references/`。

## 上传（连接器已封装为 `upload_file`）

`POST /v2/file/upload`，header 携带 `path/size/seek/split/uuid(32~128 字符)/rename`，body 为裸字节。

- `split=1` 分片；最后一帧满足 `seek + len == size` 时落盘。
- 进度查询：**`GET /v2/file/tmpinfo?path=&uuid=`**（注意是 **GET**，不是 POST）。
- 失败原因：`POST /v2/file/upload/whyfail {uuid}`。
- **断点续传**：连接器的 `uuid` 由「本地路径 + 大小 + mtime」哈希得出（稳定），
  重试时先查 `tmpinfo` 得到已写入字节数，再从该偏移继续；返回的 `resumedFrom` 表示本次起点。
  非整片偏移会回退到上一整片边界（NAS 只保证整片落盘）。

## 下载（连接器已封装为 `download_file` / `read_file`）

`GET /v2/file/download?path=...`，支持 Range。

- 连接器先 `HEAD` 取真实大小并钳制 Range（NAS 对越界 Range 处理异常，可能提前断连）。
- **流式写盘**，不再整文件读入内存。
- 后端以 `200 + application/json` 返回错误体时**不会写入文件**，直接返回后端错误码。
- `offset > 0` 续传时要求本地文件大小正好等于 `offset`，否则报 `E_OFFSET_MISMATCH`
  （避免写出损坏文件）；下载中断时会提示可用 `offset = 已写入字节数` 续传。
- `read_file` 默认最多读 64KB（`ZSPACE_MAX_READ_BYTES` 可调），二进制文件用 `encoding:"base64"`。

## 写入（`write_file`）

`POST /v2/file/create`，header `path` + `rename`，body 为文件内容（`text/plain`）。

- `rename`：0=重名报错 1=自动改名（默认）2=跳过 3=**覆盖**（⚠️ 需先经用户确认）。
