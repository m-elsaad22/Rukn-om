<?php
/**
 * Front-end repairs for Kayan + Oman IA: menus, 404s, call hide, HTML rewrites.
 */
if (!defined('ABSPATH')) {
    exit;
}

final class Rukn_Oman_Frontend
{
    const WA = '971586634710';
    const WA_HREF = 'https://wa.me/971586634710';

    public static function init()
    {
        add_action('template_redirect', [__CLASS__, 'routes'], -20);
        add_action('template_redirect', [__CLASS__, 'stop_soft_404'], 0);
        add_action('template_redirect', [__CLASS__, 'serve_real_404'], 1);
        add_action('pre_get_posts', [__CLASS__, 'tax_archives']);
        add_filter('theme_mod_nav_menu_locations', [__CLASS__, 'menu_location']);
        add_filter('body_class', [__CLASS__, 'body_class']);
        add_action('wp_head', [__CLASS__, 'head_css'], 99);
        add_action('wp_footer', [__CLASS__, 'footer_js'], 1);
        add_filter('comments_open', '__return_false', 99);
        add_filter('pings_open', '__return_false', 99);
        add_filter('get_comments_number', static function () {
            return 0;
        }, 99);
        add_filter('rank_math/frontend/disable_adjacent_rel_links', '__return_true');
        add_filter('wpseo_next_rel_link', '__return_false');
        add_filter('wpseo_prev_rel_link', '__return_false');
        add_filter('do_redirect_guess_404_permalink', '__return_false');
        add_filter('redirect_canonical', [__CLASS__, 'stop_canonical'], 0, 2);
        add_filter('wp_redirect', [__CLASS__, 'block_home_404_redirect'], 0, 2);
        add_filter('rank_math/redirection/fallback_404', '__return_false');
        add_action('init', [__CLASS__, 'disable_404_home_redirect'], 6);
        add_action('wp', [__CLASS__, 'noindex_paged_home']);
    }

    public static function disable_404_home_redirect()
    {
        $gen = get_option('rank-math-options-general');
        if (!is_array($gen)) {
            return;
        }
        $keys = ['fallback', 'fallback_behavior', 'redirections_fallback', '404_redirect'];
        $changed = false;
        foreach ($keys as $key) {
            if (!empty($gen[$key]) && !in_array($gen[$key], ['default', 'off', ''], true)) {
                $gen[$key] = 'default';
                $changed = true;
            }
        }
        if ($changed) {
            update_option('rank-math-options-general', $gen);
        }
    }

    public static function stop_canonical($redirect, $requested)
    {
        $path = rtrim(self::path(), '/') . '/';
        if (preg_match('#^/(city|service-category|services|en)(/|$)#', $path)) {
            return false;
        }
        if (is_404()) {
            return false;
        }
        return $redirect;
    }

    public static function block_home_404_redirect($location, $status)
    {
        if (is_admin() || wp_doing_ajax() || wp_doing_cron()) {
            return $location;
        }
        if (!in_array((int) $status, [301, 302, 303, 307, 308], true)) {
            return $location;
        }
        $path = rtrim(self::path(), '/') . '/';
        if ($path === '//' || $path === '') {
            $path = '/';
        }
        if (preg_match('#^/(contact-us|blog|page/\d+)/?$#', $path)) {
            return $location;
        }
        $dest = parse_url((string) $location, PHP_URL_PATH);
        $dest = is_string($dest) ? $dest : '/';
        $dest = preg_replace('#^/om(?=/|$)#', '', $dest);
        $dest = '/' . ltrim($dest, '/');
        $dest = rtrim($dest, '/') . '/';
        if ($dest === '//') {
            $dest = '/';
        }
        if ($dest === '/' && $path !== '/') {
            if (preg_match('#^/(city|service-category|services|en)/#', $path) || is_404()) {
                return false;
            }
        }
        return $location;
    }

    public static function path()
    {
        if (class_exists('Rukn_Oman_SEO')) {
            return Rukn_Oman_SEO::request_path();
        }
        $uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
        $uri = is_string($uri) ? $uri : '/';
        $uri = preg_replace('#^/om(?=/|$)#', '', $uri);
        $path = '/' . ltrim($uri, '/');
        return $path === '//' ? '/' : $path;
    }

    public static function routes()
    {
        if (is_admin() || wp_doing_ajax() || wp_doing_cron()) {
            return;
        }
        $path = rtrim(self::path(), '/') . '/';
        if ($path === '//') {
            $path = '/';
        }

        if (preg_match('#^/contact-us/?$#', $path)) {
            wp_safe_redirect(home_url('/contact/'), 301);
            exit;
        }
        if (preg_match('#^/blog/?$#', $path)) {
            wp_safe_redirect(home_url('/html-sitemap/'), 301);
            exit;
        }
        if (preg_match('#^/page/(\d+)/?$#', $path)) {
            wp_safe_redirect(home_url('/'), 301);
            exit;
        }
        if (class_exists('Rukn_Oman_SEO') && Rukn_Oman_SEO::is_english_request()) {
            if (preg_match('#^/en/?$#', $path)) {
                Rukn_Oman_SEO::render_english_home();
            }
            if (preg_match('#^/en/([a-z0-9\-]+)/?$#', $path, $m)) {
                Rukn_Oman_SEO::render_english_post($m[1]);
            }
        }
        if (preg_match('#^/services/([a-z0-9\-]+)/?$#', $path, $m) && class_exists('Rukn_Oman_SEO')) {
            Rukn_Oman_SEO::render_service($m[1]);
        }
        if (preg_match('#^/city/([a-z0-9\-]+)/?$#', $path, $m)) {
            self::force_tax('cities', $m[1]);
        }
        if (preg_match('#^/service-category/([a-z0-9\-]+)/?$#', $path, $m)) {
            self::force_tax('service_categories', $m[1]);
        }
    }

    public static function force_tax($taxonomy, $slug)
    {
        $term = get_term_by('slug', $slug, $taxonomy);
        if (!$term || is_wp_error($term)) {
            return;
        }
        global $wp_query, $wp;
        $wp_query = new WP_Query([
            'post_type' => ['post', 'services'],
            'posts_per_page' => 24,
            'tax_query' => [[
                'taxonomy' => $taxonomy,
                'field' => 'slug',
                'terms' => $slug,
            ]],
        ]);
        $wp_query->is_tax = true;
        $wp_query->is_archive = true;
        $wp_query->is_home = false;
        $wp_query->is_front_page = false;
        $wp_query->is_404 = false;
        $wp_query->is_singular = false;
        $wp_query->queried_object = $term;
        $wp_query->queried_object_id = $term->term_id;
        $wp_query->set('cities', $taxonomy === 'cities' ? $slug : '');
        status_header(200);
        if (isset($wp) && is_object($wp)) {
            $wp->query_vars['error'] = '';
            $wp->query_vars[$taxonomy] = $slug;
        }
    }

    public static function stop_soft_404()
    {
        if (is_admin() || wp_doing_ajax()) {
            return;
        }
        $path = rtrim(self::path(), '/') . '/';
        if ($path === '//') {
            $path = '/';
        }
        $is_home_path = ($path === '/' || $path === '');
        if ((is_home() || is_front_page()) && !$is_home_path && !is_paged()) {
            if (self::url_has_content($path)) {
                return;
            }
            global $wp_query;
            $wp_query->set_404();
            $wp_query->is_home = false;
            $wp_query->is_front_page = false;
            status_header(404);
            nocache_headers();
        }
    }

    public static function serve_real_404()
    {
        if (is_admin() || wp_doing_ajax() || wp_doing_cron()) {
            return;
        }
        if (!is_404()) {
            return;
        }
        $path = rtrim(self::path(), '/') . '/';
        if (preg_match('#^/(contact-us|blog|page/\d+)/?$#', $path)) {
            return;
        }
        status_header(404);
        nocache_headers();
    }

    public static function url_has_content($path)
    {
        $slug = trim($path, '/');
        if ($slug === '') {
            return true;
        }
        if (preg_match('#^(en|services|city|service-category|search|author|tag|category)/#', $slug . '/')) {
            return true;
        }
        $found = get_page_by_path($slug, OBJECT, ['post', 'page', 'services']);
        return $found && $found->post_status === 'publish';
    }

    public static function tax_archives($q)
    {
        if (is_admin() || !$q->is_main_query()) {
            return;
        }
        if ($q->is_tax('cities') || $q->is_tax('service_categories')) {
            $q->set('post_type', ['post', 'services']);
            $q->set('posts_per_page', 24);
        }
    }

    public static function menu_location($locs)
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

    public static function body_class($classes)
    {
        $classes[] = 'rukn-hide-call';
        return $classes;
    }

    public static function noindex_paged_home()
    {
        if ((is_home() || is_front_page()) && is_paged()) {
            add_filter('wp_robots', static function ($robots) {
                $robots['noindex'] = true;
                $robots['follow'] = true;
                return $robots;
            });
        }
    }

    public static function head_css()
    {
        echo '<style id="rukn-oman-fix-css">'
            . 'body.rukn-hide-call a[href^="tel:"],body.rukn-hide-call .btn-call,body.rukn-hide-call .fab-call,'
            . 'body.rukn-hide-call .fab-btn.fab-call,body.rukn-hide-call #ruknFab .fab-call,'
            . 'body.rukn-hide-call .-callbutton--post-card,body.rukn-hide-call .--button-call-link-phone,'
            . 'body.rukn-hide-call [data-rukn-call],body.rukn-hide-call a[data-call="phone" i],'
            . 'body.rukn-hide-call a[data-call="Phone"],body.rukn-hide-call .btn-phone,'
            . 'body.rukn-hide-call .cta-button[href^="tel:"],body.rukn-hide-call .hero-buttons a[href^="tel:"]'
            . '{display:none!important;pointer-events:none!important;visibility:hidden!important}'
            . '.uae-svg,.oman-svg{width:100%;max-width:340px}'
            . 'root{display:block!important;width:100%!important;max-width:100%;min-width:0}'
            . 'body:has(header#hdr) header:not(#hdr),body:has(header#hdr) .--Site--Menu{display:none!important}'
            . 'header#hdr{position:fixed;top:0;inset-inline:0;left:auto!important;right:auto!important;height:80px;min-height:80px;display:flex;align-items:center;overflow:visible;z-index:1000}'
            . 'header#hdr .wrap.nav{display:flex;flex-wrap:nowrap;align-items:center;justify-content:space-between;width:100%;min-width:0;gap:12px}'
            . 'header#hdr a.logo{display:flex;align-items:center;gap:10px;font-family:Cairo,Tajawal,sans-serif;font-weight:900;font-size:22px;color:#fff;text-decoration:none;white-space:nowrap}'
            . 'header#hdr a.logo .kayan-logo-img,header#hdr a.logo>img{display:none!important}'
            . 'header#hdr a.logo .mark{width:46px;height:46px;border-radius:13px;background:linear-gradient(135deg,#2980D4,#2E9DF7);display:grid;place-items:center;color:#fff;flex:none;overflow:hidden;box-shadow:0 16px 48px rgba(46,157,247,.28)}'
            . 'header#hdr a.logo .mark img{display:block!important;width:28px;height:28px;object-fit:contain}'
            . 'header#hdr a.logo b{color:var(--aqua,#4FA8FF)}'
            . 'header#hdr.scrolled a.logo{color:var(--navy,#0A1F4E)}'
            . 'header#hdr.scrolled a.logo b{color:var(--turq,#2E9DF7)}'
            . 'header#hdr nav.menu{display:flex;flex-wrap:nowrap;gap:4px 6px;align-items:center;min-width:0;overflow:hidden}'
            . 'header#hdr nav.menu a{color:#fff!important;font-family:Cairo,Tajawal,sans-serif;font-weight:700;font-size:15px;text-decoration:none;white-space:nowrap;padding:8px 12px;border-radius:10px}'
            . 'header#hdr.scrolled nav.menu a{color:var(--navy,#0A1F4E)!important}'
            . 'header#hdr nav.menu a:hover{color:#fff;background:rgba(255,255,255,.14)}'
            . 'header#hdr.scrolled nav.menu a:hover{color:var(--turq,#2E9DF7);background:rgba(46,157,247,.10)}'
            . '@media(max-width:1024px){header#hdr nav.menu,header#hdr .nav-cta>a.btn{display:none!important}header#hdr .ham{display:flex!important}}'
            . '#loader{animation:ruknLoaderAutoHide .01s linear 1.1s forwards}'
            . '#loader.out{opacity:0;visibility:hidden;pointer-events:none}'
            . '@keyframes ruknLoaderAutoHide{to{opacity:0;visibility:hidden;pointer-events:none}}'
            . '#ruknMob .rukn-mob-links{display:flex;flex-direction:column;gap:6px;margin:12px 0 8px}'
            . '#ruknMob .rukn-mob-links a{font-weight:800;color:#fff!important;text-decoration:none;padding:14px 10px;border-bottom:1px solid rgba(255,255,255,.12)}'
            . '</style>' . "\n";
        echo '<noscript><style>#loader{display:none!important}</style></noscript>' . "\n";
        echo '<script>window.RuknCS=Object.assign(window.RuknCS||{},{call_show:false,wa_show:true,call_number:"",wa_number:"' . self::WA . '"});</script>' . "\n";
    }

    public static function footer_js()
    {
        $wa = self::WA;
        echo '<script id="rukn-hide-call-js">(function(){window.RuknCS=Object.assign(window.RuknCS||{},{call_show:false,wa_show:true,call_number:"",wa_number:"' . $wa . '"});'
            . 'function hide(root){root=root&&root.querySelectorAll?root:document;root.querySelectorAll(\'a[href^="tel:"],.btn-call,.fab-call,.fab-btn.fab-call,.--button-call-link-phone,.-callbutton--post-card,[data-rukn-call],a[data-call="phone"],a[data-call="Phone"]\').forEach(function(el){el.remove()});}'
            . 'function fillMob(){var mob=document.getElementById("ruknMob");var menu=document.querySelector("header#hdr nav.menu");if(!mob||!menu||mob.querySelector(".rukn-mob-links"))return;var box=document.createElement("div");box.className="rukn-mob-links";box.innerHTML=menu.innerHTML;var close=mob.querySelector(".mob-close");if(close&&close.nextSibling){mob.insertBefore(box,close.nextSibling);}else{mob.insertBefore(box,mob.firstChild);}}'
            . 'function freezeCount(){document.querySelectorAll("[data-count]").forEach(function(el){var n=el.getAttribute("data-count");if(!n)return;var s=el.getAttribute("data-suffix")||"";el.textContent=n+s;});}'
            . 'function hideLoader(){var l=document.getElementById("loader");if(!l||l.classList.contains("out"))return;l.classList.add("out");l.setAttribute("aria-hidden","true");}'
            . 'function runAll(){hide(document);fillMob();freezeCount();hideLoader();}'
            . 'if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",runAll);}else{runAll();}'
            . 'if(window.MutationObserver){new MutationObserver(function(){hide(document);freezeCount();}).observe(document.documentElement,{childList:true,subtree:true});}'
            . 'window.addEventListener("load",function(){setTimeout(hideLoader,400);freezeCount();});'
            . 'setTimeout(hideLoader,900);'
            . '})();</script>' . "\n";
    }

    public static function menu_items($mobile = false)
    {
        $items = [
            ['الخدمات', home_url('/our-services/')],
            ['المدن', home_url('/cities/')],
            ['المشاريع', home_url('/portfolio/')],
            ['من نحن', home_url('/about/')],
            ['الأسئلة', home_url('/faq/')],
        ];
        if ($mobile) {
            $items[] = ['تقييمات', home_url('/reviews/')];
            $items[] = ['تواصل', home_url('/contact/')];
            $items[] = ['خريطة الموقع', home_url('/html-sitemap/')];
        }
        return $items;
    }

    public static function nav_html($mobile = false)
    {
        $out = '';
        foreach (self::menu_items($mobile) as [$label, $url]) {
            $rel = strpos($url, 'wa.me') !== false ? ' rel="nofollow noopener noreferrer" target="_blank"' : '';
            $out .= '<a href="' . esc_url($url) . '"' . $rel . '>' . esc_html($label) . '</a>';
        }
        return $out;
    }

    public static function rewrite($html)
    {
        if (!is_string($html) || $html === '') {
            return $html;
        }
        $home = home_url('/');
        $contact = home_url('/contact/');
        $sitemap = home_url('/html-sitemap/');
        $wa = self::WA_HREF;

        $html = preg_replace('#https?://(www\.)?rukn-eltatawer\.com/om/contact-us/?#i', rtrim($contact, '/'), $html);
        $html = preg_replace('#https?://(www\.)?rukn-eltatawer\.com/om/blog/?#i', rtrim($sitemap, '/'), $html);
        $html = str_replace('rukn-eltatawer.com/om/om/', 'rukn-eltatawer.com/om/', $html);
        $html = str_replace('class="uae-svg"', 'class="oman-svg"', $html);
        $html = str_replace('Table of Contents', 'جدول المحتويات', $html);
        $html = str_replace('ez-toc-title">Table of Contents', 'ez-toc-title">جدول المحتويات', $html);
        $html = str_replace('2font-family', 'font-family', $html);
        $html = str_replace('1font-family', 'font-family', $html);
        $html = preg_replace('/rel=["\']next["\'][^>]*href=["\'][^"\']*\/page\/\d+\/["\']/i', '', $html);
        $html = preg_replace('/href=["\'][^"\']*\/page\/2\/["\']/', 'href="' . esc_url($home) . '"', $html);

        $html = preg_replace('/<nav class="menu">(?:.*?)<\/nav>/s', '<nav class="menu">' . self::nav_html() . '</nav>', $html, 1);

        $logo_icon = esc_url(home_url('/wp-content/uploads/2026/09/logo-icon.webp'));
        $logo = '<a href="' . esc_url($home) . '" class="logo" title="ركن التطور عُمان">'
            . '<span class="mark"><img src="' . $logo_icon . '" alt="" width="28" height="28" decoding="async"></span>'
            . 'ركن <b>التطور</b></a>';
        $html = preg_replace('/<a\b[^>]*class="logo[^"]*"[^>]*>.*?<\/a>/s', $logo, $html, 1);

        $html = str_replace('<div class="ld-logo">ركن التطور عُمان</div>', '<div class="ld-logo">ركن <span>التطور</span></div>', $html);
        $html = preg_replace(
            '/<script>\(function\(\)\{function hide\(\)\{var l=document\.getElementById\("loader"\);[\s\S]*?setTimeout\(hide,1800\);\}\)\(\);<\/script>/',
            '<script>(function(){function hide(){var l=document.getElementById("loader");if(!l||l.classList.contains("out"))return;l.classList.add("out");l.setAttribute("aria-hidden","true");}if(document.readyState==="complete"){hide();}else{window.addEventListener("load",function(){setTimeout(hide,400);});}setTimeout(hide,900);})();</script>',
            $html,
            1
        );

        if (get_option('rukn_oman_icons_mirrored') === '1') {
            $html = preg_replace(
                '#https?://(www\.)?rukn-eltatawer\.com/(?!om/)wp-content/uploads/icon/#i',
                rtrim(home_url('/wp-content/uploads/icon/'), '/') . '/',
                $html
            );
        }
        $html = preg_replace('/"currency"\s*:\s*"AED"/', '"currency":"OMR"', $html);
        $html = preg_replace('/"priceRange"\s*:\s*"AED"/', '"priceRange":"OMR"', $html);
        $html = str_replace('data-currency="AED"', 'data-currency="OMR"', $html);
        $html = str_replace('Search Now', 'ابحث الآن', $html);
        $html = str_replace('"priceRange":"OMR",}', '"priceRange":"OMR"}', $html);
        $html = preg_replace_callback(
            '#<script type="application/ld\+json">(.*?)</script>#s',
            static function ($m) {
                $json = preg_replace('/,\s*([}\]])/', '$1', $m[1]);
                return '<script type="application/ld+json">' . $json . '</script>';
            },
            $html
        );
        $html = preg_replace_callback(
            '/data-searching-argums="([^"]+)"/',
            static function ($m) {
                $raw = base64_decode($m[1], true);
                if (!is_string($raw) || $raw === '') {
                    return $m[0];
                }
                $raw = str_replace('"Search Now"', '"ابحث الآن"', $raw);
                $raw = str_replace('"search_title":"Search"', '"search_title":"بحث"', $raw);
                return 'data-searching-argums="' . base64_encode($raw) . '"';
            },
            $html
        );
        $html = str_replace('.uae-svg', '.oman-svg', $html);
        $html = preg_replace('/<link rel="preload" as="font">/', '', $html);

        $mob = '<div class="rukn-mob-links">' . self::nav_html(true) . '</div>';
        if (strpos($html, 'rukn-mob-links') !== false) {
            $html = preg_replace('/<div class="rukn-mob-links">.*?<\/div>/s', $mob, $html, 1);
        } else {
            $html = preg_replace(
                '/(<div class="mob" id="ruknMob">)/',
                '$1' . $mob,
                $html,
                1
            );
        }

        $html = preg_replace(
            '/<body\b([^>]*)class="([^"]*)"/i',
            '<body$1class="$2 rukn-hide-call"',
            $html,
            1
        );

        $html = preg_replace_callback(
            '/<img\b([^>]*?)data-loader-src=["\']([^"\']+)["\']([^>]*?)>/i',
            static function ($m) {
                $pre = $m[1];
                $src = $m[2];
                $post = $m[3];
                if (preg_match('/\bsrc=/i', $pre . $post)) {
                    return $m[0];
                }
                return '<img' . $pre . 'src="' . esc_url($src) . '" data-loader-src="' . esc_attr($src) . '"' . $post . '>';
            },
            $html
        );

        $html = preg_replace_callback(
            '/<(b|div)([^>]*data-count="([^"]+)"[^>]*)>(?:.*?)<\/\1>/i',
            static function ($m) {
                $n = $m[3];
                $suffix = '';
                if (preg_match('/data-suffix="([^"]*)"/', $m[2], $s)) {
                    $suffix = $s[1];
                }
                return '<' . $m[1] . $m[2] . '>' . $n . $suffix . '</' . $m[1] . '>';
            },
            $html
        );

        $svc_map = [
            'كشف تسربات المياه' => home_url('/services/water-leak-detection/'),
            'كشف تسربات' => home_url('/services/water-leak-detection/'),
            'عزل الأسطح' => home_url('/services/roof-insulation/'),
            'عزل أسطح' => home_url('/services/roof-insulation/'),
            'الصيانة العامة وصيانة المباني' => home_url('/services/building-maintenance/'),
            'صيانة تكييف' => home_url('/services/ac-install-maintenance/'),
            'التكييف والكهرباء' => home_url('/service-category/ac-electrical/'),
            'السباكة وتسليك المجاري' => home_url('/service-category/plumbing/'),
            'سباكة وتسليك' => home_url('/services/plumbing/'),
            'التنظيف والتعقيم' => home_url('/services/cleaning-sterilization/'),
            'تنظيف وتعقيم' => home_url('/services/cleaning-sterilization/'),
            'مكافحة الحشرات' => home_url('/services/pest-control/'),
            'مكافحة حشرات' => home_url('/services/pest-control/'),
            'تنسيق الحدائق والمسابح' => home_url('/service-category/gardens-pools/'),
            'الصبغ والديكورات' => home_url('/service-category/painting-decor/'),
        ];
        foreach ($svc_map as $title => $url) {
            $html = preg_replace(
                '/(<a class="mini" href=")[^"]+(" title="' . preg_quote($title, '/') . '")/',
                '$1' . esc_url($url) . '$2',
                $html
            );
            $html = preg_replace(
                '/(<h3><a href=")[^"]+(" title="' . preg_quote($title, '/') . '")/',
                '$1' . esc_url($url) . '$2',
                $html
            );
        }

        $city_map = [
            'مسقط' => 'muscat',
            'صلالة' => 'salalah',
            'نزوى' => 'nizwa',
            'صحار' => 'sohar',
            'صور' => 'sur',
            'البريمي' => 'al-buraimi',
            'عبري' => 'ibri',
            'الرستاق' => 'rustaq',
        ];
        foreach ($city_map as $ar => $slug) {
            $url = home_url('/city/' . $slug . '/');
            $html = preg_replace(
                '/(<div class="ah">[\s\S]{0,280})<b>' . preg_quote($ar, '/') . '<\/b>/u',
                '$1<a class="acard-link" href="' . esc_url($url) . '"><b>' . $ar . '</b></a>',
                $html,
                1
            );
        }

        $hub = [
            'علامات تسرب المياه' => home_url('/water-leak-detection-muscat/'),
            'الكشف بدون تكسير' => home_url('/water-leak-detection-muscat/'),
            'تكلفة كشف التسربات' => home_url('/water-leak-detection-muscat/'),
            'أنواع العزل المائي' => home_url('/waterproofing-muscat/'),
            'العزل الحراري' => home_url('/thermal-insulation-muscat/'),
            'عزل الأسطح والخزانات' => home_url('/roof-insulation-muscat/'),
            'الصيانة الدورية' => home_url('/general-maintenance-muscat/'),
            'صيانة المباني' => home_url('/building-maintenance-muscat/'),
            'صيانة الأجهزة' => home_url('/appliance-maintenance-muscat/'),
            'التنظيف العميق' => home_url('/deep-cleaning-muscat/'),
            'تنظيف الخزانات' => home_url('/water-tank-cleaning-muscat/'),
            'مكافحة الحشرات' => home_url('/cockroach-control-muscat/'),
            'تصميم الحدائق' => home_url('/landscaping-muscat/'),
            'إنشاء المسابح' => home_url('/pool-maintenance-muscat/'),
            'دليل كشف التسربات' => home_url('/service-category/leak-detection/'),
            'دليل العزل' => home_url('/service-category/insulation/'),
            'دليل الصيانة العامة' => home_url('/service-category/general-maintenance/'),
            'دليل التنظيف' => home_url('/service-category/cleaning-services/'),
            'دليل الحدائق والمسابح' => home_url('/service-category/gardens-pools/'),
        ];
        foreach ($hub as $label => $url) {
            $html = preg_replace(
                '/(<a[^>]*href=["\'])#(["\'][^>]*>[\s\S]{0,80}' . preg_quote($label, '/') . ')/u',
                '$1' . esc_url($url) . '$2',
                $html
            );
            $html = preg_replace(
                '/(<a class="feat-guide" href=")[^"]+("[^>]*>[\s\S]{0,120}' . preg_quote($label, '/') . ')/u',
                '$1' . esc_url($url) . '$2',
                $html
            );
        }

        $footer = '<footer><div class="wrap"><div class="fgrid">'
            . '<div class="fcol"><div class="flogo-wrap"><a href="' . esc_url($home) . '" class="flogo" title="ركن التطور عُمان">'
            . '<span class="mark"><i class="fas fa-shield-halved"></i></span>ركن <b>التطور</b></a></div>'
            . '<p>منصة الخدمات المنزلية المتكاملة في سلطنة عُمان — معاينة ثم عرض مكتوب بالريال العُماني.</p>'
            . '<div class="fcontact"><a href="' . esc_url($wa) . '" target="_blank" rel="nofollow noopener noreferrer">'
            . '<i class="fab fa-whatsapp"></i> تواصل عبر واتساب</a>'
            . '<a href="' . esc_url($contact) . '"><i class="fas fa-location-dot"></i> مسقط، سلطنة عُمان</a></div></div>'
            . '<div class="fcol"><h4>الخدمات</h4><ul>'
            . '<li><a href="' . esc_url(home_url('/services/water-leak-detection/')) . '"><i class="fas fa-chevron-left"></i> كشف تسربات المياه</a></li>'
            . '<li><a href="' . esc_url(home_url('/services/roof-insulation/')) . '"><i class="fas fa-chevron-left"></i> عزل الأسطح</a></li>'
            . '<li><a href="' . esc_url(home_url('/services/ac-install-maintenance/')) . '"><i class="fas fa-chevron-left"></i> صيانة التكييف</a></li>'
            . '<li><a href="' . esc_url(home_url('/services/cleaning-sterilization/')) . '"><i class="fas fa-chevron-left"></i> التنظيف والتعقيم</a></li>'
            . '<li><a href="' . esc_url(home_url('/services/plumbing/')) . '"><i class="fas fa-chevron-left"></i> أعمال السباكة</a></li>'
            . '<li><a href="' . esc_url(home_url('/services/pest-control/')) . '"><i class="fas fa-chevron-left"></i> مكافحة الحشرات</a></li>'
            . '</ul></div>'
            . '<div class="fcol"><h4>المدن</h4><ul>'
            . '<li><a href="' . esc_url(home_url('/city/muscat/')) . '"><i class="fas fa-chevron-left"></i> مسقط</a></li>'
            . '<li><a href="' . esc_url(home_url('/city/salalah/')) . '"><i class="fas fa-chevron-left"></i> صلالة</a></li>'
            . '<li><a href="' . esc_url(home_url('/city/nizwa/')) . '"><i class="fas fa-chevron-left"></i> نزوى</a></li>'
            . '<li><a href="' . esc_url(home_url('/city/sohar/')) . '"><i class="fas fa-chevron-left"></i> صحار</a></li>'
            . '<li><a href="' . esc_url(home_url('/city/sur/')) . '"><i class="fas fa-chevron-left"></i> صور</a></li>'
            . '<li><a href="' . esc_url(home_url('/cities/')) . '"><i class="fas fa-chevron-left"></i> كل المدن</a></li>'
            . '</ul></div>'
            . '<div class="fcol"><h4>روابط سريعة</h4><ul>'
            . '<li><a href="' . esc_url($home) . '"><i class="fas fa-chevron-left"></i> الرئيسية</a></li>'
            . '<li><a href="' . esc_url(home_url('/our-services/')) . '"><i class="fas fa-chevron-left"></i> الخدمات</a></li>'
            . '<li><a href="' . esc_url(home_url('/portfolio/')) . '"><i class="fas fa-chevron-left"></i> المشاريع</a></li>'
            . '<li><a href="' . esc_url(home_url('/about/')) . '"><i class="fas fa-chevron-left"></i> من نحن</a></li>'
            . '<li><a href="' . esc_url(home_url('/faq/')) . '"><i class="fas fa-chevron-left"></i> الأسئلة</a></li>'
            . '<li><a href="' . esc_url($sitemap) . '"><i class="fas fa-chevron-left"></i> خريطة الموقع</a></li>'
            . '</ul><a href="' . esc_url($wa) . '" target="_blank" rel="nofollow noopener noreferrer" class="btn btn-quote" style="margin-top:6px">'
            . '<i class="fab fa-whatsapp"></i> واتساب</a></div></div></div>'
            . '<div class="wrap"><div class="fbottom">© ' . gmdate('Y') . ' ركن التطور عُمان. جميع الحقوق محفوظة.</div></div></footer>';
        $html = preg_replace('/<footer\b[\s\S]*?<\/footer>/i', $footer, $html, 1);

        $html = preg_replace('/"call_show"\s*:\s*(true|false)/i', '"call_show":false', $html);
        $html = preg_replace('/"call_number"\s*:\s*"[^"]*"/i', '"call_number":""', $html);
        $html = preg_replace('/<a\b[^>]*href=["\']tel:[^"\']+["\'][^>]*>[\s\S]*?<\/a>/i', '', $html);
        $html = preg_replace('/<a\b[^>]*class=["\'][^"\']*(btn-call|fab-call|--button-call-link-phone)[^"\']*["\'][^>]*>[\s\S]*?<\/a>/i', '', $html);

        $html = preg_replace(
            '/"aggregateRating"\s*:\s*\{\s*"@type"\s*:\s*"AggregateRating"\s*,\s*"ratingValue"\s*:\s*""\s*,\s*"reviewCount"\s*:\s*""\s*\}/',
            '',
            $html
        );
        $html = preg_replace('/,"openingHours":\s*\["Mo,Tu,We,Th,Fr,Sa,Su 09:00-17:00"\]/', ',"openingHours":["Sa,Su,Mo,Tu,We,Th 08:00-21:00"]', $html);

        $html = str_replace('اتصال أو واتساب', 'واتساب', $html);
        $html = str_replace('اتصال وواتساب', 'واتساب', $html);
        $html = str_replace('اتصل أو أرسل واتساب', 'أرسل واتساب', $html);
        $html = str_replace('لا نسعّر عبر الهاتف', 'لا نسعّر عبر الرسائل النصية دون معاينة', $html);

        return $html;
    }

    public static function maybe_mirror_icons()
    {
        if (is_admin() || get_option('rukn_oman_icons_mirrored') === '1') {
            return;
        }
        $names = [
            'building-maintenance.png',
            'cleaning-services.png',
            'decoration-services.png',
            'electrical-appliance-repair.png',
            'fast-response.png',
            'insulation-services.png',
            'landscaping-services.png',
            'lifetime-warranty.png',
            'location1.png',
            'pest-control.png',
            'plumbing-services.png',
            'price.png',
            'search.png',
            'setting.png',
            'skilled-technicians.png',
            'tab.png',
            'water-leak-detection.png',
            'whatsapp.png',
        ];
        $dir = WP_CONTENT_DIR . '/uploads/icon';
        if (!wp_mkdir_p($dir)) {
            return;
        }
        $ok = 0;
        $ctx = stream_context_create([
            'http' => ['timeout' => 12, 'header' => "User-Agent: RuknOman/1.0\r\n"],
            'ssl' => ['verify_peer' => true, 'verify_peer_name' => true],
        ]);
        foreach ($names as $name) {
            $dest = $dir . '/' . $name;
            if (is_file($dest) && filesize($dest) > 80) {
                $ok++;
                continue;
            }
            $src = 'https://www.rukn-eltatawer.com/wp-content/uploads/icon/' . $name;
            $raw = @file_get_contents($src, false, $ctx);
            if (is_string($raw) && strlen($raw) > 80) {
                file_put_contents($dest, $raw);
                $ok++;
            }
        }
        if ($ok >= 12) {
            update_option('rukn_oman_icons_mirrored', '1', false);
        }
    }
}

Rukn_Oman_Frontend::init();
