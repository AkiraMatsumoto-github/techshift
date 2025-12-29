<?php
/**
 * The template for displaying archive pages
 * Modern design matching front-page.php
 *
 * @package LogiShift
 */

get_header();
?>

<main id="primary" class="site-main">
	
	<!-- Archive Header -->
	<section class="archive-hero">
		<div class="container">
			<?php
			$object = get_queried_object();
			?>
			<h1 class="archive-title"><?php the_archive_title(); ?></h1>
			<?php if ( get_the_archive_description() ) : ?>
				<div class="archive-description"><?php the_archive_description(); ?></div>
			<?php endif; ?>
		</div>
	</section>

	<!-- Articles Grid -->
	<section class="archive-articles-section">
		<div class="container">
			<?php if ( have_posts() ) : ?>
				<div class="article-grid">
					<?php
					while ( have_posts() ) :
						the_post();
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
									<?php
									$categories = get_the_category();
									if ( ! empty( $categories ) ) :
										?>
										<span class="cat-label"><?php echo esc_html( $categories[0]->name ); ?></span>
									<?php endif; ?>
									<span class="posted-on"><?php echo get_the_date(); ?></span>
								</div>
								<h3 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
							</div>
						</article>
						<?php
					endwhile;
					?>
				</div>

				<div class="pagination">
					<?php
					the_posts_pagination(
						array(
							'prev_text' => '← 前へ',
							'next_text' => '次へ →',
						)
					);
					?>
				</div>

			<?php else : ?>
				<p class="no-posts"><?php esc_html_e( '記事が見つかりませんでした。', 'logishift' ); ?></p>
			<?php endif; ?>
		</div>
	</section>

	<!-- Contextual Popular Articles -->
	<section class="popular-articles-section" style="background-color: var(--color-light-gray); margin-top: 40px; padding-top: 40px; border-top: 1px solid var(--color-border-gray);">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( 'このカテゴリの人気記事', 'logishift' ); ?></h2>
			</div>

			<div class="featured-grid">
				<?php
				if ( function_exists( 'logishift_get_popular_posts' ) ) {
					// Get current term context
					$obj = get_queried_object();
					$term_id = isset( $obj->term_id ) ? $obj->term_id : null;
					$taxonomy = isset( $obj->taxonomy ) ? $obj->taxonomy : 'category';

					// Fetch filtered popular posts
					$popular_posts = logishift_get_popular_posts( 30, 5, $term_id, $taxonomy );

					if ( ! empty( $popular_posts ) ) {
						$rank = 1;
						foreach ( $popular_posts as $post ) : 
							setup_postdata( $post );
							?>
							<article id="post-<?php the_ID(); ?>" <?php post_class( 'featured-card popular-card' ); ?>>
								<div class="featured-thumbnail">
									<div class="rank-badge rank-<?php echo $rank; ?>"><?php echo $rank; ?></div>
									<?php if ( has_post_thumbnail( $post->ID ) ) : ?>
										<a href="<?php echo get_permalink( $post->ID ); ?>">
											<?php echo get_the_post_thumbnail( $post->ID, 'large' ); ?>
										</a>
									<?php else : ?>
										<a href="<?php echo get_permalink( $post->ID ); ?>"><div class="no-image"></div></a>
									<?php endif; ?>
								</div>
								<div class="featured-content">
									<div class="article-meta">
										<?php
										$categories = get_the_category( $post->ID );
										if ( ! empty( $categories ) ) :
											?>
											<span class="cat-label"><?php echo esc_html( $categories[0]->name ); ?></span>
										<?php endif; ?>
										<span class="posted-on"><?php echo get_the_date( '', $post->ID ); ?></span>
									</div>
									<h3 class="featured-title"><a href="<?php echo get_permalink( $post->ID ); ?>"><?php echo get_the_title( $post->ID ); ?></a></h3>
								</div>
							</article>
							<?php
							$rank++;
						endforeach;
						wp_reset_postdata();
					} else {
						echo '<p>' . esc_html__( '集計中...', 'logishift' ) . '</p>';
					}
				}
				?>
			</div>
		</div>
	</section>

</main>

<?php
get_footer();
