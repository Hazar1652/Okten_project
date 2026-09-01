# Postman

1. Import `Okten.postman_collection.json` and `Okten_Local.postman_environment.json`
2. Select environment **Okten Local** (`base_url` = `http://localhost/api`)
3. Run `register` or `login` — post-response scripts save `access_token` / `refresh_token`
4. Run `get_venues`, `get_tags` — scripts save `venue_id`, `tag_id` for the rest of the requests

Authorization is set on the collection level (Bearer `{{access_token}}`), public endpoints
override it with No Auth.
