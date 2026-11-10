# Mailbox API and capability inventory

Checked against this repository on 2026-11-10. Runtime `/open_api/settings`
flags and server responses decide availability. Paths below use the configured
API base. The client accepts mailbox `/api/` paths and `/open_api/settings`;
account/admin integrations require separate tooling and credentials.

## Supported mailbox operations

Use `python3 scripts/mailbox.py [--credentials <file>] [--body-file <json>] METHOD PATH`.
Quote paths containing query strings. JSON bodies belong in mode-0600 files.
Mailbox calls use Address JWT in `Authorization: Bearer`; creation/login do not.
Site password uses `x-custom-auth`; creation User JWT uses `x-user-token`.

| Operation | Method and path | Body / condition |
| --- | --- | --- |
| Capabilities and domains | GET `/open_api/settings` | No mailbox JWT |
| Create address | POST `/api/new_address` | Optional `name`, `domain`, `cf_token`, `enableRandomSubdomain`; requires `--save-as` |
| Password login | POST `/api/address_login` | `email`, SHA-256 hex `password`, optional `cf_token`; requires `--save-as` |
| Address and send balance | GET `/api/settings` | Existing JWT |
| Parsed inbox | GET `/api/parsed_mails?limit=20&offset=0` | Returns `results`, `count` |
| Parsed message | GET `/api/parsed_mail/<id>` | Sender, subject, text, HTML, attachment metadata |
| Raw inbox/message | GET `/api/mails?limit=20&offset=0`, `/api/mail/<id>` | RFC822 `raw`; local MIME parsing for attachment bytes |
| Mark read/unread | PATCH `/api/mails/<id>/read` | `{"isUnread":false}` or true; read-status feature required |
| Delete received message | DELETE `/api/mails/<id>` | Deletion enabled |
| Request send access | POST `/api/request_send_mail_access` | `{}`; request does not guarantee approval |
| Send | POST `/api/send_mail` | See example below; send backend and positive balance required |
| Sent messages | GET `/api/sendbox?limit=20&offset=0` | Inspect after send or ambiguous timeout |
| Delete sent record | DELETE `/api/sendbox/<id>` | Does not recall delivered mail |
| Empty inbox/sent | DELETE `/api/clear_inbox`, `/api/clear_sent_items` | Explicit target/scope; deletion enabled |
| Delete mailbox | DELETE `/api/delete_address` | Destructive mailbox lifecycle operation |
| Change password | POST `/api/address_change_password` | `new_password`: SHA-256 hex; password feature required |
| Auto reply | GET/POST `/api/auto_reply` | POST `{"auto_reply":{"name":"","subject":"Away","source_prefix":"","message":"Reply text","enabled":true}}`; enabling authorizes future automatic sends |

Send body:

```json
{"from_name":"","to_mail":"recipient@example.com","to_name":"","subject":"Hello","content":"Hello","is_html":false}
```

Use a reply's recipient/subject/body as a new send. This endpoint does not offer
a dedicated thread-reply or outbound attachment field. Do not promise either.
Hash plaintext mailbox passwords with SHA-256 exactly once before login/change;
the generated password returned on creation is plaintext, while a saved request
hash is already hashed. Credentials and password hashes are both secrets.

## Additional integrations available in the project

These require feature-specific configuration and payloads. Inspect the matching
API docs or installed source before invoking them; this inventory alone is not
an execution contract for provisioning them.

| Capability | API/component | Requirements |
| --- | --- | --- |
| Mailbox Webhook configuration, filter checks and tests | `/api/webhook/settings`, `/check_filter`, `/test` (last two under `/api/webhook`) | KV, enabled Webhooks, allowed mailbox, user-authorized destination; tests send requests |
| S3 attachment list, delete, upload/download signed URLs | `/api/attachment/list`, `/delete`, `/put_url`, `/get_url` (last three under `/api/attachment`) | Configured S3; separate from MIME attachments |
| Account registration/login, OAuth2, passkeys | `/user_api/*` | User system enabled, human participation where needed |
| Bind/unbind/transfer addresses, obtain bound JWTs, aggregate inbox/sent items | `/user_api/*` | User JWT and address ownership |
| Redeem quotas/roles | `/redeem_api/*` | Enabled redemption and valid code |
| Telegram inbox access, notifications, mailbox binding/creation | `/telegram/*` | Configured bot and valid Telegram identity; independent notification authorization |
| SMTP sending and IMAP reading | `smtp_proxy_server/` | Deployed proxy, network access and TLS configuration |
| Address/user/role administration, quotas, statistics, cleanup, password reset | `/admin/*` | Separate administrator credentials and explicit administrative scope |
| Global Webhooks, OAuth settings, IP controls, AI extraction, redemption administration | `/admin/*` | Admin scope and corresponding providers/configuration |
| Database initialization/migrations, backup/recovery and deployment | Admin API and repository maintenance tooling | Separate maintenance workflow; never part of routine mailbox access |

Hermes can additionally summarize, translate, classify and locally search fetched
mail, extract codes/links, save attachments, and run scheduled checks. These are
agent workflows over the APIs, not claims of native server search or scheduling.
