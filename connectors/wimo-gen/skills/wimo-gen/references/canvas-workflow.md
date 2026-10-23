# 画布：从零编排

首版支持文本、图片、视频节点。工具不自动运行下游；按用户授权的创作目标逐步推进。

## 准备与创建

1. 复用已指定画布，使用 `creator_get_canvas` 获取节点摘要和运行任务。项目必须返回 `workspace_mode=canvas`；只读项目只查询。指定项目不可用时停止，不替换项目。
2. 无项目时先 `creator_list_scenes`，按实际场景描述选择符合意图的场景，再 `creator_create_canvas_project`。不猜 scene_key，不使用 Flow 创建工具。当前不支持需要参考视频预置的场景。
3. 按依赖创建所需节点：`creator_create_node` 的 node_type 为 text、image 或 video。创建不生成；文本可直接写 content，也可保存 prompt 后生成。可在首次创建时成对指定坐标，未指定则由后端创建合同处理；不额外调用布局操作。

## 保存配置与参考

- 使用 `creator_get_node` 读取节点配置、修订号、输入槽位和普通生成动作。`creator_update_node` 只提交要改的标题或 payload 字段；使用本次读取的 node_revision。
- 需要选择模型时用 `creator_list_models`，文本匹配 llm、图片匹配 image、视频匹配 video。仅使用实际返回的 model_id 和能力；默认配置由后端处理，不从模型名称或价格推导。
- 创作字段以工具 schema 与实际模型能力交集为准。图片／视频生成前检查 generation_config_state 和 generation_config_missing_fields，缺配置则补齐后回读。单张请求设置支持的 output_count=1；其它数量沿用用户授权。
- 参考关系用完整的 input_bindings 保存，保留未修改的绑定。首版仅开放 reference_text、reference_image、first_frame、last_frame；还必须存在于目标节点的 available_input_slots，并满足来源类型、数量和互斥规则。不要用 parent_ids 或把节点 ID 写进提示词替代绑定。
- 先保存模型，再读取该模型的实际槽位，最后保存绑定；模型修改与绑定分两次提交。需要清空参考时明确传空数组。
- 可以提前连接尚未完成的上游，但生成下游前必须回读上游：文本应有可用内容且未运行／失败，图片须已完成且有真实媒体结果。

## 逐步生成与取回

1. 确认当前节点实际提供且启用对应的 generate_text、generate_image 或 generate_video；调用 `creator_generate_node`，使用最新 node_revision 和本次逻辑提交的稳定 request_id。配置已保存在节点，不传任意动作参数。
2. 保存返回的 task_ids，使用 `creator_query_task` 查询。按 [Flow 工作流](workflow.md) 的轮询间隔与等待预算执行，任务状态以后端为准。未知状态或合同缺失时停止依赖操作。
3. 任务成功后用 `creator_get_node` 回读结果。文本读取 payload.content；图片／视频读取 payload.result_url 或 payload.outputs 中实际返回的 result_url。不要读取 Flow history，也不以缩略图充当生成结果。
4. 上游结果可用后再生成下游。例如「文案 → 图片 → 首帧视频」先完成文案，再完成绑定文案的图片，最后完成绑定图片首帧的视频。任一步失败时停止依赖它的节点，保留已经完成的结果。

## 恢复与范围

- create/update 的 client_mutation_id 与 generate 的 request_id 由调用方生成，不向用户索取。同一操作重试保留标识及完整原参数；改变内容属于新操作。
- 超时或结果不确定时，先读画布运行任务和节点，再查询已有任务；不要盲目重新生成。项目创建没有幂等键，不自动重复创建。
- 版本冲突时重新读取画布／节点，说明冲突；不自动替换修订号重放旧修改。只读、动作禁用、槽位缺失或上游未就绪时暴露实际原因。
- 不开放删除／恢复／复制、分组、撤销／历史、重新布局、音频及专用节点、图片特效与派生、视频剪辑／导出、全图自动调度。当前也没有本地素材导入节点工具（用户本地文件可通过 `creator_upload_media` 的 `file_data` base64 参数上传后使用）；需要这些能力时明确说明缺失。
- 默认只展示必要中间结果、最终产物、项目链接与需用户处理的问题。完成或结束等待后按技能入口调用 `creator_get_project_link` 获取“查看项目”链接。节点内容按需读取；不输出整张画布、内部修订号、绑定 JSON、原始响应或账号资料。
