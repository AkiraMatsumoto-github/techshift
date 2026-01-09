<?php
/**
 * The template for displaying the footer
 *
 * @package FinShift
 */
?>

	<footer id="colophon" class="site-footer">
		<div class="container">
			<div class="footer-content">
				<!-- Footer Columns -->
				<div class="footer-columns">
					<!-- About Column -->
					<div class="footer-column">
						<h3 class="footer-title">FinShift</h3>
						<p class="footer-description">世界主要市場（US, JP, India, China）と重要資産（Crypto, Commodity）の「今」を読み解くマーケット・インテリジェンス・メディア。データとAIシナリオで、スイングトレーダーの意思決定を支援します。</p>
					</div>

					<!-- Markets Column -->
					<div class="footer-column">
						<h3 class="footer-title">Markets</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/category/featured-news/' ) ); ?>">Featured News</a></li>
							<li><a href="<?php echo esc_url( home_url( '/us/' ) ); ?>">US Market</a></li>
							<li><a href="<?php echo esc_url( home_url( '/japan/' ) ); ?>">Japan Market</a></li>
							<li><a href="<?php echo esc_url( home_url( '/china/' ) ); ?>">China Market</a></li>
							<li><a href="<?php echo esc_url( home_url( '/india/' ) ); ?>">India Market</a></li>
							<li><a href="<?php echo esc_url( home_url( '/indonesia/' ) ); ?>">Indonesia Market</a></li>
						</ul>
					</div>

					<!-- Assets Column -->
					<div class="footer-column">
						<h3 class="footer-title">Assets & Guide</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/crypto/' ) ); ?>">Crypto</a></li>
							<li><a href="<?php echo esc_url( home_url( '/tag/commodity/' ) ); ?>">Commodities</a></li>
							<li><a href="<?php echo esc_url( home_url( '/category/investment-guide/' ) ); ?>">Investment Guide</a></li>
						</ul>
					</div>

					<!-- Info Column -->
					<div class="footer-column">
						<h3 class="footer-title">Information</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/about/' ) ); ?>">About Us</a></li>
							<li><a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">Contact</a></li>
							<li><a href="<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>">Privacy Policy</a></li>
							<li><a href="https://logishift.net/" target="_blank" rel="noopener">Logishift</a></li>
						</ul>
					</div>
				</div>

				<!-- Footer Bottom -->
				<div class="footer-bottom">
					<p class="copyright">&copy; <?php echo date( 'Y' ); ?> FinShift. All rights reserved.</p>
				</div>
			</div>
		</div>
	</footer>

<?php wp_footer(); ?>

</body>
</html>
