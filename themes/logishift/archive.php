<?php
/**
 * The template for displaying archive pages
 *
 * @package LogiShift
 */

get_header();
?>

<main id="primary" class="site-main">
	<div class="container">
		<div class="page-header">
			<?php
			the_archive_title( '<h1 class="page-title">', '</h1>' );
			the_archive_description( '<div class="archive-description">', '</div>' );
			?>
		</div>

		<div class="content-sidebar-wrap">
			<div class="content-area">
				<?php if ( have_posts() ) : ?>
					<div class="article-list">
						<?php
						while ( have_posts() ) :
							the_post();
							?>
							<article id="post-<?php the_ID(); ?>" <?php post_class( 'article-card horizontal' ); ?>>
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
									<h2 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
									<div class="article-excerpt">
										<?php the_excerpt(); ?>
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
								'prev_text' => '<',
								'next_text' => '>',
							)
						);
						?>
					</div>

				<?php else : ?>
					<p><?php esc_html_e( '記事が見つかりませんでした。', 'logishift' ); ?></p>
				<?php endif; ?>
			</div>

			<?php get_sidebar(); ?>
		</div>
	</div>
</main>

<?php
get_footer();
