<?php
/**
 * The template for displaying all pages
 *
 * @package FinShift
 */

get_header();
?>

<main id="primary" class="site-main">
	<div class="container">
		
		<!-- Breadcrumb -->
		<div class="breadcrumb">
			<span><a href="<?php echo esc_url( home_url( '/' ) ); ?>">Home</a></span>
			<span class="sep">&gt;</span>
			<span class="current"><?php the_title(); ?></span>
		</div>

		<div class="page-content-area">
			<?php
			while ( have_posts() ) :
				the_post();
				?>
				<article id="post-<?php the_ID(); ?>" <?php post_class( 'single-page' ); ?>>
					
					<header class="entry-header">
						<?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
					</header>

					<div class="entry-thumbnail">
						<?php if ( has_post_thumbnail() ) : ?>
							<?php the_post_thumbnail( 'large' ); ?>
						<?php endif; ?>
					</div>

					<div class="entry-content">
						<?php
						the_content();

						wp_link_pages(
							array(
								'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'finshift' ),
								'after'  => '</div>',
							)
						);
						?>
					</div>

				</article>
				<?php
			endwhile; // End of the loop.
			?>
		</div>
	</div>
</main>

<?php
get_footer();
