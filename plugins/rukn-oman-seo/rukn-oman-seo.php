<?php
/**
 * Plugin Name: Rukn Oman SEO
 * Description: Titles, unique meta, XML sitemap, robots.txt, English /en/ routes, Oman schema, and hreflang for rukn-eltatawer.com/om.
 * Version: 2.0.6
 * Author: Rukn Eltatawer
 * Text Domain: rukn-oman-seo
 */

if (!defined('ABSPATH')) {
    exit;
}

require_once __DIR__ . '/kayan-blocks.php';
require_once __DIR__ . '/frontend-fix.php';

final class Rukn_Oman_SEO
{
    const LANG_META = '_rukn_lang';
    const PAIR_META = '_rukn_pair_slug';
    const EN_TITLE = '_rukn_en_title';
    const EN_CONTENT = '_rukn_en_content';
    const EN_EXCERPT = '_rukn_en_excerpt';
    const EN_DESC = '_rukn_en_desc';

    public static function init()
    {
        static $done = false;
        if ($done) {
            return;
        }
        $done = true;
        self::serve_static_routes();

        add_action('init', [__CLASS__, 'rewrites'], 20);
        add_action('init', [__CLASS__, 'maybe_flush'], 21);
        add_action('init', [__CLASS__, 'register_meta']);
        add_action('init', [__CLASS__, 'bind_post_taxonomies'], 40);
        add_filter('request', [__CLASS__, 'filter_request']);
        add_action('template_redirect', [__CLASS__, 'early_routes'], -1);
        add_action('template_redirect', [__CLASS__, 'buffer_start'], -999);
        add_filter('the_title', [__CLASS__, 'english_title'], 10, 2);
        add_filter('the_content', [__CLASS__, 'english_content'], 7);
        add_filter('the_content', [__CLASS__, 'single_h1'], 8);
        add_filter('get_the_terms', [__CLASS__, 'hide_uncategorized'], 10, 3);
        add_filter('the_author', [__CLASS__, 'author_name']);
        add_filter('get_the_author_display_name', [__CLASS__, 'author_name']);
        add_action('wp_head', [__CLASS__, 'head_fallback'], 1);
        add_action('rest_api_init', [__CLASS__, 'rest']);
        add_action('admin_init', [__CLASS__, 'ensure_defaults']);
        add_action('save_post', [__CLASS__, 'write_public_files'], 30);
        add_filter('wp_sitemaps_enabled', '__return_false');
    }

    public static function activate()
    {
        self::ensure_defaults();
        self::rewrites();
        flush_rewrite_rules(false);
        self::write_public_files();
        self::purge_cache();
    }

    public static function rewrites()
    {
        add_rewrite_rule('^services/([^/]+)/?$', 'index.php?post_type=services&name=$matches[1]', 'top');
        add_rewrite_rule('^city/([^/]+)/?$', 'index.php?cities=$matches[1]', 'top');
        add_rewrite_rule('^service-category/([^/]+)/?$', 'index.php?service_categories=$matches[1]', 'top');
        add_rewrite_rule('^en/?$', 'index.php?pagename=en-home', 'top');
        add_rewrite_rule('^en/([^/]+)/?$', 'index.php?name=$matches[1]&rukn_en=1', 'top');
        add_rewrite_tag('%rukn_en%', '([0-1])');
    }

    public static function maybe_flush()
    {
        if (get_option('rukn_oman_seo_flush') !== '2.0.2') {
            self::rewrites();
            flush_rewrite_rules(true);
            update_option('rukn_oman_seo_flush', '2.0.2');
            self::write_public_files();
        }
    }

    public static function register_meta()
    {
        $keys = [
            'rank_math_title',
            'rank_math_description',
            self::LANG_META,
            self::PAIR_META,
            self::EN_TITLE,
            self::EN_CONTENT,
            self::EN_EXCERPT,
            self::EN_DESC,
        ];
        foreach (['post', 'page', 'services'] as $type) {
            foreach ($keys as $key) {
                register_post_meta($type, $key, [
                    'show_in_rest' => true,
                    'single' => true,
                    'type' => 'string',
                    'auth_callback' => function () {
                        return current_user_can('edit_posts');
                    },
                ]);
            }
        }
        register_taxonomy_for_object_type('category', 'post');
    }

    public static function bind_post_taxonomies()
    {
        register_taxonomy_for_object_type('cities', 'post');
        register_taxonomy_for_object_type('service_categories', 'post');
        if (taxonomy_exists('category')) {
            register_taxonomy_for_object_type('category', 'post');
        }
    }

    public static function ensure_defaults()
    {
        if (!get_option('blog_public')) {
            update_option('blog_public', '1');
        }
        update_option('timezone_string', 'Asia/Muscat');
        update_option('blogname', 'ركن التطور عُمان');
        update_option(
            'blogdescription',
            'خدمات منزلية متكاملة في سلطنة عُمان: تنظيف، كشف تسربات، عزل، صيانة وتكييف في مسقط وصلالة وباقي المدن.'
        );

        $user = get_user_by('login', 'mahmoud');
        if ($user) {
            wp_update_user([
                'ID' => $user->ID,
                'display_name' => 'فريق ركن التطور',
                'nickname' => 'ركن التطور عُمان',
                'first_name' => 'ركن التطور',
                'last_name' => 'عُمان',
            ]);
        }
    }

    public static function request_path()
    {
        $uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
        $uri = is_string($uri) ? $uri : '/';
        $uri = preg_replace('#^/om(?=/|$)#', '', $uri);
        $path = '/' . ltrim($uri, '/');
        return $path === '//' ? '/' : $path;
    }

    public static function serve_static_routes()
    {
        if (is_admin()) {
            return;
        }
        $uri = $_SERVER['REQUEST_URI'] ?? '';
        if (strpos($uri, 'wp-admin') !== false || strpos($uri, 'wp-login.php') !== false) {
            return;
        }
        $path = rtrim(self::request_path(), '/') . '/';
        if (preg_match('#^/robots\.txt/?$#', $path) || preg_match('#/robots\.txt/?(\?|$)#', $uri)) {
            self::send_robots();
        }
        if (preg_match('#^/(sitemap\.xml|sitemap_index\.xml|wp-sitemap\.xml)/?$#', $path)) {
            // Post types are not ready this early; delay to init.
            add_action('init', [__CLASS__, 'send_sitemap'], 99);
        }
    }

    public static function early_routes()
    {
        if (is_admin() || wp_doing_ajax() || wp_doing_cron()) {
            return;
        }
        $path = rtrim(self::request_path(), '/') . '/';
        if ($path === '//') {
            $path = '/';
        }

        if (preg_match('#^/robots\.txt/?$#', $path)) {
            self::send_robots();
        }
        if (preg_match('#^/(sitemap\.xml|sitemap_index\.xml|wp-sitemap\.xml)/?$#', $path)) {
            self::send_sitemap();
        }
        if (is_page('en-home') && !self::is_english_request()) {
            wp_safe_redirect(home_url('/en/'), 301);
            exit;
        }
        if (preg_match('#^/services/?$#', $path) || is_post_type_archive('services')) {
            wp_safe_redirect(home_url('/our-services/'), 301);
            exit;
        }
        if (preg_match('#^/en/?$#', $path)) {
            self::render_english_home();
        }
        if (preg_match('#^/en/([a-z0-9\-]+)/?$#', $path, $m)) {
            self::render_english_post($m[1]);
        }
        if (preg_match('#^/services/([a-z0-9\-]+)/?$#', $path, $m)) {
            self::render_service($m[1]);
        }
    }

    public static function force_service_query($slug)
    {
        global $wp_query, $wp;
        if ($wp_query instanceof WP_Query && $wp_query->is_singular && isset($wp_query->queried_object->post_type) && $wp_query->queried_object->post_type === 'services') {
            return;
        }
        $found = get_posts([
            'name' => $slug,
            'post_type' => 'services',
            'post_status' => 'publish',
            'numberposts' => 1,
        ]);
        if (!$found) {
            return;
        }
        $post = $found[0];
        $wp_query = new WP_Query([
            'p' => $post->ID,
            'post_type' => 'services',
        ]);
        if (!$wp_query->have_posts()) {
            $wp_query->posts = [$post];
            $wp_query->post_count = 1;
            $wp_query->queried_object = $post;
            $wp_query->queried_object_id = $post->ID;
        }
        $wp_query->is_singular = true;
        $wp_query->is_single = true;
        $wp_query->is_404 = false;
        $wp_query->is_home = false;
        $wp_query->is_front_page = false;
        $wp_query->is_page = false;
        status_header(200);
        if (isset($wp) && is_object($wp)) {
            $wp->query_vars['error'] = '';
            $wp->query_vars['post_type'] = 'services';
            $wp->query_vars['name'] = $slug;
        }
    }

    public static function filter_request($vars)
    {
        $path = rtrim(self::request_path(), '/') . '/';
        if (preg_match('#^/en/?$#', $path)) {
            return ['pagename' => 'en-home'];
        }
        if (preg_match('#^/en/([a-z0-9\-]+)/?$#', $path, $m)) {
            return ['name' => $m[1], 'post_type' => 'post'];
        }
        if (preg_match('#^/services/([a-z0-9\-]+)/?$#', $path, $m)) {
            return [
                'post_type' => 'services',
                'name' => $m[1],
                'services' => $m[1],
            ];
        }
        if (preg_match('#^/city/([a-z0-9\-]+)/?$#', $path, $m)) {
            return ['cities' => $m[1]];
        }
        if (preg_match('#^/service-category/([a-z0-9\-]+)/?$#', $path, $m)) {
            return ['service_categories' => $m[1]];
        }
        return $vars;
    }

    public static function english_title($title, $post_id = 0)
    {
        if (!self::is_english_request() || !$post_id) {
            return $title;
        }
        $en = get_post_meta((int) $post_id, self::EN_TITLE, true);
        return $en ?: $title;
    }

    public static function english_content($content)
    {
        if (!self::is_english_request() || !is_singular()) {
            return $content;
        }
        $post = get_queried_object();
        if (!$post instanceof WP_Post) {
            return $content;
        }
        $en = get_post_meta($post->ID, self::EN_CONTENT, true);
        return $en ?: $content;
    }

    public static function send_robots()
    {
        nocache_headers();
        header('Content-Type: text/plain; charset=UTF-8');
        header('X-Robots-Tag: noindex');
        $home = home_url('/');
        echo "User-agent: *\n";
        echo "Allow: /\n";
        echo "Disallow: /om/wp-admin/\n";
        echo "Allow: /om/wp-admin/admin-ajax.php\n";
        echo "Disallow: /wp-admin/\n";
        echo "Sitemap: {$home}sitemap.xml\n";
        exit;
    }

    public static function sitemap_urls()
    {
        $urls = [];
        $urls[] = [home_url('/'), '1.0', 'daily', gmdate('c')];
        $urls[] = [home_url('/en/'), '0.9', 'daily', gmdate('c')];

        foreach (['cities', 'service_categories'] as $tax) {
            $terms = get_terms(['taxonomy' => $tax, 'hide_empty' => false, 'number' => 50]);
            if (is_wp_error($terms) || !$terms) {
                continue;
            }
            foreach ($terms as $term) {
                $link = get_term_link($term);
                if (!is_wp_error($link)) {
                    $urls[] = [$link, '0.7', 'weekly', gmdate('c')];
                }
            }
        }

        $svcs = get_posts([
            'post_type' => 'services',
            'post_status' => 'publish',
            'numberposts' => 50,
        ]);
        foreach ($svcs as $post) {
            $urls[] = [home_url('/services/' . $post->post_name . '/'), '0.85', 'weekly', get_post_modified_time('c', true, $post)];
        }

        $posts = get_posts([
            'post_type' => ['post', 'page'],
            'post_status' => 'publish',
            'numberposts' => 2500,
            'orderby' => 'modified',
            'order' => 'DESC',
        ]);
        foreach ($posts as $post) {
            if (in_array($post->post_name, ['sample-page', 'hello-world', 'en-home'], true)) {
                continue;
            }
            $lang = get_post_meta($post->ID, self::LANG_META, true);
            if ($lang === 'en') {
                continue;
            }
            if ($post->post_type === 'services') {
                $loc = home_url('/services/' . $post->post_name . '/');
            } else {
                $loc = get_permalink($post);
            }
            $prio = $post->post_type === 'post' ? '0.8' : '0.7';
            $urls[] = [$loc, $prio, 'weekly', get_post_modified_time('c', true, $post)];
            if (get_post_meta($post->ID, self::EN_TITLE, true) && $post->post_type === 'post') {
                $pair = get_post_meta($post->ID, self::PAIR_META, true) ?: $post->post_name;
                $urls[] = [home_url('/en/' . sanitize_title($pair) . '/'), '0.75', 'weekly', get_post_modified_time('c', true, $post)];
            }
        }
        return $urls;
    }

    public static function sitemap_xml()
    {
        $xml = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        $xml .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' . "\n";
        $seen = [];
        foreach (self::sitemap_urls() as $row) {
            $loc = esc_url($row[0]);
            if (isset($seen[$loc])) {
                continue;
            }
            $seen[$loc] = true;
            $xml .= "  <url>\n";
            $xml .= '    <loc>' . $loc . "</loc>\n";
            if (!empty($row[3])) {
                $xml .= '    <lastmod>' . esc_html($row[3]) . "</lastmod>\n";
            }
            $xml .= '    <changefreq>' . esc_html($row[2]) . "</changefreq>\n";
            $xml .= '    <priority>' . esc_html($row[1]) . "</priority>\n";
            $xml .= "  </url>\n";
        }
        $xml .= '</urlset>';
        return $xml;
    }

    public static function send_sitemap()
    {
        nocache_headers();
        header('Content-Type: application/xml; charset=UTF-8');
        echo self::sitemap_xml();
        exit;
    }

    public static function write_public_files()
    {
        if (!defined('ABSPATH')) {
            return;
        }
        $robots = "User-agent: *\nAllow: /\nDisallow: /om/wp-admin/\nAllow: /om/wp-admin/admin-ajax.php\nDisallow: /wp-admin/\nSitemap: " . home_url('/sitemap.xml') . "\n";
        @file_put_contents(ABSPATH . 'robots.txt', $robots);
        if (is_file(ABSPATH . 'sitemap.xml')) {
            @unlink(ABSPATH . 'sitemap.xml');
        }
    }

    public static function english_home_post()
    {
        $q = new WP_Query([
            'post_type' => 'page',
            'name' => 'en-home',
            'post_status' => 'publish',
            'posts_per_page' => 1,
            'no_found_rows' => true,
        ]);
        return $q->have_posts() ? $q->posts[0] : null;
    }

    public static function arabic_by_slug($slug)
    {
        $q = new WP_Query([
            'post_type' => ['post', 'page', 'services'],
            'name' => $slug,
            'post_status' => 'publish',
            'posts_per_page' => 1,
            'no_found_rows' => true,
        ]);
        return $q->have_posts() ? $q->posts[0] : null;
    }

    public static function render_virtual_post(WP_Post $post, $as = 'single')
    {
        status_header(200);
        nocache_headers();
        global $wp_query, $wp;
        $GLOBALS['post'] = $post;
        setup_postdata($post);
        $wp_query->is_single = $as === 'single';
        $wp_query->is_page = $as === 'page';
        $wp_query->is_singular = true;
        $wp_query->is_home = false;
        $wp_query->is_404 = false;
        $wp_query->is_front_page = false;
        $wp_query->queried_object = $post;
        $wp_query->queried_object_id = $post->ID;
        $wp_query->posts = [$post];
        $wp_query->post_count = 1;
        $wp_query->found_posts = 1;
        $wp_query->max_num_pages = 1;
        if (isset($wp) && is_object($wp)) {
            $wp->query_vars['error'] = '';
            $wp->query_vars['p'] = $post->ID;
            $wp->query_vars['post_type'] = $post->post_type;
            $wp->query_vars['name'] = $post->post_name;
            if ($as === 'page') {
                $wp->query_vars['pagename'] = $post->post_name;
            }
        }
    }

    public static function render_english_home()
    {
        $page = self::english_home_post();
        if (!$page) {
            return;
        }
        self::render_virtual_post($page, 'page');
    }

    public static function render_english_post($slug)
    {
        $found = self::arabic_by_slug($slug);
        if (!$found) {
            return;
        }
        $en_title = get_post_meta($found->ID, self::EN_TITLE, true);
        $en_content = get_post_meta($found->ID, self::EN_CONTENT, true);
        if (!$en_title || !$en_content) {
            return;
        }
        $virtual = clone $found;
        $virtual->post_title = $en_title;
        $virtual->post_content = $en_content;
        $virtual->post_excerpt = get_post_meta($found->ID, self::EN_EXCERPT, true) ?: wp_trim_words(wp_strip_all_tags($en_content), 28);
        $virtual->filter = 'raw';
        self::render_virtual_post($virtual, $found->post_type === 'page' ? 'page' : 'single');
    }

    public static function render_service($slug)
    {
        $q = new WP_Query([
            'post_type' => 'services',
            'name' => $slug,
            'post_status' => 'publish',
            'posts_per_page' => 1,
            'no_found_rows' => true,
        ]);
        if (!$q->have_posts()) {
            return;
        }
        self::render_virtual_post($q->posts[0], 'single');
    }

    public static function is_english_request()
    {
        return (bool) preg_match('#^/en(/|$)#', self::request_path());
    }

    public static function seo_for_current()
    {
        $en = self::is_english_request();
        $site_ar = 'ركن التطور عُمان';
        $site_en = 'Rukn Eltatawer Oman';
        $home_ar = 'ركن التطور عُمان | تنظيف وصيانة وكشف تسربات في مسقط وصلالة وكل مدن السلطنة';
        $home_en = 'Rukn Eltatawer Oman | Cleaning, leak detection and home maintenance in Muscat, Salalah and all Oman cities';
        $desc_ar = 'شركة خدمات منزلية في سلطنة عُمان: تنظيف منازل، كشف تسربات بدون تكسير، عزل أسطح، صيانة وتكييف. فريق مقيم وعرض سعر بالريال العُماني قبل التنفيذ.';
        $desc_en = 'Home services across the Sultanate of Oman: house cleaning, non-destructive leak detection, roof insulation, AC and general maintenance. On-site diagnosis and a written OMR quote before work starts.';

        if (is_front_page() && !$en) {
            return [
                'title' => $home_ar,
                'desc' => $desc_ar,
                'canonical' => home_url('/'),
                'lang' => 'ar-OM',
                'hreflang' => [['ar-OM', home_url('/')], ['en-OM', home_url('/en/')], ['x-default', home_url('/')]],
            ];
        }
        if ($en && preg_match('#^/en/?$#', rtrim(self::request_path(), '/') . '/')) {
            $page = self::english_home_post();
            return [
                'title' => $page ? (get_post_meta($page->ID, 'rank_math_title', true) ?: $home_en) : $home_en,
                'desc' => $page ? (get_post_meta($page->ID, 'rank_math_description', true) ?: $desc_en) : $desc_en,
                'canonical' => home_url('/en/'),
                'lang' => 'en-OM',
                'hreflang' => [['ar-OM', home_url('/')], ['en-OM', home_url('/en/')], ['x-default', home_url('/')]],
            ];
        }

        $obj = get_queried_object();
        if ($obj instanceof WP_Term) {
            $link = get_term_link($obj);
            if (is_wp_error($link)) {
                $link = home_url('/');
            }
            $desc = wp_strip_all_tags($obj->description ?: '');
            if ($obj->taxonomy === 'cities') {
                $title = $en
                    ? ($obj->name . ' | Home services in Oman | ' . $site_en)
                    : ('خدمات ركن التطور في ' . $obj->name . ' | ' . $site_ar);
                $desc = $desc ?: ($en
                    ? ('Field team in ' . $obj->name . ', Sultanate of Oman. Cleaning, leak detection, AC, plumbing and maintenance. Written OMR quote after a site visit.')
                    : ('فريق ركن التطور في ' . $obj->name . ' داخل سلطنة عُمان: تنظيف، كشف تسربات، تكييف، سباكة وصيانة. المعاينة ثم سعر بالريال العُماني.'));
            } else {
                $title = $en
                    ? ($obj->name . ' | ' . $site_en)
                    : ($obj->name . ' | ' . $site_ar);
                $desc = $desc ?: ($en ? $desc_en : $desc_ar);
            }
            return [
                'title' => $title,
                'desc' => wp_html_excerpt($desc, 160),
                'canonical' => $link,
                'lang' => $en ? 'en-OM' : 'ar-OM',
                'hreflang' => [['ar-OM', $link], ['x-default', $link]],
            ];
        }

        $post = $obj;
        if ($post instanceof WP_Post) {
            $title_meta = get_post_meta($post->ID, $en ? self::EN_TITLE : 'rank_math_title', true);
            if ($en) {
                $desc_meta = get_post_meta($post->ID, self::EN_DESC, true);
                if (!$desc_meta) {
                    $en_title_only = get_post_meta($post->ID, self::EN_TITLE, true);
                    if ($en_title_only) {
                        $desc_meta = wp_html_excerpt($en_title_only . '. On-site survey and a written OMR quote.', 160);
                    }
                }
            } else {
                $desc_meta = get_post_meta($post->ID, 'rank_math_description', true);
            }
            $excerpt = $en
                ? wp_strip_all_tags(get_post_meta($post->ID, self::EN_EXCERPT, true) ?: ($desc_meta ?: ''))
                : wp_strip_all_tags($post->post_excerpt ?: wp_trim_words($post->post_content, 28));
            $pair = get_post_meta($post->ID, self::PAIR_META, true) ?: $post->post_name;
            $ar_url = $post->post_type === 'services'
                ? home_url('/services/' . $post->post_name . '/')
                : home_url('/' . sanitize_title($pair) . '/');
            $en_url = home_url('/en/' . sanitize_title($pair) . '/');
            $canonical = $en ? $en_url : $ar_url;
            if ($en) {
                $title = ($title_meta ?: $post->post_title) . ' | ' . $site_en;
            } else {
                $title = $title_meta ?: ($post->post_title . ' | ' . $site_ar);
            }
            $hreflang = [['ar-OM', $ar_url], ['x-default', $ar_url]];
            if (get_post_meta($post->ID, self::EN_TITLE, true) && $post->post_type === 'post') {
                $hreflang = [['ar-OM', $ar_url], ['en-OM', $en_url], ['x-default', $ar_url]];
            }
            return [
                'title' => $title,
                'desc' => $desc_meta ?: ($excerpt ?: ($en ? $desc_en : $desc_ar)),
                'canonical' => $canonical,
                'lang' => $en ? 'en-OM' : 'ar-OM',
                'hreflang' => $hreflang,
            ];
        }

        return [
            'title' => $en ? $home_en : $home_ar,
            'desc' => $en ? $desc_en : $desc_ar,
            'canonical' => home_url('/'),
            'lang' => $en ? 'en-OM' : 'ar-OM',
            'hreflang' => [['ar-OM', home_url('/')], ['en-OM', home_url('/en/')], ['x-default', home_url('/')]],
        ];
    }

    public static function buffer_start()
    {
        if (is_admin() || wp_doing_ajax() || (defined('WP_CLI') && WP_CLI)) {
            return;
        }
        $uri = $_SERVER['REQUEST_URI'] ?? '';
        if (strpos($uri, '/wp-json/') !== false || isset($_GET['rest_route'])) {
            return;
        }
        static $started = false;
        if ($started) {
            return;
        }
        $started = true;
        ob_start([__CLASS__, 'buffer_end']);
    }

    public static function buffer_end($html)
    {
        if (!is_string($html) || strpos($html, '<html') === false) {
            return $html;
        }
        $seo = self::seo_for_current();
        $title = esc_html($seo['title']);
        $desc = esc_attr($seo['desc']);
        $canon = esc_url($seo['canonical']);
        $lang = esc_attr($seo['lang']);
        $dir = strpos($lang, 'ar') === 0 ? 'rtl' : 'ltr';

        $html = preg_replace('/<html\b[^>]*>/i', '<html lang="' . $lang . '" dir="' . $dir . '">', $html, 1);
        if (preg_match('/<title>.*<\/title>/is', $html)) {
            $html = preg_replace('/<title>.*<\/title>/is', '<title>' . $title . '</title>', $html, 1);
        } else {
            $html = preg_replace('/<head[^>]*>/i', '$0<title>' . $title . '</title>', $html, 1);
        }

        $html = preg_replace('/<meta\s+name=["\']description["\'][^>]*>/i', '', $html);
        $html = preg_replace('/<link\s+rel=["\']canonical["\'][^>]*>/i', '', $html);
        $html = preg_replace('/<link\s+rel=["\']alternate["\'][^>]*hreflang[^>]*>/i', '', $html);
        $html = preg_replace('/<link\s+rel=["\']sitemap["\'][^>]*>/i', '', $html);
        $html = preg_replace('/<meta\s+property=["\']og:(title|description|url|locale|type|site_name)["\'][^>]*>/i', '', $html);
        $html = preg_replace('/<meta\s+name=["\']robots["\'][^>]*>/i', '', $html);

        $extra = "\n<meta name=\"description\" content=\"{$desc}\" />\n";
        $extra .= '<link rel="canonical" href="' . $canon . "\" />\n";
        $extra .= '<link rel="sitemap" type="application/xml" href="' . esc_url(home_url('/sitemap.xml')) . "\" />\n";
        $extra .= '<meta name="robots" content="index, follow, max-image-preview:large" />' . "\n";
        $extra .= '<meta property="og:type" content="' . (is_singular() ? 'article' : 'website') . "\" />\n";
        $extra .= '<meta property="og:site_name" content="' . ($seo['lang'] === 'en-OM' ? 'Rukn Eltatawer Oman' : 'ركن التطور عُمان') . "\" />\n";
        $extra .= '<meta property="og:title" content="' . $title . "\" />\n";
        $extra .= '<meta property="og:description" content="' . $desc . "\" />\n";
        $extra .= '<meta property="og:url" content="' . $canon . "\" />\n";
        $extra .= '<meta property="og:locale" content="' . ($seo['lang'] === 'en-OM' ? 'en_OM' : 'ar_OM') . "\" />\n";
        $extra .= '<meta property="og:locale:alternate" content="' . ($seo['lang'] === 'en-OM' ? 'ar_OM' : 'en_OM') . "\" />\n";
        $extra .= '<meta name="twitter:card" content="summary_large_image" />' . "\n";
        $extra .= '<meta name="twitter:title" content="' . $title . "\" />\n";
        $extra .= '<meta name="twitter:description" content="' . $desc . "\" />\n";
        foreach ($seo['hreflang'] as $pair) {
            $extra .= '<link rel="alternate" hreflang="' . esc_attr($pair[0]) . '" href="' . esc_url($pair[1]) . "\" />\n";
        }
        $extra .= self::schema_json($seo);
        $html = preg_replace('/<title>.*<\/title>/is', '$0' . $extra, $html, 1);

        $post = get_queried_object();
        if ($seo['lang'] === 'en-OM' && $post instanceof WP_Post) {
            $en_h1 = get_post_meta($post->ID, self::EN_TITLE, true) ?: $post->post_title;
            if (is_page('en-home') || self::request_path() === '/en/' || self::request_path() === '/en') {
                $en_h1 = $post->post_title;
            }
            $html = preg_replace('/<h1(\b[^>]*)>.*?<\/h1>/is', '<h1$1>' . esc_html($en_h1) . '</h1>', $html, 1);
        }

        $html = str_replace('اختر الإمارة', 'اختر المدينة', $html);
        $html = str_replace('خريطة الإمارات', 'خريطة مدن عُمان', $html);
        $html = str_replace('الإمارات العربية المتحدة', 'سلطنة عُمان', $html);
        $html = preg_replace('/\bUncategorized\b/u', 'خدمات التنظيف', $html);
        $html = preg_replace('/غير مصنف/u', 'خدمات التنظيف', $html);
        $html = preg_replace('/MAHMOUD[^<]{0,24}/u', 'فريق ركن التطور', $html);
        $html = str_replace('&raquo; ', '', $html);
        $html = str_replace('» ', '', $html);
        if (class_exists('Rukn_Oman_Frontend')) {
            $html = Rukn_Oman_Frontend::rewrite($html);
        }
        $html = str_replace(',}</script>', '}</script>', $html);
        return $html;
    }

    public static function schema_json($seo)
    {
        $phone = '+971586634710';
        $graph = [
            [
                '@type' => 'LocalBusiness',
                '@id' => home_url('/#business'),
                'name' => 'ركن التطور عُمان',
                'alternateName' => 'Rukn Eltatawer Oman',
                'url' => home_url('/'),
                'telephone' => $phone,
                'areaServed' => [
                    '@type' => 'Country',
                    'name' => 'Oman',
                ],
                'address' => [
                    '@type' => 'PostalAddress',
                    'addressCountry' => 'OM',
                    'addressLocality' => 'Muscat',
                ],
                'priceRange' => 'OMR',
                'availableLanguage' => ['Arabic', 'English'],
            ],
            [
                '@type' => 'WebSite',
                '@id' => home_url('/#website'),
                'url' => home_url('/'),
                'name' => 'ركن التطور عُمان',
                'inLanguage' => ['ar-OM', 'en-OM'],
                'publisher' => ['@id' => home_url('/#business')],
            ],
        ];
        $post = get_queried_object();
        if ($post instanceof WP_Post && is_singular()) {
            $graph[] = [
                '@type' => 'Article',
                '@id' => $seo['canonical'] . '#article',
                'headline' => $seo['title'],
                'description' => $seo['desc'],
                'inLanguage' => $seo['lang'],
                'mainEntityOfPage' => $seo['canonical'],
                'author' => [
                    '@type' => 'Organization',
                    'name' => 'ركن التطور عُمان',
                ],
                'publisher' => ['@id' => home_url('/#business')],
                'dateModified' => get_post_modified_time('c', true, $post),
            ];
        }
        $schema = ['@context' => 'https://schema.org', '@graph' => $graph];
        $json = wp_json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        return '<script type="application/ld+json">' . $json . "</script>\n";
    }

    public static function head_fallback()
    {
        // Buffer handles the public head.
    }

    public static function single_h1($content)
    {
        if (!is_singular() || !is_string($content)) {
            return $content;
        }
        $content = preg_replace('/<h1(\b[^>]*)>/i', '<h2$1>', $content, 1);
        $content = preg_replace('/<\/h1>/i', '</h2>', $content, 1);
        return $content;
    }

    public static function hide_uncategorized($terms, $post_id, $taxonomy)
    {
        if ($taxonomy !== 'category' || !is_array($terms)) {
            return $terms;
        }
        return array_values(array_filter($terms, function ($term) {
            return is_object($term) && !in_array($term->slug, ['uncategorized', 'غير-مصنف'], true);
        }));
    }

    public static function author_name($name)
    {
        if (is_string($name) && (stripos($name, 'MAHMOUD') !== false || strpos($name, 'Ȝ') !== false)) {
            return self::is_english_request() ? 'Rukn Eltatawer team' : 'فريق ركن التطور';
        }
        return $name;
    }

    public static function purge_cache()
    {
        if (function_exists('do_action')) {
            do_action('litespeed_purge_all');
        }
        if (class_exists('LiteSpeed\Purge') && method_exists('LiteSpeed\Purge', 'purge_all')) {
            \LiteSpeed\Purge::purge_all();
        }
    }

    public static function bulk_fix()
    {
        global $wpdb;
        update_option('default_comment_status', 'closed');
        update_option('default_ping_status', 'closed');
        $comments = $wpdb->query(
            "UPDATE {$wpdb->posts} SET comment_status='closed', ping_status='closed' "
            . "WHERE post_type IN ('post','page','services') "
            . "AND post_status IN ('publish','future','draft','private')"
        );

        $cleaning = 'cleaning|steriliz|marble-polish|moquette|sofa-cleaning|curtain-cleaning|mattress-cleaning|glass-facade';
        $featured = $wpdb->query(
            "UPDATE {$wpdb->postmeta} m "
            . "INNER JOIN {$wpdb->posts} p ON p.ID = m.post_id "
            . "SET m.meta_value = '245' "
            . "WHERE m.meta_key = '_thumbnail_id' AND m.meta_value IN ('246','0') "
            . "AND p.post_type = 'post' AND p.post_name NOT REGEXP '{$cleaning}'"
        );

        $en_fixed = 0;
        $ids = $wpdb->get_col(
            "SELECT ID FROM {$wpdb->posts} WHERE post_type = 'post' AND post_status = 'publish' LIMIT 2500"
        );
        foreach ($ids as $id) {
            $id = (int) $id;
            $en = (string) get_post_meta($id, self::EN_TITLE, true);
            if ($en !== '' && !preg_match('/\p{Arabic}/u', $en)) {
                continue;
            }
            $slug = (string) get_post_field('post_name', $id);
            $words = preg_replace('/-(muscat|salalah|nizwa|sohar|sur|al-buraimi|ibri|rustaq)$/', '', $slug);
            $title = ucwords(str_replace('-', ' ', (string) $words)) . ' in Oman';
            $html = '<section><h2>' . esc_html($title) . '</h2><p>Rukn Eltatawer provides this service in the Sultanate of Oman. Site visit first, then a written OMR quote. Message WhatsApp 971586634710.</p>'
                . '<p><a href="https://wa.me/971586634710" rel="noopener">WhatsApp</a></p></section>';
            $desc = wp_html_excerpt($title . '. Site visit then a written OMR quote.', 160);
            update_post_meta($id, self::EN_TITLE, $title);
            update_post_meta($id, self::EN_CONTENT, $html);
            update_post_meta($id, self::EN_EXCERPT, $desc);
            update_post_meta($id, self::EN_DESC, $desc);
            update_post_meta($id, self::LANG_META, 'ar');
            update_post_meta($id, self::PAIR_META, $slug);
            $en_fixed++;
        }

        self::ensure_defaults();
        self::rewrites();
        flush_rewrite_rules(false);
        update_option('rukn_oman_seo_flush', '2.0.2');
        self::write_public_files();
        self::purge_cache();
        return [
            'ok' => true,
            'comments_closed' => (int) $comments,
            'featured_remapped' => (int) $featured,
            'english_fixed' => $en_fixed,
            'sitemap' => home_url('/sitemap.xml'),
        ];
    }

    public static function rest()
    {
        $can = function () {
            return current_user_can('manage_options');
        };
        register_rest_route('rukn-seo/v1', '/rebuild', [
            'methods' => 'POST',
            'permission_callback' => $can,
            'callback' => function () {
                self::ensure_defaults();
                self::write_public_files();
                self::purge_cache();
                return [
                    'ok' => true,
                    'sitemap' => home_url('/sitemap.xml'),
                    'robots' => home_url('/robots.txt'),
                ];
            },
        ]);
        register_rest_route('rukn-seo/v1', '/bulk-fix', [
            'methods' => 'POST',
            'permission_callback' => $can,
            'callback' => [__CLASS__, 'bulk_fix'],
        ]);
    }
}

add_action('plugins_loaded', ['Rukn_Oman_SEO', 'init']);
if (did_action('plugins_loaded')) {
    Rukn_Oman_SEO::init();
}
Rukn_Oman_SEO::buffer_start();
if (function_exists('register_activation_hook')) {
    register_activation_hook(__FILE__, ['Rukn_Oman_SEO', 'activate']);
}
