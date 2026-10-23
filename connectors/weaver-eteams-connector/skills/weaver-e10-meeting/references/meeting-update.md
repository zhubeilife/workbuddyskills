# 已迁移

本文件已由 [meeting-change.md](meeting-change.md) 取代。

- 业务术语为「变更」；CLI operation 为 `meeting.change.prepare` / `meeting.change.apply`。
- 旧 `meeting.update.*` 已下线：它会固定发送 `operateType=UPDATE`，与"草稿走 UPDATE、正常走 CHANGE"的真实业务语义不符。
- 本文件保留仅作迁移提示；**不要单独删除本文件**：`SKILL.md`「不在范围」仍引用它，且 `test/skills/layout.test.ts` 要求 `references/` 下每个 `.md` 都被 `SKILL.md` 链接。如需彻底移除，请同时删掉 `SKILL.md` 中的引用行。
