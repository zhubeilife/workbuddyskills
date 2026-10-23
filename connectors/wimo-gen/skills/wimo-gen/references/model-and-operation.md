# Flow 模型与参数

生成合同来自 FlowGenerateRequest，连接器已通过 inputSchema 暴露。模型目录用于选择 model_id 和校验支持范围，不需要它再提供低层供应商参数 schema。

## 模型选择

- `creator_list_models` 返回 items。图片选 model_type=image，视频选 model_type=video；仅使用实际返回的 model_id。
- 用户指定模型时匹配目录中的显示名或 ID，确认媒体类型和能力；无法唯一匹配时澄清。
- 未指定模型时，优先使用符合请求且 is_default=true、is_deprecated=false 的模型。无唯一合适默认模型时，按已返回能力给出选择，不猜测价格或模型排名。
- 支持范围读取 supported_output_counts、supported_image_sizes、metadata.generation_params、metadata.slot_mode_rules；必需的能力约定缺失时报告缺失，不用家族名推导。

## 提交字段

- project_id：真实 Flow 项目 id。
- prompt：创作描述；当前后端合同必填非空字符串，最多 8000 字符。
- media_type：image 或 video。
- model_id：所选模型 UUID；普通生成必传，cutout/upscale 的模型省略仅按工具明确的后端合同执行。
- request_id：本连接器要求非空幂等键，同一逻辑提交重试保持不变。
- aspect_ratio、resolution、quality、size、width/height、duration、output_count 等可选字段，按工具 schema 与模型配置交集填写。metadata.generation_params.ratio 的选项映射到 Flow 合同中的 aspect_ratio；不是提交 ratio 字段。
- 默认值仅可来自所选模型明确返回的 generation_defaults 或后端合同，未提供的可选字段可省略并由后端处理。不从计费 manifest 的 default_params 合成生成参数，也不自拟默认值。
- 单张请求明确传 output_count=1；其它数量必须属于模型支持范围。宽高必须成对传入，图片比例和分辨率必须符合 supported_image_sizes 的组合。

## Operation 与参考

- 文生图、文生视频省略 operation，后端按 media_type 处理。
- 图生图、图生视频、多参考和首尾帧使用工具 schema 中的 operation 及模型明确支持的能力；不按模型名字猜能力。
- 已有参考素材按 source_media_id 或 source_media_ids[{media_id, slot_type}] 传入；slot_type 与数量取自模型槽位合同。
- `creator_upload_media` 支持两种输入：公网 HTTPS URL（`source_url`）或 base64 编码文件数据（`file_data` + `filename` + `mime_type`），二者选一。返回真实 `media_id` 后才能作为 source media 使用。
