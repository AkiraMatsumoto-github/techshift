<?php
/**
 * The template for displaying the footer
 *
 * @package LogiShift
 */
?>

	<footer id="colophon" class="site-footer">
		<div class="container">
			<div class="footer-content">
				<!-- Footer Columns -->
				<div class="footer-columns">
					<!-- About Column -->
					<div class="footer-column">
						<h3 class="footer-title">LogiShift</h3>
						<p class="footer-description">物流担当者と経営層のための課題解決メディア。現場のノウハウから最新のDX事例まで、ビジネスを加速させる情報をお届けします。</p>
					</div>

					<!-- Categories Column -->
					<div class="footer-column">
						<h3 class="footer-title">カテゴリー</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/?cat=11' ) ); ?>">物流DX・トレンド</a></li>
							<li><a href="<?php echo esc_url( home_url( '/?cat=12' ) ); ?>">倉庫管理・WMS</a></li>
							<li><a href="<?php echo esc_url( home_url( '/?cat=13' ) ); ?>">輸配送・TMS</a></li>
							<li><a href="<?php echo esc_url( home_url( '/?cat=14' ) ); ?>">マテハン・ロボット</a></li>
						</ul>
					</div>

					<!-- More Categories Column -->
					<div class="footer-column">
						<h3 class="footer-title">もっと探す</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/?cat=15' ) ); ?>">サプライチェーン</a></li>
							<li><a href="<?php echo esc_url( home_url( '/?cat=17' ) ); ?>">海外トレンド</a></li>
							<li><a href="<?php echo esc_url( home_url( '/?cat=16' ) ); ?>">事例</a></li>
						</ul>
					</div>

					<!-- Info Column -->
					<div class="footer-column">
						<h3 class="footer-title">サイト情報</h3>
						<ul class="footer-links">
							<li><a href="<?php echo esc_url( home_url( '/about/' ) ); ?>">運営者情報</a></li>
							<li><a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">お問い合わせ</a></li>
							<li><a href="<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>">プライバシーポリシー</a></li>
							<li><a href="https://en.logishift.net/">LogiShift Global</a></li>
						</ul>
					</div>
				</div>

				<!-- Footer Bottom -->
				<div class="footer-bottom">
					<p class="copyright">&copy; <?php echo date( 'Y' ); ?> LogiShift. All rights reserved.</p>
				</div>
			</div>
		</div>
	</footer>

<?php wp_footer(); ?>

</body>
</html>
