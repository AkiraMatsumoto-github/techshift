<?php
/**
 * The template for displaying the front page
 * SEO-optimized design based on content_strategy.md
 *
 * @package TechShift
 */

get_header();
?>

<main id="primary" class="site-main">
	<!-- Hero Section (Slider) - Kept as requested -->
	<section class="hero-slider-section">
		<div class="swiper hero-slider-container">
			<div class="swiper-wrapper">
				<?php
				$hero_args = array(
					'posts_per_page' => 5,
					'orderby'        => 'date',
					'order'          => 'DESC',
					'tax_query'      => array(
						array(
							'taxonomy' => 'post_tag',
							'field'    => 'slug',
							'terms'    => 'pickup',
						),
					),
				);
				$hero_query = new WP_Query( $hero_args );
				if ( ! $hero_query->have_posts() ) {
					// Fallback
					$hero_query = new WP_Query( array( 'post_type' => 'post', 'posts_per_page' => 5 ) );
				}

				if ( $hero_query->have_posts() ) :
					while ( $hero_query->have_posts() ) :
						$hero_query->the_post();
						$thumb_url = has_post_thumbnail() ? get_the_post_thumbnail_url( get_the_ID(), 'full' ) : get_template_directory_uri() . '/assets/images/hero-bg.png';
						$categories = get_the_category();
						$cat_name = ! empty( $categories ) ? $categories[0]->name : 'TECHSHIFT';
						?>
						<div class="swiper-slide" style="background-image: url('<?php echo esc_url( $thumb_url ); ?>');">
							<a href="<?php the_permalink(); ?>" class="hero-full-link"><span class="screen-reader-text"><?php the_title(); ?></span></a>
							<div class="hero-slide-overlay"></div>
							<div class="hero-slide-content">
								<div class="hero-meta-line">
									<span class="hero-cat-label"><?php echo esc_html( $cat_name ); ?></span>
									<span class="hero-slide-date"><?php echo get_the_date(); ?></span>
								</div>
								<h2 class="hero-slide-title">
									<?php the_title(); ?>
								</h2>
							</div>
						</div>
						<?php
					endwhile;
					wp_reset_postdata();
				endif;
				?>
			</div>
			<div class="swiper-pagination"></div>
			<div class="swiper-button-prev"></div>
			<div class="swiper-button-next"></div>
		</div>
	</section>

	<!-- Market Pulse (Dashboard) -->
	<section class="market-pulse-section">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title">Technology Pulse <span style="font-size:0.6em; color:var(--color-text-secondary);"></span></h2>
			</div>
			
			<div class="article-grid dashboard-grid">
				<?php
				// Fetch Latest TechShift Briefings (Category: summary)
				$dashboard_query = new WP_Query([
					'category_name' => 'summary',
					'posts_per_page' => 4, // Show more
					'orderby' => 'date',
					'order' => 'DESC'
				]);
                
				if ( $dashboard_query->have_posts() ) :
					while ( $dashboard_query->have_posts() ) : $dashboard_query->the_post();
						$phase = get_post_meta(get_the_ID(), '_techshift_phase', true);
						$impact = get_post_meta(get_the_ID(), '_techshift_impact', true);
                        
                        // Get Summary
                        $summary_json = get_post_meta(get_the_ID(), '_ai_structured_summary', true);
                        $summary_text = '';
                        if ($summary_json) {
                            $data = json_decode($summary_json, true);
                            if (json_last_error() === JSON_ERROR_NONE && !empty($data['summary'])) {
                                $summary_text = $data['summary'];
                            }
                        }

						$i_val = intval($impact);
						$i_class = ($i_val > 60) ? 'accelerated' : (($i_val < 40) ? 'delayed' : 'neutral');
                        
                        // Get Region from Tag (First tag usually)
                        $post_tags = get_the_tags();
                        $region_label = ($post_tags) ? $post_tags[0]->name : 'Global';
				?>
				<article class="article-card dashboard-card">
                    <a href="<?php the_permalink(); ?>" class="card-overlay-link" aria-hidden="true" tabindex="-1"></a>
					
					<div class="dashboard-metrics">
                        <!-- Region -->
                        <div class="metric-box region-box">
							<span class="metric-label">Region</span>
							<span class="metric-value"><?php echo esc_html($region_label); ?></span>
						</div>
                        <!-- Phase (formerly Regime) -->
						<div class="metric-box">
							<span class="metric-label">Phase</span>
							<span class="metric-value"><?php echo $phase ? esc_html($phase) : '-'; ?></span>
						</div>
                        <!-- Impact (formerly Sentiment) -->
						<div class="metric-box">
							<span class="metric-label">Impact</span>
							<span class="metric-value impact-<?php echo $i_class; ?>"><?php echo $impact !== '' ? esc_html($impact) : '-'; ?></span>
						</div>
					</div>
					
					<h3 class="dashboard-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
					
                    <?php if ($summary_text) : ?>
                        <div class="dashboard-scenario-teaser">
                            <span class="scenario-text"><?php echo esc_html($summary_text); ?></span>
                        </div>
                    <?php endif; ?>

                    <div class="dashboard-footer">
                        <span class="date-badge"><?php echo get_the_date('m/d'); ?></span>
                        <span class="read-briefing-text">Read Briefing &rarr;</span>
                    </div>
				</article>
				<?php 
					endwhile;
                    wp_reset_postdata();
                else :
                    echo '<p style="color:var(--color-text-secondary);">' . esc_html__('No scenarios available yet.', 'techshift') . '</p>';
				endif;
				?>
			</div>
		</div>
	</section>

	<!-- Latest News Stream -->
	<section class="latest-news-section">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title">Latest News</h2>
			</div>
			
			<div class="article-grid">
				<?php
				$news_query = new WP_Query([
					'posts_per_page' => 6,
					'ignore_sticky_posts' => 1,
					'tax_query' => array(
						array(
							'taxonomy' => 'category',
							'field'    => 'slug',
							'terms'    => 'summary',
							'operator' => 'NOT IN',
						),
					),
				]);
				
				if ( $news_query->have_posts() ) :
					while ( $news_query->have_posts() ) : $news_query->the_post();
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
							<h3 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
						</div>
					</article>
				<?php
					endwhile;
					wp_reset_postdata();
				endif;
				?>
			</div>
		</div>
	</section>

	<!-- Ranking Section (Restored) -->
	<section id="popular-articles" class="popular-articles-section" style="background-color: var(--color-bg-secondary);">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '人気記事ランキング', 'techshift' ); ?></h2>
			</div>

			<div class="featured-grid">
				<?php
				if ( function_exists( 'techshift_get_popular_posts' ) ) {
					$popular_posts = techshift_get_popular_posts( 7, 5 ); // 5 posts for ranking

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

			<div class="section-footer" style="text-align: right; margin-top: var(--spacing-md);">
				<a href="<?php echo esc_url( home_url( '/ranking/' ) ); ?>" class="text-link-arrow"><?php esc_html_e( 'ランキング一覧を見る', 'techshift' ); ?> &rarr;</a>
			</div>
		</div>
	</section>

	<!-- Asset Class / Sector Section (Reusing Industry Layout) -->
	<section class="industry-tags-section" style="padding: var(--spacing-section) 0;">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '主要セクター (Tech Sectors)', 'techshift' ); ?></h2>
			</div>

			<?php
			$industry_tags = array(
				array( 'slug' => 'advanced-ai', 'name' => 'Advanced AI' ),
				array( 'slug' => 'robotics', 'name' => 'Robotics & Mobility' ),
				array( 'slug' => 'quantum', 'name' => 'Quantum & Semi' ),
				array( 'slug' => 'green-tech', 'name' => 'Green Tech' ),
				array( 'slug' => 'life-science', 'name' => 'Life Science' ),
				array( 'slug' => 'space-aero', 'name' => 'Space & Aero' ),
			);
			?>

			<!-- Filter Tabs -->
			<div class="region-filter-tabs industry-tabs">
				<?php foreach ( $industry_tags as $index => $industry_tag ) : 
					$active_class = $index === 0 ? 'active' : '';
				?>
					<button class="region-tab <?php echo $active_class; ?>" data-industry="<?php echo esc_attr( $industry_tag['slug'] ); ?>">
						<?php echo esc_html( $industry_tag['name'] ); ?>
					</button>
				<?php endforeach; ?>
			</div>

			<!-- Content Blocks -->
			<div class="industry-content-container">
				<?php foreach ( $industry_tags as $index => $industry_tag ) : 
					$display_style = $index === 0 ? 'block' : 'none';
				?>
					<div class="industry-tag-block" id="industry-block-<?php echo esc_attr( $industry_tag['slug'] ); ?>" style="display: <?php echo $display_style; ?>;">
						<div class="article-grid">
							<?php
							$ind_args = array(
								'category_name'  => $industry_tag['slug'],
								'posts_per_page' => 3,
								'orderby'        => 'date',
								'order'          => 'DESC',
                                'tax_query'      => array(
                                    array(
                                        'taxonomy' => 'category',
                                        'field'    => 'slug',
                                        'terms'    => 'summary',
                                        'operator' => 'NOT IN',
                                    ),
                                ),
							);
							$ind_query = new WP_Query( $ind_args );

							if ( $ind_query->have_posts() ) :
								while ( $ind_query->have_posts() ) :
									$ind_query->the_post();
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
											<h3 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
										</div>
									</article>
									<?php
								endwhile;
								wp_reset_postdata();
							else:
								?>
								<p class="no-posts"><?php esc_html_e( 'No Briefing Available.', 'techshift' ); ?></p>
								<?php
							endif;
							?>
						</div>
						<div class="section-footer" style="text-align: right; margin-top: var(--spacing-md);">
							<?php
							$slugs = explode( ',', $industry_tag['slug'] );
							$primary_slug = trim( $slugs[0] );
							$term = get_term_by( 'slug', $primary_slug, 'category' );
							if ( $term && ! is_wp_error( $term ) ) :
								$term_link = get_term_link( $term );
								if ( ! is_wp_error( $term_link ) ) :
									?>
									<a href="<?php echo esc_url( $term_link ); ?>" class="text-link-arrow"><?php printf( esc_html__( 'Explore %s', 'techshift' ), esc_html( $industry_tag['name'] ) ); ?> &rarr;</a>
									<?php
								endif;
							endif;
							?>
						</div>
					</div>
				<?php endforeach; ?>
			</div>
		</div>
	</section>

	<!-- Theme Tags Section -->
	<section class="theme-tags-section" style="background-color: var(--color-bg-secondary);">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '注目トピック (Deep Dives)', 'techshift' ); ?></h2>
			</div>

			<?php
			$theme_tags = array(
				array( 'slug' => 'foundation-models', 'name' => 'Foundation Models' ),
				array( 'slug' => 'autonomous-driving', 'name' => 'Autonomous Driving' ),
				array( 'slug' => 'fusion-energy', 'name' => 'Fusion Energy' ),
				array( 'slug' => 'ai-drug-discovery', 'name' => 'AI Drug Discovery' ),
				array( 'slug' => 'quantum-gate-computing', 'name' => 'Quantum Computing' ),
				array( 'slug' => 'reusable-rockets', 'name' => 'Starship & Rocket' ),
			);
			?>

			<!-- Filter Tabs -->
			<div class="region-filter-tabs theme-tabs">
				<?php foreach ( $theme_tags as $index => $theme_tag ) : 
					$active_class = $index === 0 ? 'active' : '';
				?>
					<button class="region-tab <?php echo $active_class; ?>" data-theme="<?php echo esc_attr( $theme_tag['slug'] ); ?>">
						<?php echo esc_html( $theme_tag['name'] ); ?>
					</button>
				<?php endforeach; ?>
			</div>

			<!-- Content Blocks -->
			<div class="theme-content-container">
				<?php foreach ( $theme_tags as $index => $theme_tag ) : 
					$display_style = $index === 0 ? 'block' : 'none';
				?>
					<div class="theme-tag-block" id="theme-block-<?php echo esc_attr( $theme_tag['slug'] ); ?>" style="display: <?php echo $display_style; ?>;">
						<div class="article-grid">
							<?php
							$tag_args = array(
								'category_name'  => $theme_tag['slug'],
								'posts_per_page' => 3,
								'orderby'        => 'date',
								'order'          => 'DESC',
							);
							$tag_query = new WP_Query( $tag_args );

							if ( $tag_query->have_posts() ) :
								while ( $tag_query->have_posts() ) :
									$tag_query->the_post();
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
											<h3 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
										</div>
									</article>
									<?php
								endwhile;
								wp_reset_postdata();
							endif;
							?>
						</div>
						<div class="section-footer" style="text-align: right; margin-top: var(--spacing-md);">
							<?php
							$slugs = explode( ',', $theme_tag['slug'] );
							$primary_slug = trim( $slugs[0] );
							$term = get_term_by( 'slug', $primary_slug, 'category' );
							if ( $term && ! is_wp_error( $term ) ) :
								$term_link = get_term_link( $term );
								if ( ! is_wp_error( $term_link ) ) :
									?>
									<a href="<?php echo esc_url( $term_link ); ?>" class="text-link-arrow"><?php printf( esc_html__( 'Explore %s', 'techshift' ), esc_html( $theme_tag['name'] ) ); ?> &rarr;</a>
									<?php
								endif;
							endif;
							?>
						</div>
					</div>
				<?php endforeach; ?>
			</div>
		</div>
	</section>

</main>



<?php
get_footer();
