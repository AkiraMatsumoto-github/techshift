<?php
/**
 * The template for displaying the footer
 *
 * @package LogiShift
 */
?>

	<footer id="colophon" class="site-footer">
		<div class="container">
			<div class="site-info">
				<nav class="footer-navigation">
					<?php
					wp_nav_menu(
						array(
							'theme_location' => 'footer',
							'menu_id'        => 'footer-menu',
							'depth'          => 1,
						)
					);
					?>
				</nav>
				<div class="copyright">
					&copy; <?php echo date( 'Y' ); ?> <a href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php bloginfo( 'name' ); ?></a>
				</div>
			</div><!-- .site-info -->
		</div>
	</footer><!-- #colophon -->
</div><!-- #page -->

<?php wp_footer(); ?>

</body>
</html>
