<?php
/**
 * FinShift functions and definitions
 *
 * @package FinShift
 */

// Enqueue styles
function finshift_scripts() {
    wp_enqueue_style( 'finshift-style', get_stylesheet_uri(), array(), '1.0.15' );

    // Swiper
    if ( is_front_page() ) {
        wp_enqueue_style( 'swiper-css', 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css', array(), '11.0.0' );
        wp_enqueue_script( 'swiper-js', 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js', array(), '11.0.0', true );
        wp_enqueue_script( 'finshift-front-page', get_template_directory_uri() . '/assets/js/front-page.js', array( 'swiper-js', 'jquery' ), '1.0.0', true );
    }

    wp_enqueue_script( 'finshift-navigation', get_template_directory_uri() . '/assets/js/navigation.js', array(), '1.0.7', true );
}
add_action( 'wp_enqueue_scripts', 'finshift_scripts' );

if ( ! function_exists( 'finshift_setup' ) ) :
	function finshift_setup() {
		// Add default posts and comments RSS feed links to head.
		add_theme_support( 'automatic-feed-links' );

		// Let WordPress manage the document title.
		add_theme_support( 'title-tag' );

		// Enable support for Post Thumbnails on posts and pages.
		add_theme_support( 'post-thumbnails' );

		// Add support for editor styles.
		add_theme_support( 'editor-styles' );

		// Enqueue editor styles.
		add_editor_style( 'style.css' );

		// Register navigation menus.
		register_nav_menus(
			array(
				'menu-1' => esc_html__( 'Primary', 'finshift' ),
				'footer' => esc_html__( 'Footer', 'finshift' ),
			)
		);

		// Add support for core custom logo.
		add_theme_support(
			'custom-logo',
			array(
				'height'      => 250,
				'width'       => 250,
				'flex-width'  => true,
				'flex-height' => true,
			)
		);
	}
endif;
add_action( 'after_setup_theme', 'finshift_setup' );

/**
 * Register widget area.
 *
 * @link https://developer.wordpress.org/themes/functionality/sidebars/#registering-a-sidebar
 */
function finshift_widgets_init() {
	register_sidebar(
		array(
			'name'          => esc_html__( 'Sidebar', 'finshift' ),
			'id'            => 'sidebar-1',
			'description'   => esc_html__( 'Add widgets here.', 'finshift' ),
			'before_widget' => '<section id="%1$s" class="widget %2$s">',
			'after_widget'  => '</section>',
			'before_title'  => '<h2 class="widget-title">',
			'after_title'   => '</h2>',
		)
	);
}
add_action( 'widgets_init', 'finshift_widgets_init' );

/**
 * Create dummy menu for demonstration.
 */
function finshift_create_dummy_menu() {
    $menu_name = 'Primary Menu';
    $menu_exists = wp_get_nav_menu_object( $menu_name );

    if ( ! $menu_exists ) {
        $menu_id = wp_create_nav_menu( $menu_name );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Home', 'finshift' ),
            'menu-item-url' => home_url( '/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'About', 'finshift' ),
            'menu-item-url' => home_url( '/about/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Logistics Strategy', 'finshift' ),
            'menu-item-url' => home_url( '/category/strategy/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'DX Solutions', 'finshift' ),
            'menu-item-url' => home_url( '/category/dx/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Cost Reduction', 'finshift' ),
            'menu-item-url' => home_url( '/category/cost/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Contact', 'finshift' ),
            'menu-item-url' => home_url( '/contact/' ),
            'menu-item-status' => 'publish'
        ) );

        $locations = get_theme_mod( 'nav_menu_locations' );
        $locations['menu-1'] = $menu_id;
        set_theme_mod( 'nav_menu_locations', $locations );
    }
}
add_action( 'init', 'finshift_create_dummy_menu' );

/**
 * Add search form to navigation menu.
 */
function finshift_add_search_to_menu( $items, $args ) {
    if ( $args->theme_location == 'menu-1' ) {
        $items .= '<li class="menu-item menu-item-search">';
        $items .= get_search_form( false );
        $items .= '</li>';
    }
    return $items;
}

add_filter( 'wp_nav_menu_items', 'finshift_add_search_to_menu', 10, 2 );

/**
 * Output SEO Meta Tags.
 */
function finshift_seo_meta() {
    global $post;

    // Default values
    $title = wp_get_document_title();
    $description = get_bloginfo( 'description' );
    $url = get_permalink();
    $site_name = get_bloginfo( 'name' );
    $type = 'website';
    $image = get_template_directory_uri() . '/assets/images/hero-bg.png'; // Default image

    // Single Post / Page
    if ( is_singular() ) {
        $type = 'article';
        if ( has_excerpt() ) {
            $description = get_the_excerpt();
        } else {
            $description = wp_trim_words( $post->post_content, 120, '...' );
        }
        
        if ( has_post_thumbnail() ) {
            $image = get_the_post_thumbnail_url( $post->ID, 'large' );
        }
    }
    
    // Archive / Category
    if ( is_archive() ) {
        $description = get_the_archive_description();
        if ( empty( $description ) ) {
            $description = 'Archive for ' . get_the_archive_title();
        }
        $url = get_category_link( get_queried_object_id() );
    }

    // Sanitize
    $description = strip_tags( $description );
    $description = str_replace( array( "\r", "\n" ), '', $description );

    ?>
    <!-- SEO Meta Tags -->
    <meta name="description" content="<?php echo esc_attr( $description ); ?>">
    
    <!-- OGP -->
    <meta property="og:title" content="<?php echo esc_attr( $title ); ?>">
    <meta property="og:description" content="<?php echo esc_attr( $description ); ?>">
    <meta property="og:url" content="<?php echo esc_url( $url ); ?>">
    <meta property="og:type" content="<?php echo esc_attr( $type ); ?>">
    <meta property="og:site_name" content="<?php echo esc_attr( $site_name ); ?>">
    <meta property="og:image" content="<?php echo esc_url( $image ); ?>">
    <meta property="og:locale" content="ja_JP">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="<?php echo esc_attr( $title ); ?>">
    <meta name="twitter:description" content="<?php echo esc_attr( $description ); ?>">
    <meta name="twitter:image" content="<?php echo esc_url( $image ); ?>">
    <?php
}
add_action( 'wp_head', 'finshift_seo_meta', 1 );

/**
 * Disable canonical redirects only for category URLs.
 * This prevents ?cat=ID from being redirected to /category/slug/
 * while keeping redirects working for other pages.
 */
function finshift_disable_category_redirect( $redirect_url ) {
    if ( is_category() && strpos( $_SERVER['REQUEST_URI'], '?cat=' ) !== false ) {
        return false;
    }
    return $redirect_url;
}
add_filter( 'redirect_canonical', 'finshift_disable_category_redirect' );

/**
 * Force enable pretty permalinks.
 * This ensures post URLs work correctly.
 */
function finshift_enable_permalinks() {
    $current_structure = get_option( 'permalink_structure' );
    if ( empty( $current_structure ) ) {
        global $wp_rewrite;
        $wp_rewrite->set_permalink_structure( '/%postname%/' );
        update_option( 'rewrite_rules', false );
        $wp_rewrite->flush_rules( true );
    }
}
add_action( 'init', 'finshift_enable_permalinks' );

/**
 * Automatically generate SEO-friendly English slugs from Japanese titles.
 * Uses post ID (e.g., post-123) to ensure clean URLs.
 * Hooked to save_post to ensure ID is available.
 */
function finshift_auto_generate_slug_on_save( $post_id, $post, $update ) {
    // Only process posts
    if ( $post->post_type !== 'post' ) {
        return;
    }

    // Avoid infinite loops
    if ( wp_is_post_revision( $post_id ) || wp_is_post_autosave( $post_id ) ) {
        return;
    }

    // Check if slug is empty, contains Japanese, or is URL-encoded
    $slug = $post->post_name;
    if ( empty( $slug ) || preg_match( '/[ぁ-んァ-ヶー一-龠％]/u', $slug ) || strpos( $slug, '%' ) !== false ) {
        
        // Unhook to prevent infinite loop
        remove_action( 'save_post', 'finshift_auto_generate_slug_on_save', 10, 3 );

        // Update the post slug
        wp_update_post( array(
            'ID'        => $post_id,
            'post_name' => 'post-' . $post_id,
        ) );

        // Re-hook
        add_action( 'save_post', 'finshift_auto_generate_slug_on_save', 10, 3 );
    }
}
add_action( 'save_post', 'finshift_auto_generate_slug_on_save', 10, 3 );

/**
 * Sanitize post slugs to prevent Japanese characters in URLs.
 * Generates clean English slugs from Japanese titles.
 */
function finshift_sanitize_post_slug( $slug, $post_ID, $post_status, $post_type ) {
    // Only process posts, not pages or other post types
    if ( $post_type !== 'post' ) {
        return $slug;
    }

    // If slug is empty or contains Japanese characters
    if ( empty( $slug ) || preg_match( '/[ぁ-んァ-ヶー一-龠]/u', $slug ) ) {
        // Get the post title
        $post = get_post( $post_ID );
        if ( $post ) {
            // Generate slug from post ID and first few words of title
            $title_words = explode( ' ', $post->post_title );
            $slug = 'post-' . $post_ID;
        }
    }

    return $slug;
}
add_filter( 'wp_unique_post_slug', 'finshift_sanitize_post_slug', 10, 4 );



/**
 * Remove prefixes from archive titles.
 */
function finshift_archive_title( $title ) {
    if ( is_category() ) {
        $title = single_cat_title( '', false );
    } elseif ( is_tag() ) {
        $title = single_tag_title( '', false );
    } elseif ( is_author() ) {
        $title = '<span class="vcard">' . get_the_author() . '</span>';
    } elseif ( is_post_type_archive() ) {
        $title = post_type_archive_title( '', false );
    } elseif ( is_tax() ) {
        $title = single_term_title( '', false );
    }
    return $title;
}
add_filter( 'get_the_archive_title', 'finshift_archive_title' );

/**
 * View Controller for Popular Articles.
 */
require get_template_directory() . '/inc/view-controller.php';

/**
 * Market Dashboard Metaboxes.
 */
require get_template_directory() . '/inc/market-metaboxes.php';

/**
 * Post Meta Registration for REST API.
 */
require get_template_directory() . '/inc/post-meta.php';

/**
 * Initialize Popular Articles DB Table.
 * Runs on init to check if table needs creation/update.
 */
function finshift_initialize_popular_articles() {
    $current_version = get_option( 'finshift_view_table_version' );
    if ( version_compare( $current_version, '1.0.0', '<' ) ) {
        finshift_create_view_table();
    }
}
add_action( 'init', 'finshift_initialize_popular_articles' );
/**
 * Register REST API endpoint for Popular Posts.
 * Endpoint: /wp-json/finshift/v1/popular-posts
 */
function finshift_register_popular_posts_route() {
    register_rest_route( 'finshift/v1', '/popular-posts', array(
        'methods'  => 'GET',
        'callback' => 'finshift_get_popular_posts_api',
        'permission_callback' => '__return_true', // Public endpoint
    ) );
}
add_action( 'rest_api_init', 'finshift_register_popular_posts_route' );

/**
 * Callback for Popular Posts API.
 */
function finshift_get_popular_posts_api( $request ) {
    $days = $request->get_param( 'days' ) ? intval( $request->get_param( 'days' ) ) : 30; // Default to 30 days for broader range
    $limit = $request->get_param( 'limit' ) ? intval( $request->get_param( 'limit' ) ) : 20;

    if ( ! function_exists( 'finshift_get_popular_posts' ) ) {
        return new WP_Error( 'no_function', 'Popular posts function not found', array( 'status' => 500 ) );
    }

    $posts = finshift_get_popular_posts( $days, $limit );
    
    $data = array();
    foreach ( $posts as $post ) {
        // Format similar to standard WP REST API post object (simplified)
        $data[] = array(
            'id' => $post->ID,
            'date' => $post->post_date,
            'link' => get_permalink( $post->ID ),
            'title' => array( 'rendered' => $post->post_title ),
            'excerpt' => array( 'rendered' => has_excerpt( $post->ID ) ? get_the_excerpt( $post->ID ) : wp_trim_words( $post->post_content, 20 ) ),
            'views' => $post->views,
            'meta' => array(
                'ai_structured_summary' => get_post_meta( $post->ID, 'ai_structured_summary', true )
            )
        );
    }

    return $data;
}

// Force enable Application Passwords for Local HTTP dev
add_filter( 'wp_is_application_passwords_available', '__return_true' );

/**
 * FinShift DB Integration
 * Defines custom tables and REST API endpoints for Market Data, Analysis, and Economic Events.
 */

// Table Names
define('FINSHIFT_TBL_MARKET_SNAPSHOTS', 'fs_market_snapshots');
define('FINSHIFT_TBL_DAILY_ANALYSIS', 'fs_daily_analysis');
define('FINSHIFT_TBL_ECONOMIC_EVENTS', 'fs_economic_events');
define('FINSHIFT_TBL_ARTICLES', 'fs_articles');

/**
 * Initialize Tables on Theme Switch / Admin Init
 */
function finshift_initialize_tables() {
    global $wpdb;
    $charset_collate = $wpdb->get_charset_collate();
    require_once( ABSPATH . 'wp-admin/includes/upgrade.php' );

    // 1. fs_market_snapshots
    $sql_snapshots = "CREATE TABLE " . $wpdb->prefix . FINSHIFT_TBL_MARKET_SNAPSHOTS . " (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        date date NOT NULL,
        data_json json NOT NULL,
        sp500_close float DEFAULT NULL,
        us10y_yield float DEFAULT NULL,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY  (id),
        UNIQUE KEY date (date)
    ) $charset_collate;";
    dbDelta( $sql_snapshots );

    // 2. fs_daily_analysis
    $sql_analysis = "CREATE TABLE " . $wpdb->prefix . FINSHIFT_TBL_DAILY_ANALYSIS . " (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        date date NOT NULL,
        region varchar(10) NOT NULL,
        sentiment_score float DEFAULT NULL,
        sentiment_label varchar(20) DEFAULT NULL,
        market_regime varchar(50) DEFAULT NULL,
        scenarios_json json DEFAULT NULL,
        full_briefing_md text DEFAULT NULL,
        wp_post_id bigint(20) DEFAULT NULL,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY  (id),
        UNIQUE KEY region_date (region, date)
    ) $charset_collate;";
    dbDelta( $sql_analysis );

    // 3. fs_economic_events
    $sql_events = "CREATE TABLE " . $wpdb->prefix . FINSHIFT_TBL_ECONOMIC_EVENTS . " (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        event_date date NOT NULL,
        country varchar(50) DEFAULT NULL,
        event_name varchar(255) NOT NULL,
        impact varchar(20) DEFAULT 'Medium',
        description text DEFAULT NULL,
        source varchar(50) DEFAULT 'system',
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY  (id),
        UNIQUE KEY event_unique (event_date, event_name, country)
    ) $charset_collate;";
    dbDelta( $sql_events );

    // 4. fs_articles
    $sql_articles = "CREATE TABLE " . $wpdb->prefix . FINSHIFT_TBL_ARTICLES . " (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        url_hash char(64) NOT NULL,
        title varchar(512) NOT NULL,
        source varchar(100) DEFAULT NULL,
        region varchar(20) DEFAULT NULL,
        published_at datetime DEFAULT NULL,
        fetched_at datetime DEFAULT CURRENT_TIMESTAMP,
        summary text DEFAULT NULL,
        is_relevant tinyint(1) DEFAULT 1,
        relevance_reason text DEFAULT NULL,
        sentiment_score int(11) DEFAULT NULL,
        PRIMARY KEY  (id),
        UNIQUE KEY url_hash (url_hash),
        KEY idx_region (region),
        KEY idx_published (published_at)
    ) $charset_collate;";
    dbDelta( $sql_articles );
}
add_action( 'after_switch_theme', 'finshift_initialize_tables' );
// Also run on admin_init once to ensure created if theme already active
function finshift_check_tables() {
    if ( ! get_option( 'finshift_tables_created' ) ) {
        finshift_initialize_tables();
        update_option( 'finshift_tables_created', true );
    }
}
add_action( 'admin_init', 'finshift_check_tables' );

/**
 * Register REST API Routes
 */
function finshift_register_api_routes() {
    $namespace = 'finshift/v1';

    // Market Snapshots
    register_rest_route( $namespace, '/market-snapshots', array(
        array(
            'methods' => 'POST',
            'callback' => 'finshift_api_save_market_snapshot',
            'permission_callback' => 'finshift_api_auth_check',
        ),
        array(
            'methods' => 'GET',
            'callback' => 'finshift_api_get_market_snapshots',
            'permission_callback' => '__return_true',
        )
    ) );
    register_rest_route( $namespace, '/market-snapshots/(?P<date>\d{4}-\d{2}-\d{2})', array(
        'methods' => 'GET',
        'callback' => 'finshift_api_get_market_snapshot',
        'permission_callback' => '__return_true',
    ) );

    // Daily Analysis
    register_rest_route( $namespace, '/daily-analysis', array(
        'methods' => 'POST',
        'callback' => 'finshift_api_save_daily_analysis',
        'permission_callback' => 'finshift_api_auth_check',
    ) );

    // Economic Events
    register_rest_route( $namespace, '/economic-events', array(
        array(
            'methods' => 'POST',
            'callback' => 'finshift_api_save_economic_event',
            'permission_callback' => 'finshift_api_auth_check',
        ),
        array(
            'methods' => 'GET',
            'callback' => 'finshift_api_get_economic_events',
            'permission_callback' => '__return_true',
        )
    ) );
    register_rest_route( $namespace, '/economic-events/(?P<date>\d{4}-\d{2}-\d{2})', array(
        'methods' => 'GET',
        'callback' => 'finshift_api_get_economic_event',
        'permission_callback' => '__return_true',
    ) );

    // Articles
    register_rest_route( $namespace, '/articles/check', array(
        'methods' => 'POST',
        'callback' => 'finshift_api_check_articles_exist',
        'permission_callback' => 'finshift_api_auth_check',
    ) );
    register_rest_route( $namespace, '/articles', array(
        'methods' => 'POST',
        'callback' => 'finshift_api_save_article',
        'permission_callback' => 'finshift_api_auth_check',
    ) );
    register_rest_route( $namespace, '/articles', array(
        'methods' => 'GET',
        'callback' => 'finshift_api_get_articles',
        'permission_callback' => 'finshift_api_auth_check',
    ) );
}

function finshift_api_get_market_snapshots( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_MARKET_SNAPSHOTS;
    $limit = $request->get_param('limit') ? intval($request->get_param('limit')) : 1;
    
    $results = $wpdb->get_results( $wpdb->prepare( "SELECT * FROM $table ORDER BY date DESC LIMIT %d", $limit ) );
    
    foreach ($results as $row) {
        $row->data_json = json_decode( $row->data_json );
    }
    return $results;
}

function finshift_api_get_economic_events( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_ECONOMIC_EVENTS;
    
    // Support date range
    $start_date = $request->get_param('start_date') ?: date('Y-m-d');
    $days = $request->get_param('days') ? intval($request->get_param('days')) : 7;
    $end_date = date('Y-m-d', strtotime("$start_date + $days days"));

    $results = $wpdb->get_results( $wpdb->prepare( 
        "SELECT * FROM $table WHERE event_date BETWEEN %s AND %s ORDER BY event_date ASC",
        $start_date, $end_date
    ) );
    return $results;
}
add_action( 'rest_api_init', 'finshift_register_api_routes' );

/**
 * Auth Check (Application Passwords or Admin)
 */
function finshift_api_auth_check() {
    return current_user_can( 'edit_posts' );
}

/**
 * API Callbacks
 */
function finshift_api_save_market_snapshot( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_MARKET_SNAPSHOTS;
    
    $params = $request->get_json_params();
    $data_json = json_encode( $params['data'] );
    
    // Extract key metrics for columns
    $sp500 = null; 
    $us10y = null;
    
    // Simple extraction logic (adjust based on actual JSON structure)
    if (isset($params['data']['indices'])) {
        foreach($params['data']['indices'] as $idx) {
            if ($idx['symbol'] === '^GSPC') $sp500 = $idx['price'];
        }
    }
    if (isset($params['data']['bonds'])) {
        foreach($params['data']['bonds'] as $bnd) {
            if ($bnd['symbol'] === '^TNX') $us10y = $bnd['yield'];
        }
    }

    $result = $wpdb->replace( 
        $table, 
        array( 
            'date' => $params['date'],
            'data_json' => $data_json,
            'sp500_close' => $sp500,
            'us10y_yield' => $us10y,
        ),
        array( '%s', '%s', '%f', '%f' ) 
    );

    if ( $result === false ) return new WP_Error( 'db_error', $wpdb->last_error, array( 'status' => 500 ) );
    return array( 'success' => true, 'id' => $wpdb->insert_id );
}

function finshift_api_get_market_snapshot( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_MARKET_SNAPSHOTS;
    $date = $request['date'];
    $row = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM $table WHERE date = %s", $date ) );
    if ( ! $row ) return new WP_Error( 'not_found', 'Data not found', array( 'status' => 404 ) );
    
    $row->data_json = json_decode( $row->data_json );
    return $row;
}

function finshift_api_save_daily_analysis( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_DAILY_ANALYSIS;
    $params = $request->get_json_params();

    $result = $wpdb->replace( 
        $table, 
        array( 
            'date' => $params['date'],
            'region' => $params['region'],
            'sentiment_score' => $params['sentiment_score'],
            'sentiment_label' => $params['sentiment_label'],
            'market_regime' => $params['market_regime'],
            'scenarios_json' => json_encode( $params['scenarios'] ),
            'full_briefing_md' => $params['full_briefing_md'], // Optional
            'wp_post_id' => $params['wp_post_id']
        ),
        array( '%s', '%s', '%f', '%s', '%s', '%s', '%s', '%d' ) 
    );
    
    if ( $result === false ) return new WP_Error( 'db_error', $wpdb->last_error, array( 'status' => 500 ) );
    return array( 'success' => true );
}

function finshift_api_save_economic_event( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_ECONOMIC_EVENTS;
    $params = $request->get_json_params();

    // Use replace to handle uniqueness on (date, name, country)
    $result = $wpdb->replace( 
        $table, 
        array( 
            'event_date' => $params['event_date'],
            'country' => $params['country'],
            'event_name' => $params['event_name'],
            'impact' => $params['impact'],
            'description' => $params['description'],
            'source' => $params['source']
        ),
        array( '%s', '%s', '%s', '%s', '%s', '%s' ) 
    );
    
    if ( $result === false ) return new WP_Error( 'db_error', $wpdb->last_error, array( 'status' => 500 ) );
    return array( 'success' => true );
}

function finshift_api_get_economic_event( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_ECONOMIC_EVENTS;
    $date = $request['date'];
    // Return ALL events for that date
    $rows = $wpdb->get_results( $wpdb->prepare( "SELECT * FROM $table WHERE event_date = %s", $date ) );
    return $rows;
}

function finshift_api_check_articles_exist( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_ARTICLES;
    $params = $request->get_json_params();
    $hashes = $params['hashes']; // Expect list of hashes

    if ( empty( $hashes ) ) return array( 'exists' => array() );

    // Sanitize hashes (they are hex strings)
    $escaped_hashes = array_map( function($h) { return "'" . esc_sql($h) . "'"; }, $hashes );
    $hashes_str = implode(',', $escaped_hashes);

    $results = $wpdb->get_results( "SELECT url_hash FROM $table WHERE url_hash IN ($hashes_str)" );
    
    $existing = array_column( $results, 'url_hash' );
    return array( 'exists' => $existing );
}

function finshift_api_save_article( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_ARTICLES;
    $params = $request->get_json_params();

    // Use replace or insert ignore? 
    // Requirement is deduplication. If hash exists, we might want to update or skip.
    // Client logic usually checks existence first. But INSERT IGNORE or ON DUPLICATE UPDATE is safer.
    // Let's use $wpdb->replace which does DELETE + INSERT (might change ID).
    // Or just custom query for INSERT IGNORE.
    // Let's use replace for simplicity, assumption is hash is unique.

    $result = $wpdb->replace( 
        $table, 
        array( 
            'url_hash' => $params['url_hash'],
            'title' => $params['title'],
            'source' => $params['source'],
            'region' => $params['region'],
            'published_at' => $params['published_at'], // Ensure ISO format or mysql format
            'summary' => $params['summary'],
            'is_relevant' => isset($params['is_relevant']) ? $params['is_relevant'] : 1,
            'relevance_reason' => isset($params['relevance_reason']) ? $params['relevance_reason'] : '',
        ),
        array( '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s' ) 
    );
    
    if ( $result === false ) return new WP_Error( 'db_error', $wpdb->last_error, array( 'status' => 500 ) );
    return array( 'success' => true, 'id' => $wpdb->insert_id );
}

function finshift_api_get_articles( $request ) {
    global $wpdb;
    $table = $wpdb->prefix . FINSHIFT_TBL_ARTICLES;
    
    $hours = $request->get_param('hours') ? intval($request->get_param('hours')) : 24;
    $region = $request->get_param('region');
    $limit = $request->get_param('limit') ? intval($request->get_param('limit')) : 50;

    $query = "SELECT title, summary, source, region, published_at FROM $table WHERE is_relevant = 1";
    $query .= $wpdb->prepare( " AND published_at >= DATE_SUB(NOW(), INTERVAL %d HOUR)", $hours );

    if ( $region && $region !== 'Global' ) {
        $query .= $wpdb->prepare( " AND (region = %s OR region = 'Global')", $region );
    }

    $query .= " ORDER BY published_at DESC LIMIT %d";
    
    $articles = $wpdb->get_results( $wpdb->prepare( $query, $limit ) );
    return $articles;
}

add_action( 'rest_api_init', function () {
    register_rest_route( 'finshift/v1', '/market-snapshots', array(
        'methods' => 'POST',
        'callback' => 'finshift_api_save_market_snapshot',
        'permission_callback' => 'finshift_api_auth_check',
    ) );
    register_rest_route( 'finshift/v1', '/market-snapshots/(?P<date>\d{4}-\d{2}-\d{2})', array(
        'methods' => 'GET',
        'callback' => 'finshift_api_get_market_snapshot',
        'permission_callback' => '__return_true',
    ) );
    register_rest_route( 'finshift/v1', '/daily-analysis', array(
        'methods' => 'POST',
        'callback' => 'finshift_api_save_daily_analysis',
        'permission_callback' => 'finshift_api_auth_check',
    ) );
    register_rest_route( 'finshift/v1', '/economic-events', array(
        'methods' => 'POST',
        'callback' => 'finshift_api_save_economic_event',
        'permission_callback' => 'finshift_api_auth_check',
    ) );
    register_rest_route( 'finshift/v1', '/economic-events/(?P<date>\d{4}-\d{2}-\d{2})', array(
        'methods' => 'GET',
        'callback' => 'finshift_api_get_economic_event',
        'permission_callback' => '__return_true',
    ) );
    register_rest_route( 'finshift/v1', '/update-schema', array(
        'methods' => 'GET',
        'callback' => 'finshift_api_update_schema',
        'permission_callback' => '__return_true',
    ) );
} );

function finshift_api_update_schema( $request ) {
    finshift_initialize_tables();
    return array( 'success' => true, 'message' => 'Schema updated via dbDelta' );
}
