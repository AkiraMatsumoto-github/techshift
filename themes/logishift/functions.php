<?php
/**
 * LogiShift functions and definitions
 *
 * @package LogiShift
 */

// Enqueue styles
function logishift_scripts() {
    wp_enqueue_style( 'logishift-style', get_stylesheet_uri(), array(), '1.0.15' );

    // Swiper
    if ( is_front_page() ) {
        wp_enqueue_style( 'swiper-css', 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css', array(), '11.0.0' );
        wp_enqueue_script( 'swiper-js', 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js', array(), '11.0.0', true );
        wp_enqueue_script( 'logishift-front-page', get_template_directory_uri() . '/assets/js/front-page.js', array( 'swiper-js', 'jquery' ), '1.0.0', true );
    }

    wp_enqueue_script( 'logishift-navigation', get_template_directory_uri() . '/assets/js/navigation.js', array(), '1.0.7', true );
}
add_action( 'wp_enqueue_scripts', 'logishift_scripts' );

if ( ! function_exists( 'logishift_setup' ) ) :
	function logishift_setup() {
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
				'menu-1' => esc_html__( 'Primary', 'logishift' ),
				'footer' => esc_html__( 'Footer', 'logishift' ),
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
add_action( 'after_setup_theme', 'logishift_setup' );

/**
 * Register widget area.
 *
 * @link https://developer.wordpress.org/themes/functionality/sidebars/#registering-a-sidebar
 */
function logishift_widgets_init() {
	register_sidebar(
		array(
			'name'          => esc_html__( 'Sidebar', 'logishift' ),
			'id'            => 'sidebar-1',
			'description'   => esc_html__( 'Add widgets here.', 'logishift' ),
			'before_widget' => '<section id="%1$s" class="widget %2$s">',
			'after_widget'  => '</section>',
			'before_title'  => '<h2 class="widget-title">',
			'after_title'   => '</h2>',
		)
	);
}
add_action( 'widgets_init', 'logishift_widgets_init' );

/**
 * Create dummy menu for demonstration.
 */
function logishift_create_dummy_menu() {
    $menu_name = 'Primary Menu';
    $menu_exists = wp_get_nav_menu_object( $menu_name );

    if ( ! $menu_exists ) {
        $menu_id = wp_create_nav_menu( $menu_name );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Home', 'logishift' ),
            'menu-item-url' => home_url( '/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'About', 'logishift' ),
            'menu-item-url' => home_url( '/about/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Logistics Strategy', 'logishift' ),
            'menu-item-url' => home_url( '/category/strategy/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'DX Solutions', 'logishift' ),
            'menu-item-url' => home_url( '/category/dx/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Cost Reduction', 'logishift' ),
            'menu-item-url' => home_url( '/category/cost/' ),
            'menu-item-status' => 'publish'
        ) );

        wp_update_nav_menu_item( $menu_id, 0, array(
            'menu-item-title' =>  __( 'Contact', 'logishift' ),
            'menu-item-url' => home_url( '/contact/' ),
            'menu-item-status' => 'publish'
        ) );

        $locations = get_theme_mod( 'nav_menu_locations' );
        $locations['menu-1'] = $menu_id;
        set_theme_mod( 'nav_menu_locations', $locations );
    }
}
add_action( 'init', 'logishift_create_dummy_menu' );

/**
 * Add search form to navigation menu.
 */
function logishift_add_search_to_menu( $items, $args ) {
    if ( $args->theme_location == 'menu-1' ) {
        $items .= '<li class="menu-item menu-item-search">';
        $items .= get_search_form( false );
        $items .= '</li>';
    }
    return $items;
}

add_filter( 'wp_nav_menu_items', 'logishift_add_search_to_menu', 10, 2 );

/**
 * Output SEO Meta Tags.
 */
function logishift_seo_meta() {
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
add_action( 'wp_head', 'logishift_seo_meta', 1 );

/**
 * Disable canonical redirects only for category URLs.
 * This prevents ?cat=ID from being redirected to /category/slug/
 * while keeping redirects working for other pages.
 */
function logishift_disable_category_redirect( $redirect_url ) {
    if ( is_category() && strpos( $_SERVER['REQUEST_URI'], '?cat=' ) !== false ) {
        return false;
    }
    return $redirect_url;
}
add_filter( 'redirect_canonical', 'logishift_disable_category_redirect' );

/**
 * Force enable pretty permalinks.
 * This ensures post URLs work correctly.
 */
function logishift_enable_permalinks() {
    $current_structure = get_option( 'permalink_structure' );
    if ( empty( $current_structure ) ) {
        global $wp_rewrite;
        $wp_rewrite->set_permalink_structure( '/%postname%/' );
        update_option( 'rewrite_rules', false );
        $wp_rewrite->flush_rules( true );
    }
}
add_action( 'init', 'logishift_enable_permalinks' );

/**
 * Automatically generate SEO-friendly English slugs from Japanese titles.
 * Uses post ID (e.g., post-123) to ensure clean URLs.
 * Hooked to save_post to ensure ID is available.
 */
function logishift_auto_generate_slug_on_save( $post_id, $post, $update ) {
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
        remove_action( 'save_post', 'logishift_auto_generate_slug_on_save', 10, 3 );

        // Update the post slug
        wp_update_post( array(
            'ID'        => $post_id,
            'post_name' => 'post-' . $post_id,
        ) );

        // Re-hook
        add_action( 'save_post', 'logishift_auto_generate_slug_on_save', 10, 3 );
    }
}
add_action( 'save_post', 'logishift_auto_generate_slug_on_save', 10, 3 );

/**
 * Sanitize post slugs to prevent Japanese characters in URLs.
 * Generates clean English slugs from Japanese titles.
 */
function logishift_sanitize_post_slug( $slug, $post_ID, $post_status, $post_type ) {
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
add_filter( 'wp_unique_post_slug', 'logishift_sanitize_post_slug', 10, 4 );

/**
 * Register custom meta fields for REST API.
 * This exposes the AI structured summary to the API.
 */
function logishift_register_meta() {
    register_post_meta( 'post', 'ai_structured_summary', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'string',
        'auth_callback' => '__return_true'
    ) );
}
add_action( 'init', 'logishift_register_meta' );

/**
 * Remove prefixes from archive titles.
 */
function logishift_archive_title( $title ) {
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
add_filter( 'get_the_archive_title', 'logishift_archive_title' );

/**
 * View Controller for Popular Articles.
 */
require get_template_directory() . '/inc/view-controller.php';

/**
 * Initialize Popular Articles DB Table.
 * Runs on init to check if table needs creation/update.
 */
function logishift_initialize_popular_articles() {
    $current_version = get_option( 'logishift_view_table_version' );
    if ( version_compare( $current_version, '1.0.0', '<' ) ) {
        logishift_create_view_table();
    }
}
add_action( 'init', 'logishift_initialize_popular_articles' );
