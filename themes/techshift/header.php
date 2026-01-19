<?php
/**
 * The header for our theme
 *
 * @package TechShift
 */
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="profile" href="https://gmpg.org/xfn/11">


	<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div id="page" class="site">
	<a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e( 'Skip to content', 'techshift' ); ?></a>

	<header id="masthead" class="site-header">
		<div class="container header-container">
			<div class="site-branding">
				<?php
				the_custom_logo();
				if ( is_front_page() && is_home() ) :
					?>
				<h1 class="site-title">
					<a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
						<img src="<?php echo get_template_directory_uri(); ?>/assets/images/logo.svg" alt="TechShift" style="height: 40px; width: auto; display: block;">
					</a>
				</h1>
					<?php
				else :
					?>
					<p class="site-title">
						<a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
							<img src="<?php echo get_template_directory_uri(); ?>/assets/images/logo.svg" alt="<?php bloginfo( 'name' ); ?>" style="height: 40px; width: auto;">
						</a>
					</p>
					<?php
				endif;
				?>
				<?php
				// Description removed from header as per user request
				/*
				$techshift_description = get_bloginfo( 'description', 'display' );
				if ( $techshift_description || is_customize_preview() ) :
					?>
					<p class="site-description"><?php echo $techshift_description; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></p>
				<?php endif; 
				*/
				?>
			</div><!-- .site-branding -->

			<nav id="site-navigation" class="main-navigation">
				<button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
					<span class="screen-reader-text"><?php esc_html_e( 'Menu', 'techshift' ); ?></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>
				<ul id="primary-menu" class="menu">
					<li><a href="<?php echo esc_url( home_url( '/category/summary/' ) ); ?>">日次・週次まとめ</a></li>
					<li><a href="<?php echo esc_url( home_url( '/category/multi-agent-systems/' ) ); ?>">マルチエージェント</a></li>
					<li><a href="<?php echo esc_url( home_url( '/category/post-quantum-cryptography/' ) ); ?>">耐量子暗号 (PQC)</a></li>
					<li><a href="<?php echo esc_url( home_url( '/category/solid-state-batteries/' ) ); ?>">全固体電池</a></li>
					<li><a href="<?php echo esc_url( home_url( '/category/autonomous-driving/' ) ); ?>">自動運転</a></li>
				</ul>
			</nav><!-- #site-navigation -->
		</div>
	</header><!-- #masthead -->

    <?php 
    if ( function_exists( 'techshift_breadcrumb' ) ) {
        techshift_breadcrumb(); 
    }
    ?>
