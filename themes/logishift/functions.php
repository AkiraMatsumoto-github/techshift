<?php
/**
 * LogiShift functions and definitions
 *
 * @package LogiShift
 */

// Enqueue styles
function logishift_scripts() {
    wp_enqueue_style( 'logishift-style', get_stylesheet_uri(), array(), '1.0.10' );

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
