<?php
/**
 * Custom search form
 *
 * @package LogiShift
 */
?>
<form role="search" method="get" class="search-form" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<label>
		<span class="screen-reader-text"><?php echo _x( 'Search for:', 'label', 'logishift' ); ?></span>
		<input type="search" class="search-field" placeholder="<?php echo esc_attr_x( 'Search...', 'placeholder', 'logishift' ); ?>" value="<?php echo get_search_query(); ?>" name="s" />
	</label>
	<button type="submit" class="search-submit button primary"><?php echo _x( 'Search', 'submit button', 'logishift' ); ?></button>
</form>
