# Postman

1. Import `Okten.postman_collection.json` and `Okten_Local.postman_environment.json`
2. Select environment **Okten Local** (`base_url` = `http://localhost/api`)
3. Run requests in this order (Collection Runner «Run all» as-is will fail)

### Порядок перевірки

**A. Auth**
1. `login` (або `register` з новими username/email) — збереже `access_token`
2. `refresh_token`, `me`, `oauth_config`, `health`

Демо: `demo_user` / `DemoPass123!` (має бути `super_admin`).  
Другий юзер для чатів: `demo_guest` / `DemoPass123!`.

**B. Довідники**
3. `get_tags` → `get_tag_by_id`
4. `get_venue_features` → `get_venue_feature_by_id`
5. `get_pages` → `get_page_by_slug`
6. `get_top_categories`

**C. Venue (як super_admin)**
7. `post_venue` → `submit_venue` → `approve_venue`
8. `get_venues` → `get_venue_by_id` → `patch_venue`
9. `places_autocomplete` / `places_details` (потрібен `GOOGLE_PLACES_API_KEY`)

**D. Контент по `venue_id`**
10. `post_review` → `get_reviews` → `patch_review`
11. `post_complaint` → `get_complaints` → `patch_complaint_status`
12. `post_favorite` → `get_favorites`
13. `post_news` → `get_news` → `patch_news`
14. `post_hangout` → `get_hangouts` → `patch_hangout`
15. `post_top_category` → `patch_top_category`
16. `venue_stats`

**E. Чати (інший акаунт)**
17. `login` як `demo_guest` → `post_conversation` → `post_message` → `read_conversation` → `get_messages` → `unread_count`
18. Знову `login` як `demo_user` для admin/delete

**F. Hangout status / moderation**
19. `cancel_hangout` **або** `close_hangout` (не обидва як обов’язкові)
20. `reject_venue` — лише в кінці (ламатиме published-залежні запити)

**G. Deletes (в кінці; admin delete — чужий `user_id`, напр. guest)**
21. delete review / favorite / news / hangout / top_category / venue
22. `admin_users` → `admin_patch_user` → `admin_delete_user` / `admin_hard_delete_user` (не свій id)

URLs must end with `/`. Bearer `{{access_token}}` на рівні колекції; публічні — No Auth.
