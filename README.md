# Agent Skills

[English](README_EN.md)

可单独安装的 Agent 技能集合，以 Hermes 工作流为主。每个技能包含自己的说明、脚本和参考资料。

| 技能 | 版本 | 用途 |
| --- | --- | --- |
| [writing-skills](skills/writing-skills/SKILL.md) | 0.7.0 | 编写和维护 Hermes 技能；查询指定运行实例、profile 及安装位置，检查同名冲突 |
| [cf-temp-mail-agent-mail](skills/cf-temp-mail-agent-mail/SKILL.md) | 1.0.0 | 通过 cloudflare_temp_email API 创建邮箱、读信、提取验证码及管理邮件；发信等功能取决于服务端配置 |

## 安装到 Hermes

将 `<profile>` 替换为你明确选择的、已存在的 profile 名；使用默认 profile 时写 `default`。
在实际运行 Hermes 的主机或容器内执行，选择所需技能即可：

```sh
hermes -p <profile> skills install iasi777/agent-skills/skills/writing-skills
hermes -p <profile> skills install iasi777/agent-skills/skills/cf-temp-mail-agent-mail
```

也可以将本仓库加入技能源，方便后续发现新技能：

```sh
hermes -p <profile> skills tap add iasi777/agent-skills
```

添加技能源不等于安装技能。Hermes 自身的第三方技能扫描和提示保持有效。
目录结构采用官方支持的 [`skills/<name>/SKILL.md` 布局](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/#publishing-a-custom-skill-tap)。

如果使用手工安装，先克隆本仓库，再把所需的整个技能目录复制到已经解析好的
`<profile-home>/skills/` 下。更新前检查同名目录；不要只复制 SKILL.md，也不要直接覆盖本地修改。

## 首次配置

- **writing-skills**：参考 [固定查询入口](skills/writing-skills/references/target-lookup.md)，将示例复制为 `~/.config/writing-skills/hermes-targets.json`，填写你自己的 SSH 别名、容器、Python、代码目录和 `data_root`。它只查询位置，安装仍由技能流程执行。
- **邮箱管理**：按 [技能说明](skills/cf-temp-mail-agent-mail/SKILL.md)配置 API 地址及必要凭据。凭据放在运行环境中，使用独立的私密文件；此仓库不提供邮箱服务或默认账号。

运行配置、邮箱凭据、验证码、邮件内容和任务状态均保存在技能目录之外。可提交的配置只有占位示例。

## 本地检查

需要 Python 3.10 或更新版本，不需要额外 Python 包：

```sh
python3 -B scripts/check.py
python3 -B -m unittest discover -s skills/writing-skills/tests -v
python3 -B skills/cf-temp-mail-agent-mail/scripts/mailbox.py --help
```

GitHub Actions 在 push 和 pull request 时运行这些检查。单元测试使用临时目录和模拟的 Hermes 接口，
不会连接真实服务器、创建邮箱或发送邮件。真实部署验证应按各技能说明单独执行。

## 维护与来源

本仓库是集合的维护和发布入口。每个技能保留独立的 `metadata.version`；修复在这里进行，
本机维护目录为 `~/projects/agent-skills/`。本机 Codex 的 writing-skills 通过符号链接直接使用这里的源码；
独立安装的客户端和原应用仓库副本仍需显式更新。

writing-skills 修改前保留一份上一版目录备份：`~/.local/state/writing-skills/backups/previous`。
先验证新备份完整，再替换旧备份；备份留在仓库和技能发现目录之外。

本仓库只收录两个通用技能；`cf-temp-mail-agent-read` 是独立的个人读取技能，不包含在本集合中。
邮箱项目本身保持独立，详见 [来源与许可证](NOTICE.md)。

新技能放入 `skills/<name>/`，保持可单独安装。变更记录见 [CHANGELOG.md](CHANGELOG.md)。
