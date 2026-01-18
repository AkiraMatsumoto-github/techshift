<?php
/**
 * The template for displaying the footer
 *
 * @package TechShift
 */
?>

	<footer id="colophon" class="site-footer">
		<div class="container">
			<div class="footer-content">
				<!-- Footer Columns -->
				<div class="footer-columns">
					<!-- About Column -->
					<div class="footer-column">
						<h3 class="footer-title">TechShift</h3>
						<p class="footer-description">未来を実装する実務者のためのテクノロジー・ロードマップ。AI、量子技術、宇宙開発などの最先端分野における技術革新と、それが社会に与えるインパクトを可視化します。</p>
					</div>

					<!-- Navigation Column -->
					<div class="footer-column">
						<h3 class="footer-title">Navigation</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/category/summary/' ) ); ?>">日次・週次まとめ</a></li>
							<li><a href="<?php echo esc_url( home_url( '/category/multi-agent-systems/' ) ); ?>">マルチエージェント</a></li>
							<li><a href="<?php echo esc_url( home_url( '/category/post-quantum-cryptography/' ) ); ?>">耐量子暗号 (PQC)</a></li>
							<li><a href="<?php echo esc_url( home_url( '/category/solid-state-batteries/' ) ); ?>">全固体電池</a></li>
							<li><a href="<?php echo esc_url( home_url( '/category/autonomous-driving/' ) ); ?>">自動運転</a></li>
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
					<p class="copyright">&copy; <?php echo date( 'Y' ); ?> TechShift. All rights reserved.</p>
				</div>
			</div>
		</div>
	</footer>

<?php wp_footer(); ?>

</body>
</html>
