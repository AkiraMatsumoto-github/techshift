<?php
/**
 * Custom search form
 *
 * @package TechShift
 */
?>
<form role="search" method="get" class="search-form" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<span class="screen-reader-text"><?php echo _x( 'Search for:', 'label', 'techshift' ); ?></span>
	<input type="search" class="search-field" placeholder="<?php echo esc_attr_x( 'Search...', 'placeholder', 'techshift' ); ?>" value="<?php echo get_search_query(); ?>" name="s" />
	<button type="submit" class="search-submit button primary"><?php echo _x( 'Search', 'submit button', 'techshift' ); ?></button>
</form>
