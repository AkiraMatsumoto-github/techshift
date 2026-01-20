<?php
/**
 * The template for displaying search results pages
 *
 * @package TechShift
 */

get_header();
?>

<main id="primary" class="site-main">
	<div class="container">
		
		<!-- Breadcrumb -->
		<div class="breadcrumb">
			<span><a href="<?php echo esc_url( home_url( '/' ) ); ?>">Home</a></span>
			<span class="sep">&gt;</span>
			<span class="current"><?php printf( esc_html__( '「%s」の検索結果', 'techshift' ), '<span>' . get_search_query() . '</span>' ); ?></span>
		</div>

		<div class="content-sidebar-wrap">
			<div class="content-area">
				<header class="page-header">
					<h1 class="page-title">
						<?php
						printf( esc_html__( '検索結果: %s', 'techshift' ), '<span>' . get_search_query() . '</span>' );
						?>
					</h1>
				</header>

				<?php if ( have_posts() ) : ?>
					<div class="article-grid">
						<?php
						while ( have_posts() ) :
							the_post();
							// Metadata
							$phase = get_post_meta(get_the_ID(), '_techshift_phase', true);
							$impact = get_post_meta(get_the_ID(), '_techshift_impact', true);
							$i_val = intval($impact);
							
							// Summary
							$summary_json = get_post_meta(get_the_ID(), '_ai_structured_summary', true);
							$summary_text = '';
							if ($summary_json) {
								$data = json_decode($summary_json, true);
								if (json_last_error() === JSON_ERROR_NONE && !empty($data['summary'])) {
									$summary_text = mb_substr($data['summary'], 0, 80) . '...';
								}
							}
							if (!$summary_text) {
								$summary_text = get_the_excerpt(); 
							}

							// Meter Logic
							$impact_label_text = ($i_val > 50) ? '+' . ($i_val - 50) : (($i_val < 50) ? '-' . (50 - $i_val) : '±0');
							$bar_width = abs($i_val - 50); 
							$bar_left = ($i_val < 50) ? $i_val : 50;
							$meter_color_class = ($i_val >= 50) ? 'accelerated' : 'delayed';
							if ($i_val == 50) $meter_color_class = 'neutral';
							?>
							<article id="post-<?php the_ID(); ?>" class="dashboard-card mobile-horizontal">
								<a href="<?php the_permalink(); ?>" class="card-overlay-link" aria-hidden="true" tabindex="-1"></a>
								
								<div class="card-header-line">
									<span class="sector-badge">
										<?php
										$categories = get_the_category();
										if ( ! empty( $categories ) ) :
											?>
											<span class="sector-icon">●</span> <?php echo esc_html( $categories[0]->name ); ?>
										<?php endif; ?>
									</span>
									<span class="date-label" style="font-family:var(--font-heading);"><?php echo get_the_date('Y.m.d'); ?></span>
								</div>

								<div class="card-body-flex">
									<div class="card-content-side">
										<h2 class="dashboard-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>

									</div>
									<?php if (has_post_thumbnail()): ?>
									<div class="card-thumbnail-side">
										<?php the_post_thumbnail('thumbnail'); ?>
									</div>
									<?php endif; ?>
								</div>
								
								<div style="margin-top: auto;">
									<?php if ($phase) : ?>
										<div class="phase-status-line" style="margin-bottom: 12px;">
											<span class="phase-label-mini">Phase Shift (Before &rarr; After)</span>
											<span class="phase-value-text"><?php echo esc_html($phase); ?></span>
										</div>
									<?php endif; ?>

									<?php if ($impact !== '') : ?>
									<div class="impact-section">
										<div class="impact-header-row">
											<span class="impact-title">Impact</span>
											<span class="impact-score-display"><?php echo $impact_label_text; ?></span>
										</div>
										<div class="diverging-meter-container">
											<div class="meter-center-line"></div>
											<div class="diverging-bar <?php echo $meter_color_class; ?>" 
													style="left: <?php echo $bar_left; ?>%; width: <?php echo $bar_width; ?>%;">
											</div>
										</div>
										<div class="meter-axis-labels">
											<span>Delayed</span>
											<span>Neutral</span>
											<span>Accelerated</span>
										</div>
									</div>
									<?php endif; ?>

									<a href="<?php the_permalink(); ?>" class="card-footer-link" style="margin-top: 12px; display: block;">
										Read Analysis <span class="arrow">&rarr;</span>
									</a>
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
						<p><?php esc_html_e( 'お探しのキーワードに一致する記事は見つかりませんでした。別のキーワードをお試しください。', 'techshift' ); ?></p>
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
