# Provenance and licenses / 来源与许可证

Repository additions are available under the root MIT [LICENSE](LICENSE).

`writing-skills` was imported from the owner's existing local skill, version 0.6.0. Its frontmatter declares MIT.
The package includes authoring procedures and the independently configured Hermes target lookup; actual runtime configuration is not distributed.

`cf-temp-mail-agent-mail` was imported from the owner's local adaptation in
[cloudflare_temp_email](https://github.com/dreamhunter2333/cloudflare_temp_email), version 1.0.0.
The upstream copyright is Copyright (c) 2023 Dream Hunter; the complete upstream
[MIT license](skills/cf-temp-mail-agent-mail/LICENSE) is preserved inside that package.
The imported adaptation adds creation, credential persistence, management workflows and a Python client.
The package is a client workflow; it does not bundle the mailbox application.

`github` is a complete backup of the owner's default-profile GitHub skill as of 2026-11-10,
based on [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/software-development/github).
Its frontmatter credits Ben Barclay (benbarclay) and Hermes Agent. The package preserves the
upstream [MIT license](skills/github/LICENSE), Copyright (c) 2025 Nous Research.
The local 2.0.1 adaptation adds PR submitter profile/session identity instructions. It excludes
the separate gpt profile's `Advancing an Already-Deployed Tracking Issue` customization.
All 17 component files were copied unchanged from the default-profile source; the upstream
LICENSE was added for redistribution. No runtime configuration or credentials are included.

`github` 为默认 profile 的完整组件备份，保留 PR 会话身份提示，不含 gpt 专属的已部署 Issue
跟进规范。原组件 17 个文件按原内容复制，另附上游完整 MIT 许可证；未备份运行配置或凭据。

仓库新增内容采用根目录 MIT 许可证。邮箱技能源自上述上游项目的本地扩展，技能目录中保留完整上游版权与许可。
writing-skills 来自已有的本地 MIT 技能。第三方服务的名称不表示其维护者为本仓库背书。
