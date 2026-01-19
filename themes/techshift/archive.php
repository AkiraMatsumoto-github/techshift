<?php
/**
 * The template for displaying archive pages
 * Modern design matching front-page.php
 *
 * @package TechShift
 */

get_header();
?>

<main id="primary" class="site-main">
	
	<!-- Archive Header -->
	<section class="archive-hero" style="background-color: var(--color-bg-primary); padding-bottom: 0;">
		<div class="container">
			<?php
			$object = get_queried_object();
            $slug = isset($object->slug) ? $object->slug : '';
            
            // Symbol Mapping
            $symbols = [
                'us' => 'FOREXCOM:SPXUSD', 'usa' => 'FOREXCOM:SPXUSD',
                'jp' => 'TVC:NI225', 'japan' => 'TVC:NI225',
                'china' => 'TVC:SHCOMP',
                'europe' => 'TVC:DEU40',
                'india' => 'NSE:NIFTY',
                'crypto' => 'BINANCE:BTCUSDT',
                'fx' => 'FX:USDJPY',
                'stocks' => 'FOREXCOM:SPXUSD', // Default for stocks
                'commodities' => 'TVC:GOLD',
                'tech' => 'NASDAQ:NDX',
                'semiconductor' => 'NASDAQ:SOX',
            ];
            
            $chart_symbol = isset($symbols[$slug]) ? $symbols[$slug] : null;
			?>
            
            <div class="archive-header-content" style="margin-bottom: var(--spacing-lg);">
			    <h1 class="archive-title"><?php the_archive_title(); ?></h1>
			    <?php if ( get_the_archive_description() ) : ?>
				    <div class="archive-description"><?php the_archive_description(); ?></div>
			    <?php endif; ?>
            </div>
            
            <?php if ($chart_symbol) : ?>
                <!-- Regional/Topic Chart -->
                <div class="regional-chart-widget" style="height: 400px; margin-bottom: -40px; border: 1px solid var(--color-bg-tertiary); border-radius: var(--radius-lg); overflow: hidden;">
                    <!-- TradingView Widget BEGIN -->
                    <div class="tradingview-widget-container" style="height:100%;width:100%">
                        <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
                        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                        {
                        "autosize": true,
                        "symbol": "<?php echo $chart_symbol; ?>",
                        "interval": "D",
                        "timezone": "Asia/Tokyo",
                        "theme": "dark",
                        "style": "1",
                        "locale": "ja",
                        "enable_publishing": false,
                        "hide_top_toolbar": true,
                        "hide_legend": false,
                        "save_image": false,
                        "calendar": false,
                        "hide_volume": true,
                        "support_host": "https://www.tradingview.com"
                        }
                        </script>
                    </div>
                    <!-- TradingView Widget END -->
                </div>
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
									<h3 class="dashboard-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
									<?php if ($summary_text): ?>
										<p class="card-summary"><?php echo esc_html($summary_text); ?></p>
									<?php endif; ?>
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
										<span class="impact-title">Timeline Impact</span>
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

								<div class="card-footer-link" style="margin-top: 12px;">
									Read Analysis <span class="arrow">&rarr;</span>
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
				<p class="no-posts"><?php esc_html_e( '記事が見つかりませんでした。', 'techshift' ); ?></p>
			<?php endif; ?>
		</div>
	</section>

	<!-- Contextual Popular Articles -->
	<section class="popular-articles-section" style="background-color: var(--color-light-gray); margin-top: 40px; padding-top: 40px; border-top: 1px solid var(--color-border-gray);">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( 'このカテゴリの人気記事', 'techshift' ); ?></h2>
			</div>

			<div class="featured-grid">
				<?php
				if ( function_exists( 'techshift_get_popular_posts' ) ) {
					// Get current term context
					$obj = get_queried_object();
					$term_id = isset( $obj->term_id ) ? $obj->term_id : null;
					$taxonomy = isset( $obj->taxonomy ) ? $obj->taxonomy : 'category';

					// Fetch filtered popular posts
					$popular_posts = techshift_get_popular_posts( 30, 5, $term_id, $taxonomy );

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
						echo '<p>' . esc_html__( '集計中...', 'techshift' ) . '</p>';
					}
				}
				?>
			</div>
		</div>
	</section>

</main>

<?php
get_footer();
