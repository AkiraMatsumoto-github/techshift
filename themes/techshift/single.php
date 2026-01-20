<?php
/**
 * The template for displaying all single posts
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
                            
                            <?php
                            // TechShift Custom Meta
                            $impact = get_post_meta( get_the_ID(), '_techshift_impact', true );
                            $phase = get_post_meta( get_the_ID(), '_techshift_phase', true );
                            
                            if ( $impact !== '' || $phase ) : ?>
                                <div class="techshift-impact-meta">
                                    <?php if ( $phase ) : ?>
                                        <span class="market-chip phase-label"><?php echo esc_html( $phase ); ?></span>
                                    <?php endif; ?>
                                    
                                    <?php if ( $impact !== '' ) : 
                                        $i_val = intval( $impact );
                                        $i_class = ($i_val > 60) ? 'accelerated' : (($i_val < 40) ? 'delayed' : 'neutral');
                                        $i_text = ($i_val > 60) ? 'Accelerated' : (($i_val < 40) ? 'Delayed' : 'Neutral');
                                    ?>
                                        <span class="market-chip impact-label <?php echo $i_class; ?>">
                                            Impact: <?php echo $i_val; ?> (<?php echo $i_text; ?>)
                                        </span>
                                    <?php endif; ?>
                                </div>
                            <?php endif; ?>

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
									'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'techshift' ),
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
								<div class="share-buttons-container">
									<button class="button share-twitter">X (Twitter)</button>
									<button class="button share-facebook">Facebook</button>
								</div>
							</div>
						</footer>
					</article>

					<!-- Related Posts -->
					<div class="related-posts">
						<h3 class="related-title"><?php esc_html_e( '関連記事', 'techshift' ); ?></h3>
						<div class="article-grid">
							<?php
                            // Improved Related Posts Logic
                            $related_tags = get_the_tags();
                            $related_args = array(
								'post_type'      => 'post',
								'posts_per_page' => 3,
								'post__not_in'   => array( get_the_ID() ),
								'orderby'        => 'date',
                                'order'          => 'DESC',
							);

                            // Priority 1: Tags
                            if ( $related_tags ) {
                                $tag_ids = array();
                                foreach( $related_tags as $t ) $tag_ids[] = $t->term_id;
                                $related_args['tag__in'] = $tag_ids;
                            } 
                            // Priority 2: Category (if no tags, or fallback logic needed - but let's stick to simple tag priority first, or mix?)
                            // Let's rely on tags if present. If query returns 0, we could fallback. 
                            // For simplicity and performance, let's add category as well if tags are few? 
                            // Better approach: Try tags first.
                            
                            $related_query = new WP_Query( $related_args );
                            
                            // Fallback to Category if NO posts found by tags (or no tags)
                            if ( ! $related_query->have_posts() && ! empty( $categories ) ) {
                                unset($related_args['tag__in']);
                                $related_args['category__in'] = array( $categories[0]->term_id );
                                $related_query = new WP_Query( $related_args );
                            }

							if ( $related_query->have_posts() ) :
								while ( $related_query->have_posts() ) : $related_query->the_post();

									// Metadata
									$phase = get_post_meta(get_the_ID(), '_techshift_phase', true);
									$impact = get_post_meta(get_the_ID(), '_techshift_impact', true);
									$i_val = intval($impact);
									
									// Summary logic
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

									// Meter Visual Logic
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
												<h4 class="dashboard-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h4>
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
								wp_reset_postdata();
							else :
								echo '<p>' . esc_html__( '関連記事はありません。', 'techshift' ) . '</p>';
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
