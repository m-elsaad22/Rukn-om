<?php
/**
 * REST writer for Kayan post blocks (FAQ, features, steps, services, prices, call, schema).
 */
if (!defined('ABSPATH')) {
    exit;
}

if (!function_exists('rukn_oman_kayan_allowed_meta')) {
    function rukn_oman_kayan_allowed_meta(): array
    {
        return [
            'yourcolor__faqs',
            'post__features__data',
            'post__work_steps__data',
            'post__services__data',
            'post__price_list__data',
            'post__call_section__data',
            'post__card__data',
            'post__popover__data',
            'post__service_request__data',
            'YourColor_Service',
            'YourColor_Article',
            'YourColor_ImageObject',
            'phone_number',
            'whatsapp_number',
            'references',
            'rank_math_title',
            'rank_math_description',
            'rank_math_focus_keyword',
            'rank_math_canonical_url',
            'rank_math_robots',
            'rank_math_facebook_title',
            'rank_math_facebook_description',
            'rank_math_twitter_title',
            'rank_math_twitter_description',
            '_rukn_lang',
            '_rukn_pair_slug',
            '_rukn_en_title',
            '_rukn_en_content',
            '_rukn_en_excerpt',
            '_rukn_en_desc',
            '_rukn_article_ver',
            'hide_features__section',
            'hide_work_steps',
            'hide_services_section',
            'hide_price_list__section',
            'hide_call_section',
            'hide_post_gallery',
            'hide__post_card',
            'title_post_gallery',
            'content_post_gallery',
        ];
    }

    function rukn_oman_kayan_save_article(WP_REST_Request $req)
    {
        $id = (int) $req['id'];
        $post = get_post($id);
        if (!$post || $post->post_type !== 'post') {
            return new WP_Error('not_found', 'Post not found', ['status' => 404]);
        }

        $update = ['ID' => $id];
        $content = $req->get_param('content');
        $excerpt = $req->get_param('excerpt');
        if (is_string($content)) {
            $update['post_content'] = $content;
        }
        if (is_string($excerpt)) {
            $update['post_excerpt'] = $excerpt;
        }
        if (count($update) > 1) {
            $result = wp_update_post($update, true);
            if (is_wp_error($result)) {
                return $result;
            }
        }

        $meta = $req->get_param('meta');
        $allowed = array_flip(rukn_oman_kayan_allowed_meta());
        if (is_array($meta)) {
            foreach ($meta as $key => $value) {
                if (!is_string($key) || !isset($allowed[$key])) {
                    continue;
                }
                update_post_meta($id, $key, $value);
            }
        }

        $tags = $req->get_param('tags');
        if (is_array($tags)) {
            $clean = array_values(array_filter(array_map('strval', $tags)));
            wp_set_post_terms($id, $clean, 'post_tag', false);
        }

        return [
            'ok' => true,
            'id' => $id,
            'link' => get_permalink($id),
        ];
    }

    add_action('rest_api_init', function () {
        register_rest_route('rukn/v1', '/article/(?P<id>\d+)', [
            'methods' => 'POST',
            'permission_callback' => function () {
                return current_user_can('edit_posts');
            },
            'callback' => 'rukn_oman_kayan_save_article',
            'args' => [
                'id' => ['required' => true],
            ],
        ]);
    });
}
