<?php
/**
 * Template Name: Ranking Page
 * The template for displaying the ranking page
 *
 * @package LogiShift
 */

get_header();
?>

<main id="primary" class="site-main">
	
	<!-- Ranking Header -->
	<section class="archive-hero">
		<div class="container">
			<h1 class="archive-title"><?php esc_html_e( '人気記事ランキング', 'logishift' ); ?></h1>
			<div class="archive-description">
				<?php esc_html_e( 'LogiShiftで最も読まれている記事をランキング形式でご紹介します。', 'logishift' ); ?>
			</div>
		</div>
	</section>

	<section class="ranking-section" style="padding: var(--spacing-2xl) 0;">
		<div class="container">
			
			<!-- Time Period Tabs -->
			<div class="region-filter-tabs ranking-tabs" style="justify-content: center; margin-bottom: 40px;">
				<button class="region-tab active" data-period="7">
					<?php esc_html_e( '7日間', 'logishift' ); ?>
				</button>
				<button class="region-tab" data-period="14">
					<?php esc_html_e( '14日間', 'logishift' ); ?>
				</button>
				<button class="region-tab" data-period="30">
					<?php esc_html_e( '30日間', 'logishift' ); ?>
				</button>
				<button class="region-tab" data-period="60">
					<?php esc_html_e( '60日間', 'logishift' ); ?>
				</button>
			</div>

			<!-- Ranking Content Blocks -->
			<?php
			$periods = array( 7, 14, 30, 60 );
			
			foreach ( $periods as $index => $days ) :
				$display_style = ( $index === 0 ) ? 'block' : 'none';
				
				// Calculate date range for display
				$start_date = date_i18n( 'Y年n月j日', strtotime( "-$days days" ) );
				$end_date   = date_i18n( 'Y年n月j日' );
				?>
				<div class="ranking-block" id="ranking-block-<?php echo esc_attr( $days ); ?>" style="display: <?php echo $display_style; ?>;">
					
					<p class="ranking-period-info" style="text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9em;">
						<?php printf( esc_html__( '集計期間: %s 〜 %s', 'logishift' ), $start_date, $end_date ); ?>
					</p>

					<div class="featured-grid">
						<?php
						if ( function_exists( 'logishift_get_popular_posts' ) ) {
							// Get top 20 posts for this period
							$popular_posts = logishift_get_popular_posts( $days, 20 );

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
												<?php if ( isset( $post->views ) ) : ?>
													<span class="views-count" style="margin-left: 10px; color: #888; font-size: 0.9em;">
														<i class="fas fa-eye"></i> <?php echo number_format( $post->views ); ?> views
													</span>
												<?php endif; ?>
											</div>
											<h3 class="featured-title"><a href="<?php echo get_permalink( $post->ID ); ?>"><?php echo get_the_title( $post->ID ); ?></a></h3>
										</div>
									</article>
									<?php
									$rank++;
								endforeach;
								wp_reset_postdata();
							} else {
								echo '<p style="text-align:center; width:100%;">' . esc_html__( '集計データがありません。', 'logishift' ) . '</p>';
							}
						}
						?>
					</div>
				</div>
			<?php endforeach; ?>

		</div>
	</section>

</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
	const tabs = document.querySelectorAll('.ranking-tabs .region-tab');
	const blocks = document.querySelectorAll('.ranking-block');

	tabs.forEach(tab => {
		tab.addEventListener('click', function() {
			const selectedPeriod = this.getAttribute('data-period');

			// Switch Tabs
			tabs.forEach(t => t.classList.remove('active'));
			this.classList.add('active');

			// Switch Content
			blocks.forEach(block => {
				if (block.id === 'ranking-block-' + selectedPeriod) {
					block.style.display = 'block';
					
					// Optional: Add simple fade-in effect
					block.style.opacity = 0;
					setTimeout(() => {
						block.style.opacity = 1;
						block.style.transition = 'opacity 0.3s ease';
					}, 10);
				} else {
					block.style.display = 'none';
				}
			});
		});
	});
});
</script>

<?php
get_footer();
