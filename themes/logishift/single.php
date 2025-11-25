<?php
/**
 * The template for displaying all single posts
 *
 * @package LogiShift
 */

get_header();
?>

<main id="primary" class="site-main">
	<div class="container">
		
		<!-- Breadcrumb -->
		<div class="breadcrumb">
			<span><a href="<?php echo esc_url( home_url( '/' ) ); ?>">Home</a></span>
			<span class="sep">&gt;</span>
			<?php
			$categories = get_the_category();
			if ( ! empty( $categories ) ) {
				$cat = $categories[0];
				echo '<span><a href="' . esc_url( get_category_link( $cat->term_id ) ) . '">' . esc_html( $cat->name ) . '</a></span>';
				echo '<span class="sep">&gt;</span>';
			}
			?>
			<span class="current"><?php the_title(); ?></span>
		</div>

		<div class="content-sidebar-wrap">
			<div class="content-area">
				<?php
				while ( have_posts() ) :
					the_post();
					?>
					<article id="post-<?php the_ID(); ?>" <?php post_class( 'single-article' ); ?>>
						
						<header class="entry-header">
							<div class="entry-meta">
								<?php
								if ( ! empty( $categories ) ) :
									?>
									<span class="cat-label"><?php echo esc_html( $categories[0]->name ); ?></span>
								<?php endif; ?>
								<span class="posted-on"><?php echo get_the_date(); ?></span>
							</div>
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
									'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'logishift' ),
									'after'  => '</div>',
								)
							);
							?>
						</div>

						<footer class="entry-footer">
							<!-- Share Buttons Placeholder -->
							<div class="share-buttons">
								<p>Share this article:</p>
								<!-- TODO: Implement actual share links -->
								<button class="button outline small">X (Twitter)</button>
								<button class="button outline small">Facebook</button>
							</div>
						</footer>
					</article>

					<!-- Related Posts -->
					<div class="related-posts">
						<h3 class="related-title"><?php esc_html_e( '関連記事', 'logishift' ); ?></h3>
						<div class="article-grid">
							<?php
							$related_args = array(
								'post_type'      => 'post',
								'posts_per_page' => 3,
								'post__not_in'   => array( get_the_ID() ),
								'orderby'        => 'rand',
							);
							
							if ( ! empty( $categories ) ) {
								$related_args['category__in'] = array( $categories[0]->term_id );
							}

							$related_query = new WP_Query( $related_args );

							if ( $related_query->have_posts() ) :
								while ( $related_query->have_posts() ) :
									$related_query->the_post();
									?>
									<article id="post-<?php the_ID(); ?>" <?php post_class( 'article-card' ); ?>>
										<div class="article-thumbnail">
											<?php if ( has_post_thumbnail() ) : ?>
												<a href="<?php the_permalink(); ?>"><?php the_post_thumbnail( 'medium' ); ?></a>
											<?php else : ?>
												<a href="<?php the_permalink(); ?>"><div class="no-image"></div></a>
											<?php endif; ?>
										</div>
										<div class="article-content">
											<div class="article-meta">
												<span class="posted-on"><?php echo get_the_date(); ?></span>
											</div>
											<h4 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h4>
										</div>
									</article>
									<?php
								endwhile;
								wp_reset_postdata();
							else :
								echo '<p>' . esc_html__( '関連記事はありません。', 'logishift' ) . '</p>';
							endif;
							?>
						</div>
					</div>

					<?php
				endwhile; // End of the loop.
				?>
			</div>

			<?php get_sidebar(); ?>
		</div>
	</div>
</main>

<?php
get_footer();
