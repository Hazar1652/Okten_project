# Postman

1. Import `Okten.postman_collection.json` and `Okten_Local.postman_environment.json`
2. Select environment **Okten Local** (`base_url` = `http://localhost/api`)
3. Scripts save tokens and ids with `pm.environment.set` into that environment (not collection variables)

### Demo users

| User | Password | Role |
|------|----------|------|
| `demo_user` | `DemoPass123!` | `super_admin` (moderation) |
| `demo_guest` | `DemoPass123!` | regular (messaging) |

### Folders (run in order)

1. **Auth** — `register` or `login` / `login_admin` → `refresh_token` → `me` → `oauth_config` → `health`
2. **Catalog** — tags, features, pages, top-categories (fills `tag_id`, `feature_id`, …)
3. **Venues** — `post_venue` → `submit_venue` → `login_admin` → `approve_venue` → gets → `patch_venue` → places
4. **Content** — per resource: create → get → patch (reviews, complaints, favorites, news, hangouts, top-category, stats, `patch_me`)
5. **Messaging** — `login_guest` → conversation/messages → `login_admin` again
6. **Lifecycle** — `cancel_hangout` / `close_hangout`; `reject_venue` last
7. **Deletes and Admin** — deletes, then admin user endpoints (use another user’s `user_id`, not your own)

URLs end with `/`. Collection auth is Bearer `{{access_token}}`; public endpoints use No Auth.
