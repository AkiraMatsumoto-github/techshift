<?php
/**
 * The template for displaying the front page
 * SEO-optimized design based on content_strategy.md
 *
 * @package LogiShift
 */

get_header();
?>

<main id="primary" class="site-main">

	<!-- Hero Section -->
	<!-- Hero Section (Slider) -->
	<section class="hero-slider-section">
		<div class="swiper hero-slider-container">
			<div class="swiper-wrapper">
				<?php
				// Arguments for the Query
				// First, try to get posts with tag 'pickup'
				$hero_args = array(
					'tag'            => 'pickup',
					'posts_per_page' => 5,
					'orderby'        => 'date',
					'order'          => 'DESC',
				);
				$hero_query = new WP_Query( $hero_args );

				// Fallback: If no pickup posts, get latest 5 posts
				if ( ! $hero_query->have_posts() ) {
					$hero_args = array(
						'post_type'      => 'post',
						'posts_per_page' => 5,
						'orderby'        => 'date',
						'order'          => 'DESC',
					);
					$hero_query = new WP_Query( $hero_args );
				}

				if ( $hero_query->have_posts() ) :
					while ( $hero_query->have_posts() ) :
						$hero_query->the_post();
						$thumb_url = has_post_thumbnail() ? get_the_post_thumbnail_url( get_the_ID(), 'full' ) : get_template_directory_uri() . '/assets/images/hero-bg.png';
						$categories = get_the_category();
						$cat_name = ! empty( $categories ) ? $categories[0]->name : 'LOGISHIFT';
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
			<!-- If we need pagination -->
			<div class="swiper-pagination"></div>

			<!-- If we need navigation buttons -->
			<div class="swiper-button-prev"></div>
			<div class="swiper-button-next"></div>
		</div>
	</section>

	<!-- Featured Articles -->
	<section id="latest-articles" class="featured-articles-section">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '最新記事', 'logishift' ); ?></h2>
			</div>

			<div class="featured-grid">
				<?php
				$featured_args = array(
					'post_type'      => 'post',
					'posts_per_page' => 3,
					'orderby'        => 'date',
					'order'          => 'DESC',
				);
				$featured_query = new WP_Query( $featured_args );

				if ( $featured_query->have_posts() ) :
					while ( $featured_query->have_posts() ) :
						$featured_query->the_post();
						?>
						<article id="post-<?php the_ID(); ?>" <?php post_class( 'featured-card' ); ?>>
							<div class="featured-thumbnail">
								<?php if ( has_post_thumbnail() ) : ?>
									<a href="<?php the_permalink(); ?>"><?php the_post_thumbnail( 'large' ); ?></a>
								<?php else : ?>
									<a href="<?php the_permalink(); ?>"><div class="no-image"></div></a>
								<?php endif; ?>
							</div>
							<div class="featured-content">
								<div class="article-meta">
									<?php
									$categories = get_the_category();
									if ( ! empty( $categories ) ) :
										?>
										<span class="cat-label"><?php echo esc_html( $categories[0]->name ); ?></span>
									<?php endif; ?>
									<span class="posted-on"><?php echo get_the_date(); ?></span>
								</div>
								<h3 class="featured-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
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

	<!-- Popular Articles Section -->
	<section id="popular-articles" class="popular-articles-section" style="background-color: var(--color-light-gray);">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '人気記事', 'logishift' ); ?></h2>
			</div>

			<div class="featured-grid">
				<?php
				if ( function_exists( 'logishift_get_popular_posts' ) ) {
					$popular_posts = logishift_get_popular_posts( 7, 5 );

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

			<div style="text-align: right; margin-top: 24px;">
				<a href="<?php echo esc_url( home_url( '/ranking/' ) ); ?>" class="text-link-arrow">
					<?php esc_html_e( 'ランキング一覧へ', 'logishift' ); ?> →
				</a>
			</div>
		</div>
	</section>

	<?php
	// Category sections based on content_strategy.md
	$category_sections = array(
		array(
			'slug'        => 'logistics-dx',
			'name'        => '物流DX・トレンド',
			'description' => '物流業界の最新動向、2024年問題、DX推進の実践的ノウハウ',
		),
		array(
			'slug'        => 'warehouse-management',
			'name'        => '倉庫管理・WMS',
			'description' => 'WMS導入、在庫管理、ピッキング効率化の成功事例',
		),
		array(
			'slug'        => 'transportation',
			'name'        => '輸配送・TMS',
			'description' => '配車計画、ラストワンマイル、動態管理の最適化手法',
		),
		array(
			'slug'        => 'material-handling',
			'name'        => 'マテハン・ロボット',
			'description' => '自動倉庫、AGV/AMR、RFID導入の最新トレンド',
		),
		array(
			'slug'        => 'supply-chain',
			'name'        => 'サプライチェーン',
			'description' => 'SCM戦略、調達最適化、国際物流のベストプラクティス',
		),
		array(
			'slug'        => 'case-studies',
			'name'        => '事例',
			'description' => '企業の成功事例、現場インタビュー、導入効果の実績',
		),
	);

	foreach ( $category_sections as $cat_section ) :
		$cat_obj = get_category_by_slug( $cat_section['slug'] );
		if ( ! $cat_obj ) {
			continue;
		}
		?>
		<section class="category-section category-<?php echo esc_attr( $cat_section['slug'] ); ?>">
			<div class="container">
				<div class="section-header">
					<div class="section-header-content">
						<h2 class="section-title"><?php echo esc_html( $cat_section['name'] ); ?></h2>
						<p class="section-description"><?php echo esc_html( $cat_section['description'] ); ?></p>
					</div>
					<!-- Link removed from header -->
				</div>

				<div class="article-grid">
					<?php
					$cat_args = array(
						'category_name'  => $cat_section['slug'],
						'posts_per_page' => 3,
						'orderby'        => 'date',
						'order'          => 'DESC',
					);
					$cat_query = new WP_Query( $cat_args );

					if ( $cat_query->have_posts() ) :
						while ( $cat_query->have_posts() ) :
							$cat_query->the_post();
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
					else :
						?>
						<p class="no-posts"><?php esc_html_e( '記事がまだありません。', 'logishift' ); ?></p>
					<?php endif; ?>
				</div>

				<!-- Moved Button to Bottom -->
				<div style="text-align: right; margin-top: 24px;">
					<a href="<?php echo esc_url( get_category_link( $cat_obj ) ); ?>" class="text-link-arrow">
						<?php esc_html_e( '一覧へ', 'logishift' ); ?> →
					</a>
				</div>
			</div>
		</section>
		<?php
	endforeach;
	?>

	<!-- Global Trends Section with Regional Filtering -->
	<section class="global-trends-section">
		<div class="container">
			<div class="section-header">
				<div class="section-header-content">
					<h2 class="section-title"><?php esc_html_e( '海外トレンド', 'logishift' ); ?></h2>
					<p class="section-description"><?php esc_html_e( '米国・欧州・アジアの最新物流DX事例と日本への示唆', 'logishift' ); ?></p>
				</div>
			</div>

			<!-- Regional Filter Tabs -->
			<div class="region-filter-tabs">
				<?php
				$global_cat = get_category_by_slug( 'news-global' );
				$global_url = $global_cat ? get_category_link( $global_cat ) : '#';
				?>
				<button class="region-tab active" data-region="all" data-url="<?php echo esc_url( $global_url ); ?>"><?php esc_html_e( 'すべて', 'logishift' ); ?></button>
				
				<?php
				$regions = array(
					'usa'            => array( 'label' => 'アメリカ' ),
					'europe'         => array( 'label' => 'ヨーロッパ' ),
					'china'          => array( 'label' => '中国' ),
					'southeast-asia' => array( 'label' => '東南アジア' ),
					'japan' => array( 'label' => '日本' ),
				);

				foreach ( $regions as $slug => $info ) :
					$tag = get_term_by( 'slug', $slug, 'post_tag' );
					$url = $tag ? get_tag_link( $tag ) : '#';
					?>
					<button class="region-tab" data-region="<?php echo esc_attr( $slug ); ?>" data-url="<?php echo esc_url( $url ); ?>">
						<?php echo esc_html( $info['label'] ); ?>
					</button>
				<?php endforeach; ?>
			</div>

			<div class="global-articles-container">
				<?php
				// Get all global trend articles with regional tags
				$global_args = array(
					'category_name'  => 'news-global',
					'posts_per_page' => 6,
					'orderby'        => 'date',
					'order'          => 'DESC',
				);
				$global_query = new WP_Query( $global_args );

				if ( $global_query->have_posts() ) :
					?>
					<div class="article-grid global-grid">
						<?php
						while ( $global_query->have_posts() ) :
							$global_query->the_post();
							$post_tags = get_the_tags();
							$region_tags = array();
							
							if ( $post_tags ) {
								foreach ( $post_tags as $tag ) {
									if ( in_array( $tag->slug, array( 'usa', 'europe', 'china', 'southeast-asia', 'japan', 'global' ) ) ) {
										$region_tags[] = $tag->slug;
									}
								}
							}
							
							$region_data = ! empty( $region_tags ) ? implode( ' ', $region_tags ) : 'all';
							?>
							<article id="post-<?php the_ID(); ?>" <?php post_class( 'article-card global-article' ); ?> data-regions="<?php echo esc_attr( $region_data ); ?>">
								<div class="article-thumbnail">
									<?php if ( has_post_thumbnail() ) : ?>
										<a href="<?php the_permalink(); ?>"><?php the_post_thumbnail( 'medium' ); ?></a>
									<?php else : ?>
										<a href="<?php the_permalink(); ?>"><div class="no-image"></div></a>
									<?php endif; ?>
								</div>
								<div class="article-content">
									<div class="article-meta">
										<?php if ( ! empty( $region_tags ) ) : ?>
											<span class="region-label"><?php echo esc_html( $region_tags[0] ); ?></span>
										<?php endif; ?>
										<span class="posted-on"><?php echo get_the_date(); ?></span>
									</div>
									<h3 class="article-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
								</div>
							</article>
							<?php
						endwhile;
						wp_reset_postdata();
						?>
					</div>
					
					<!-- Show More Button -->
					<div class="global-show-more-container" style="text-align: right; margin-top: 24px;">
						<a href="<?php echo esc_url( $global_url ); ?>" class="text-link-arrow global-show-more-link">
							<?php esc_html_e( 'もっと見る', 'logishift' ); ?> →
						</a>
					</div>

				<?php else : ?>
					<p class="no-posts"><?php esc_html_e( '記事がまだありません。', 'logishift' ); ?></p>
				<?php endif; ?>
			</div>
		</div>
	</section>

	<!-- Industry-based Tag Sections -->
	<section class="industry-tags-section" style="background-color: var(--color-light-gray); padding: var(--spacing-section) 0;">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '業界別で探す', 'logishift' ); ?></h2>
			</div>

			<?php
			$industry_tags = array(
				array( 'slug' => 'manufacturing', 'name' => '製造業' ),
				array( 'slug' => 'retail', 'name' => '小売・流通' ),
				array( 'slug' => 'ecommerce', 'name' => 'EC・通販' ),
				array( 'slug' => '3pl-warehouse', 'name' => '3PL・倉庫' ),
				array( 'slug' => 'food-beverage', 'name' => '食品・飲料' ),
				array( 'slug' => 'apparel', 'name' => 'アパレル' ),
				array( 'slug' => 'medical', 'name' => '医薬品・医療' ),
			);
			?>

			<!-- Industry Tabs -->
			<div class="region-filter-tabs industry-tabs">
				<?php foreach ( $industry_tags as $index => $industry_tag ) : 
					$active_class = $index === 0 ? 'active' : '';
				?>
					<button class="region-tab <?php echo $active_class; ?>" data-industry="<?php echo esc_attr( $industry_tag['slug'] ); ?>">
						<?php echo esc_html( $industry_tag['name'] ); ?>
					</button>
				<?php endforeach; ?>
			</div>

			<!-- Industry Content Blocks -->
			<div class="industry-content-container">
				<?php foreach ( $industry_tags as $index => $industry_tag ) : 
					$display_style = $index === 0 ? 'block' : 'none';
				?>
					<div class="industry-tag-block" id="industry-block-<?php echo esc_attr( $industry_tag['slug'] ); ?>" style="display: <?php echo $display_style; ?>;">
						<div class="article-grid">
							<?php
							$ind_args = array(
								'tag'            => $industry_tag['slug'],
								'posts_per_page' => 3,
								'orderby'        => 'date',
								'order'          => 'DESC',
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
								<p class="no-posts"><?php esc_html_e( '記事がまだありません。', 'logishift' ); ?></p>
								<?php
							endif;
							?>
						</div>
						<div style="text-align: right; margin-top: 24px;">
							<a href="<?php echo esc_url( get_tag_link( get_term_by( 'slug', $industry_tag['slug'], 'post_tag' ) ) ); ?>" class="text-link-arrow">
								<?php echo esc_html( $industry_tag['name'] ); ?> <?php esc_html_e( 'の記事一覧', 'logishift' ); ?> →
							</a>
						</div>
					</div>
				<?php endforeach; ?>
			</div>
		</div>
	</section>

	<!-- Theme-based Tag Sections -->
	<section class="theme-tags-section">
		<div class="container">
			<div class="section-header">
				<h2 class="section-title"><?php esc_html_e( '課題別で探す', 'logishift' ); ?></h2>
			</div>

			<?php
			$theme_tags = array(
				array(
					'slug' => 'cost-reduction',
					'name' => 'コスト削減',
					'icon' => '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="theme-icon-svg"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>',
				),
				array(
					'slug' => 'labor-shortage',
					'name' => '人手不足対策',
					'icon' => '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="theme-icon-svg"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
				),
				array(
					'slug' => 'quality-improvement',
					'name' => '品質向上',
					'icon' => '',
				),
				array(
					'slug' => 'environment-sdgs',
					'name' => '環境・SDGs',
					'icon' => '',
				),
				array(
					'slug' => 'safety-bcp',
					'name' => '安全・BCP',
					'icon' => '',
				),
				array(
					'slug' => 'subsidy',
					'name' => '補助金・助成金',
					'icon' => '',
				),
			);
			?>

			<!-- Theme Tabs -->
			<div class="region-filter-tabs theme-tabs">
				<?php foreach ( $theme_tags as $index => $theme_tag ) : 
					$active_class = $index === 0 ? 'active' : '';
				?>
					<button class="region-tab <?php echo $active_class; ?>" data-theme="<?php echo esc_attr( $theme_tag['slug'] ); ?>">
						<!-- <?php echo $theme_tag['icon']; ?> -->
						<?php echo esc_html( $theme_tag['name'] ); ?>
					</button>
				<?php endforeach; ?>
			</div>

			<!-- Theme Content Blocks -->
			<div class="theme-content-container">
				<?php foreach ( $theme_tags as $index => $theme_tag ) : 
					$display_style = $index === 0 ? 'block' : 'none';
				?>
					<div class="theme-tag-block" id="theme-block-<?php echo esc_attr( $theme_tag['slug'] ); ?>" style="display: <?php echo $display_style; ?>;">
						<div class="article-grid">
							<?php
							$tag_args = array(
								'tag'            => $theme_tag['slug'],
								'posts_per_page' => 3, // Changed to 3 to match other grids
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
						<div style="text-align: right; margin-top: 24px;">
							<a href="<?php echo esc_url( get_tag_link( get_term_by( 'slug', $theme_tag['slug'], 'post_tag' ) ) ); ?>" class="text-link-arrow">
								<?php echo esc_html( $theme_tag['name'] ); ?> <?php esc_html_e( 'の記事一覧', 'logishift' ); ?> →
							</a>
						</div>
					</div>
				<?php endforeach; ?>
			</div>
		</div>
	</section>

</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
	// 1. Global Trends Filter (Existing Logic)
	const regionTabs = document.querySelectorAll('.global-trends-section .region-tab');
	const globalArticles = document.querySelectorAll('.global-article');
	const showMoreLink = document.querySelector('.global-show-more-link');
	
	function filterArticles(selectedRegion) {
		let visibleCount = 0;
		const isMobile = window.matchMedia("(max-width: 768px)").matches;
		const limit = isMobile ? 3 : 999; 

		globalArticles.forEach(article => {
			const articleRegions = article.getAttribute('data-regions');
			const shouldShow = (selectedRegion === 'all' || articleRegions.includes(selectedRegion));

			if (shouldShow) {
				if (visibleCount < limit) {
					article.style.display = ''; 
					visibleCount++;
				} else {
					article.style.display = 'none';
				}
			} else {
				article.style.display = 'none';
			}
		});

		if (showMoreLink) {
			const activeTab = document.querySelector('.global-trends-section .region-tab[data-region="' + selectedRegion + '"]');
			if (activeTab && activeTab.dataset.url) {
				showMoreLink.href = activeTab.dataset.url;
				showMoreLink.style.display = 'inline-block';
			}
		}
	}

	regionTabs.forEach(tab => {
		tab.addEventListener('click', function() {
			const selectedRegion = this.getAttribute('data-region');
			regionTabs.forEach(t => t.classList.remove('active'));
			this.classList.add('active');
			filterArticles(selectedRegion);
		});
	});

	filterArticles('all');

	window.addEventListener('resize', function() {
		const activeTab = document.querySelector('.global-trends-section .region-tab.active');
		const selectedRegion = activeTab ? activeTab.getAttribute('data-region') : 'all';
		filterArticles(selectedRegion);
	});

	// 2. Theme Tabs Logic (New)
	const themeTabs = document.querySelectorAll('.theme-tabs .region-tab');
	const themeBlocks = document.querySelectorAll('.theme-tag-block');

	themeTabs.forEach(tab => {
		tab.addEventListener('click', function() {
			const selectedTheme = this.getAttribute('data-theme');

			// Switch Tabs
			themeTabs.forEach(t => t.classList.remove('active'));
			this.classList.add('active');

			// Switch Content
			themeBlocks.forEach(block => {
				if (block.id === 'theme-block-' + selectedTheme) {
					block.style.display = 'block';
				} else {
					block.style.display = 'none';
				}
			});
		});
	});
	// 3. Industry Tabs Logic (New)
	const industryTabs = document.querySelectorAll('.industry-tabs .region-tab');
	const industryBlocks = document.querySelectorAll('.industry-tag-block');

	industryTabs.forEach(tab => {
		tab.addEventListener('click', function() {
			const selectedIndustry = this.getAttribute('data-industry');

			// Switch Tabs
			industryTabs.forEach(t => t.classList.remove('active'));
			this.classList.add('active');

			// Switch Content
			industryBlocks.forEach(block => {
				if (block.id === 'industry-block-' + selectedIndustry) {
					block.style.display = 'block';
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
