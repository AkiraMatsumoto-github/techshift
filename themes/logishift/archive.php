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
								<div class="article-excerpt">
									<?php echo wp_trim_words( get_the_excerpt(), 30 ); ?>
								</div>
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

</main>

<?php
get_footer();
