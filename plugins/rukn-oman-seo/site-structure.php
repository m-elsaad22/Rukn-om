<?php
/**
 * Site structure helpers for Rukn Oman (also deployed as a Code Snippet).
 * Taxonomies, city/category archives, menu location. Service CPT pages stay live.
 */
if (!defined('ABSPATH')) {
    exit;
}

if (!function_exists('rukn_oman_site_boot')) {
    function rukn_oman_site_boot()
    {
        add_action('init', 'rukn_oman_register_post_tax', 40);
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
