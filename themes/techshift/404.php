<?php
/**
 * The template for displaying 404 pages (not found)
 *
 * @package FinShift
 */

get_header();
?>

<main id="primary" class="site-main">
	<div class="container">
		
		<div class="error-404 not-found" style="text-align: center; padding: var(--spacing-3xl) 0;">
			<header class="page-header">
				<h1 class="page-title" style="font-size: 6rem; color: var(--color-tech-blue); margin-bottom: var(--spacing-md);">404</h1>
				<h2 class="page-subtitle" style="font-size: 1.5rem; margin-bottom: var(--spacing-xl);"><?php esc_html_e( 'お探しのページは見つかりませんでした。', 'finshift' ); ?></h2>
			</header>

			<div class="page-content" style="max-width: 600px; margin: 0 auto;">
				<p style="margin-bottom: var(--spacing-xl);"><?php esc_html_e( '申し訳ありませんが、お探しのページは削除されたか、URLが変更された可能性があります。検索をお試しいただくか、トップページへお戻りください。', 'finshift' ); ?></p>

				<div style="margin-bottom: var(--spacing-2xl);">
					<?php get_search_form(); ?>
				</div>

				<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="button primary"><?php esc_html_e( 'トップページへ戻る', 'finshift' ); ?></a>
			</div>
		</div>

	</div>
</main>

<?php
get_footer();
