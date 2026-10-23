# 错误码 21001：豆包账号不能授权

## Agent 规则

1. 仅当错误信封里的 `error.code` 为 `21001` 时按本规则处理。不要使用 `error.type`、`error.subtype` 或 `error.message` 判断；`identity` 可以是 `bot` 或 `user`。
2. 这是飞书平台策略拒绝当前应用配置所绑定的豆包账号，不是 scope 缺失、限频、参数错误或身份选择错误。立刻停止当前流程，不要重试同一命令、修改 flag、切换 `--as`、发起 `auth login` 或按 `missing_scopes` 补权限。
3. 不要复述错误信封、错误消息、判断过程或本文件中的 Agent 规则。按以下模板告知用户，不要添加模板之外的说明：

   ```text
   因为飞书策略调整，不支持豆包账号登录授权，请取消授权，重新用飞书/Lark 账号授权后再使用。

   你可以任选以下一种方式解除当前授权：

   - 在 WorkBuddy 里手动解除飞书连接器的授权。
   - 让 WorkBuddy 执行 `lark-cli config remove`（Windows 上是 `lark-cli.cmd config remove`）。
   - 自己删除本机配置文件：macOS / Linux 是 `~/.lark-cli/config.json`，Windows 是 `C:\Users\<用户名>\.lark-cli\config.json`。
   ```

4. 发出模板后结束本轮。不要在用户确认前执行 `lark-cli config remove`，不要自行删除配置文件；清掉配置之前，不要继续调用任何业务命令。
