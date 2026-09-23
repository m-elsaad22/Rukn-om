# How to find the exact meta keys for `[post_features]` and friends

The five shortcodes in the post body are **live Kayan (YourColor) shortcodes**. They do not read ACF field names such as `features_field`. They read nested PHP-serialized post meta that the theme writes from the metaboxes at the bottom of the post editor.

This site’s keys were confirmed from `post.php` on published articles. Use the steps below to re-check on your dashboard before `--apply`.

## Confirmed mapping (Rukn Oman / Kayan)

| Shortcode in content | Dashboard metabox | Root meta key | Nested fields the script writes |
|---|---|---|---|
| `[post_features]` | مميزات المقال (`YC__CFM-yourcolor__features_short_code`) | `post__features__data` | `features__title`, `features__content`, `yourcolor__post_features[][title\|content\|icon]` |
| `[post_steps]` | خطوات العمل (`YC__CFM-yourcolor__work_steps_short_code`) | `post__work_steps__data` | `work_steps__title`, `work_steps__content`, `work_steps_items[][title\|content]` |
| `[post_prices]` | قائمة الأسعار (`YC__CFM-yourcolor__price_list_short_code`) | `post__price_list__data` | `price_list__title`, `price_list__content`, `price_list__table_title1/2`, `price_list__items[][title\|value]` |
| `[post_services]` | خدمات مرتبطة (`YC__CFM-yourcolor__post_services_short_code`) | `post__services__data` | `services__title`, `services__content`, `post_services_items[][title\|content\|image\|image_id]` |
| `[post_call]` | قسم الاتصال (`YC__CFM-yourcolor__post_call_short_code`) | `post__call_section__data` | `call_section_title`, `call_section_content`, `call_section_phone`, `call_section_whatsapp` |

Related hide checkboxes (must stay **empty**, not `on`, or the shortcode renders nothing):

- `hide_features__section`
- `hide_work_steps`
- `hide_price_list__section`
- `hide_services_section`
- `hide_call_section`

Call / WhatsApp policy on this site: keep `call_section_whatsapp=971586634710`, leave `call_section_phone` empty, do not add `tel:` CTAs.

## Method 1 — Inspect the post editor (fastest)

1. wp-admin → **Posts → All Posts** → open any city-service article (example: تركيب عرائش خشبية في البريمي).
2. Scroll to the bottom of the editor, below Rank Math. You should see Kayan boxes titled roughly: المميزات، خطوات العمل، قائمة الأسعار، الخدمات، قسم الاتصال.
3. Right-click a title or row input → **Inspect**.
4. In the HTML, copy the `name="..."` attribute. Kayan uses PHP array names, for example:

```html
<input name="post__features__data[features__title]" />
<input name="post__features__data[yourcolor__post_features][0][title]" />
<input name="post__features__data[yourcolor__post_features][0][icon]" />
<input name="post__work_steps__data[work_steps_items][0][title]" />
<input name="post__price_list__data[price_list__items][0][value]" />
<input name="post__services__data[post_services_items][0][title]" />
<input name="post__call_section__data[call_section_whatsapp]" />
```

5. The **root meta key** is the part before the first `[` (`post__features__data`). That is what `update_post_meta()` stores as a serialized array.

## Method 2 — Custom Fields panel (shows the root keys)

1. On the same edit screen, open **Screen Options** (top right).
2. Enable **Custom Fields**.
3. Reload. A “Custom Fields” box appears at the bottom.
4. Look for keys exactly named `post__features__data`, `post__work_steps__data`, `post__price_list__data`, `post__services__data`, `post__call_section__data`.
5. Values look like `a:3:{s:16:"features__title";...}` (PHP serialization). Do not paste HTML into that blob by hand.

If those keys are missing, the boxes are empty for that post — that is the gap this script fills.

## Method 3 — View-source search

1. On `post.php?post=ID&action=edit`, use the browser **View page source**.
2. Search for `name="post__features__data` or `YC__CFM-yourcolor__`.
3. Every `name="post__…"` is a meta path.

## Method 4 — ACF (only if you actually use ACF)

This theme is **not** ACF. Skip this unless you installed Advanced Custom Fields yourself.

1. **ACF → Field Groups** → open the group attached to Posts.
2. The REST / script name is the **Field Name** (slug), never the **Field Label**.
3. If “Show in REST API” is on, core `PUT /wp/v2/posts/{id}` accepts `{ "acf": { "field_name": "..." } }` or `{ "meta": { "field_name": "..." } }` depending on ACF version.
4. Put those slugs in `.env`:

```bash
WRITE_MODE=acf
FEATURES_META_KEY=features_field
STEPS_META_KEY=steps_field
PRICES_META_KEY=prices_field
SERVICES_META_KEY=services_field
CALL_META_KEY=call_action_field
```

Then run with `--write-mode acf`.

## Method 5 — Let the script print the keys

```bash
python3 scripts/fill_kayan_fields.py --inspect-keys --post-id 1204
```

Needs `WP_USER` + `WP_APP_PASSWORD`. Adding `WP_ADMIN_PASSWORD` also dumps every `name="post__*"` from the editor HTML.

## Why core REST GET looks empty

`GET /wp-json/wp/v2/posts/{id}?context=edit` only returns meta that was registered with `show_in_rest`. Rank Math and `_rukn_*` appear. Kayan keys do not. That does **not** mean the fields are unwritable.

This site’s writer is:

```http
POST /wp-json/rukn/v1/article/{id}
{"meta": {"post__features__data": { ... }, ...}}
```

Core `PUT /wp/v2/posts/{id}` with a `meta` object will silently drop unregistered Kayan keys.

## Empty vs filled

A post can have the five shortcodes in the **raw** content and still be filled: the theme expands them at render time when the nested meta is present.

Treat a post as empty when:

- the Custom Fields value for `post__features__data` is missing, or `features__title` is blank, or
- the public HTML still contains the literal string `[post_features]`.

The script’s `--empty-only` (default) skips posts whose public HTML already expanded those shortcodes.

## How to run (after you confirm the keys)

```bash
cp .env.example .env   # then fill WP_APP_PASSWORD and OPENAI_API_KEY or GEMINI_API_KEY

python3 scripts/fill_kayan_fields.py --inspect-keys --post-id 1204
python3 scripts/fill_kayan_fields.py --dry-run --offline --limit 3
python3 scripts/fill_kayan_fields.py --dry-run --provider openai --limit 2
python3 scripts/fill_kayan_fields.py --apply --empty-only --limit 5 --provider openai
```

`--apply` is required to write. `--empty-only` skips posts whose public HTML already expanded the shortcodes. `--force` overwrites. WhatsApp stays `971586634710`; the phone field is left empty.

Progress: `fill-kayan-progress.json` + `fill-kayan-progress.jsonl` (gitignored). Resume with `--resume`.
