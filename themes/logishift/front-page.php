<?php
/**
 * The template for displaying the front page
 *
 * @package LogiShift
 */

get_header();
?>

<main id="primary" class="site-main">

	<!-- Hero Section -->
	<section class="hero-section">
		<div class="container">
			<div class="hero-content">
				<h2 class="hero-title"><?php esc_html_e( 'LogiShift your Business.', 'logishift' ); ?></h2>
				<p class="hero-description"><?php esc_html_e( '物流の「今」を変え、「未来」を創る。DXと戦略で描く新しい成長軌道。', 'logishift' ); ?></p>
				<a href="#latest-articles" class="button hero-cta"><?php esc_html_e( '記事を読む', 'logishift' ); ?></a>
			</div>
		</div>
	</section>

	<!-- Latest Articles -->
	<section id="latest-articles" class="latest-articles-section">
		<div class="container">
			<div class="section-header">
				<h3 class="section-title"><?php esc_html_e( '新着記事', 'logishift' ); ?></h3>
			</div>

			<div class="article-grid">
				<?php
				$args = array(
					'post_type'      => 'post',
					'posts_per_page' => 6,
				);
				$latest_query = new WP_Query( $args );

				if ( $latest_query->have_posts() ) :
					while ( $latest_query->have_posts() ) :
						$latest_query->the_post();
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
								<h4 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h4>
							</div>
						</article>
						<?php
					endwhile;
					wp_reset_postdata();
				else :
					?>
					<p><?php esc_html_e( '記事がまだありません。', 'logishift' ); ?></p>
				<?php endif; ?>
			</div>
			
			<div class="view-more-container" style="text-align: center; margin-top: var(--spacing-xl);">
				<a href="<?php echo esc_url( get_permalink( get_option( 'page_for_posts' ) ) ); ?>" class="button outline"><?php esc_html_e( 'もっと見る', 'logishift' ); ?></a>
			</div>
		</div>
	</section>

	<!-- Category Pickup: Cost Reduction -->
	<section class="category-pickup-section">
		<div class="container">
			<div class="section-header">
				<h3 class="section-title"><?php esc_html_e( 'コスト削減', 'logishift' ); ?></h3>
				<a href="<?php echo esc_url( get_category_link( get_category_by_slug( 'cost-reduction' ) ) ); ?>" class="section-link"><?php esc_html_e( '一覧へ', 'logishift' ); ?></a>
			</div>
			<!-- TODO: Implement Category Query Loop -->
		</div>
	</section>

	<!-- About Section -->
	<section class="about-section">
		<div class="container">
			<div class="about-content" style="text-align: center; max-width: 800px; margin: 0 auto;">
				<h3><?php esc_html_e( 'About LogiShift', 'logishift' ); ?></h3>
				<p><?php esc_html_e( 'LogiShiftは、物流担当者と経営層のための課題解決メディアです。現場のノウハウから最新のDX事例まで、ビジネスを加速させる情報をお届けします。', 'logishift' ); ?></p>
				<a href="<?php echo esc_url( home_url( '/about/' ) ); ?>" class="button text-link"><?php esc_html_e( '運営者情報へ', 'logishift' ); ?></a>
			</div>
		</div>
	</section>

</main>

<?php
get_footer();
