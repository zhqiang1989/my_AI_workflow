# 私行客户经理 · WorkBuddy + LLM Wiki 基础实操手册

面向零基础学员的 WorkBuddy 实操课件。先用虚构样例练习建库、整理资料、编译画像和准备沟通草稿。

[在线打开实操手册](https://zhqiang1989.github.io/my_AI_workflow/)

[PPT 简报（长微信版）](https://raw.githubusercontent.com/zhqiang1989/my_AI_workflow/master/materials/brief.md) · [公开课堂材料和可复制指令](materials/)

## 文件说明

| 文件 | 用途 |
|---|---|
| `私行客户经理_WorkBuddy实操手册.html` | 主课件。示例工作流、客户对话样例、完整工作流三个页签 |
| `samples/客户微信_*.txt` | 王先生、李女士和张总的虚构档案卡与长微信对话，共 63 条消息 |
| `samples/微信对话样例.zip` | 三份 TXT 的下载包 |
| `samples/人物样例.json`、`samples/portraits/` | 可编辑的画像文字和三张课堂配图 |

## 课件结构

页面默认打开**示例工作流**，用「课堂示例知识库」练习。**客户对话样例**展示三位课堂客户的画像和长微信记录，可复制单份，也可复制三份记录和录入指令。**完整工作流**用独立的「私行工作知识库」整理一位客户的微信记录和公开产品资料。WorkBuddy 会询问日常沟通还要参考哪些资料，按确认范围补充后起草消息。试跑通过后，可用本地定时任务归档该客户新增的微信，并更新已确认的产品资料。

提示词可以直接复制到 WorkBuddy。微信备注名、来源范围和定时时间在 WorkBuddy 对话里确认。

## 修改课堂样例

微信原文保存在 `samples/客户微信_*.txt`，画像文字保存在 `samples/人物样例.json`。如要更新，在仓库根目录运行 `python scripts/build_samples.py`，从这组资料重建 PPT 简报、长微信合辑、下载包和 HTML 画像。配图保存在 `samples/portraits/`。

## 数据与合规说明

- 资金、日期、对白、客户档案及其中的风险测评均为课堂虚构。
- 产品信息来自建行公开渠道，以官方最新公告为准。
- 课件保留人工审核要求：AI 生成话术须经客户经理审核后使用。
