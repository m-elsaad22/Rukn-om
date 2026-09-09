<?php
/**
 * Site structure helpers for Rukn Oman (also deployed as a Code Snippet).
 * Registers post taxonomies, fixes /services/ 500s, and assigns the main menu.
 */
if (!defined('ABSPATH')) {
    exit;
}

if (!function_exists('rukn_oman_site_boot')) {
    function rukn_oman_site_boot()
    {
        add_action('init', 'rukn_oman_register_post_tax', 40);
        add_action('template_redirect', 'rukn_oman_fix_service_urls', -5);
        add_action('pre_get_posts', 'rukn_oman_tax_archives');
        add_filter('theme_mod_nav_menu_locations', 'rukn_oman_menu_location');
    }

    function rukn_oman_register_post_tax()
    {
        register_taxonomy_for_object_type('cities', 'post');
        register_taxonomy_for_object_type('service_categories', 'post');
        if (taxonomy_exists('category')) {
            register_taxonomy_for_object_type('category', 'post');
        }
    }

    function rukn_oman_fix_service_urls()
    {
        if (is_admin() || wp_doing_ajax() || wp_doing_cron()) {
            return;
        }
        $uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
        $uri = is_string($uri) ? $uri : '/';
        $path = '/' . ltrim(preg_replace('#^/om(?=/|$)#', '', $uri), '/');
        $path = rtrim($path, '/') . '/';
        if (preg_match('#^/services/?$#', $path) || is_post_type_archive('services')) {
            wp_safe_redirect(home_url('/our-services/'), 301);
            exit;
        }
        if (preg_match('#^/services/([a-z0-9\-]+)/?$#', $path, $m)) {
            $muscat = get_page_by_path($m[1] . '-muscat', OBJECT, 'post');
            if ($muscat && $muscat->post_status === 'publish') {
                wp_safe_redirect(get_permalink($muscat), 301);
                exit;
            }
            wp_safe_redirect(home_url('/our-services/'), 301);
            exit;
        }
    }

    function rukn_oman_tax_archives($q)
    {
        if (is_admin() || !$q->is_main_query()) {
            return;
        }
        if ($q->is_tax('cities') || $q->is_tax('service_categories')) {
            $q->set('post_type', ['post', 'services']);
            $q->set('posts_per_page', 24);
        }
    }

    function rukn_oman_menu_location($locs)
    {
        if (!is_array($locs)) {
            $locs = [];
        }
        $id = (int) get_option('rukn_main_menu_id');
        if ($id) {
            $locs['main-menu'] = $id;
        }
        return $locs;
    }

    rukn_oman_site_boot();
}
