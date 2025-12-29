<?php
/**
 * The template for displaying search results pages
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
			<span class="current"><?php printf( esc_html__( '「%s」の検索結果', 'logishift' ), '<span>' . get_search_query() . '</span>' ); ?></span>
		</div>

		<div class="content-sidebar-wrap">
			<div class="content-area">
				<header class="page-header">
					<h1 class="page-title">
						<?php
						printf( esc_html__( '検索結果: %s', 'logishift' ), '<span>' . get_search_query() . '</span>' );
						?>
					</h1>
				</header>

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
									<h2 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
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
								'prev_text' => '&lt;',
								'next_text' => '&gt;',
							)
						);
						?>
					</div>

				<?php else : ?>

					<div class="no-results">
						<p><?php esc_html_e( 'お探しのキーワードに一致する記事は見つかりませんでした。別のキーワードをお試しください。', 'logishift' ); ?></p>
						<?php get_search_form(); ?>
					</div>

				<?php endif; ?>
			</div>

			<?php get_sidebar(); ?>
		</div>
	</div>
</main>

<?php
get_footer();
