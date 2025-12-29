<?php
/**
 * View tracking and retrieval logic for Popular Articles
 *
 * @package LogiShift
 */

/**
 * Create the daily views table if it doesn't exist.
 */
function logishift_create_view_table() {
    global $wpdb;
    $table_name = $wpdb->prefix . 'logishift_daily_views';
    $charset_collate = $wpdb->get_charset_collate();

    $sql = "CREATE TABLE $table_name (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        post_id bigint(20) NOT NULL,
        view_date date NOT NULL,
        count bigint(20) NOT NULL DEFAULT 1,
        PRIMARY KEY  (id),
        UNIQUE KEY post_date (post_id, view_date)
    ) $charset_collate;";

    require_once( ABSPATH . 'wp-admin/includes/upgrade.php' );
    dbDelta( $sql );
    
    update_option( 'logishift_view_table_version', '1.0.0' );
}

/**
 * Track post view.
 */
function logishift_track_post_view() {
    if ( ! is_single() ) {
        return;
    }

    global $post, $wpdb;

    // Optional: We can exclude admins here if requested, but for now we track everyone so user can verify it works
    // if ( current_user_can( 'manage_options' ) ) return;

    $post_id = $post->ID;
    $date = current_time( 'Y-m-d' );
    $table_name = $wpdb->prefix . 'logishift_daily_views';

    // Insert or Update count
    // Using simple query since dbDelta created the table
    $query = $wpdb->prepare(
        "INSERT INTO $table_name (post_id, view_date, count) VALUES (%d, %s, 1)
        ON DUPLICATE KEY UPDATE count = count + 1",
        $post_id,
        $date
    );

    $wpdb->query( $query );
}
add_action( 'wp_head', 'logishift_track_post_view' );

/**
 * Get popular posts by view count.
 *
 * @param int $days Number of days to look back.
 * @param int $limit Number of posts to return.
 * @return array List of WP_Post objects with 'views' property.
 */
function logishift_get_popular_posts( $days = 7, $limit = 5, $term_id = null, $taxonomy = 'category' ) {
    global $wpdb;
    $table_name = $wpdb->prefix . 'logishift_daily_views';
    
    // Check if table exists (to avoid errors if called before init)
    if ( $wpdb->get_var( "SHOW TABLES LIKE '$table_name'" ) != $table_name ) {
        return array();
    }

    // Calculate start date
    $start_date = date( 'Y-m-d', strtotime( "-$days days" ) );

    // Build Query
    $sql = "SELECT v.post_id, SUM(v.count) as views FROM $table_name v";
    $join = "";
    $where = "WHERE v.view_date >= %s";
    $args = array( $start_date );

    // Add Taxonomy Filtering
    if ( $term_id ) {
        $join .= " LEFT JOIN {$wpdb->term_relationships} tr ON v.post_id = tr.object_id";
        $join .= " LEFT JOIN {$wpdb->term_taxonomy} tt ON tr.term_taxonomy_id = tt.term_taxonomy_id";
        
        $where .= " AND tt.term_id = %d AND tt.taxonomy = %s";
        $args[] = $term_id;
        $args[] = $taxonomy;
    }

    $sql .= $join . " " . $where . " GROUP BY v.post_id ORDER BY views DESC LIMIT %d";
    $args[] = $limit;

    $query = $wpdb->prepare( $sql, $args );

    $results = $wpdb->get_results( $query );

    if ( ! $results ) {
        return array();
    }

    $posts = array();
    foreach ( $results as $row ) {
        $post = get_post( $row->post_id );
        if ( $post ) {
            $post->views = $row->views;
            $posts[] = $post;
        }
    }

    return $posts;
}

/**
 * Helper to get total views for a specific post within the last N days.
 *
 * @param int $post_id Post ID.
 * @param int $days Number of days to look back.
 * @return int Total views.
 */
function logishift_get_post_views( $post_id, $days = 7 ) {
    global $wpdb;
    $table_name = $wpdb->prefix . 'logishift_daily_views';
    
    // Check if table exists
    if ( $wpdb->get_var( "SHOW TABLES LIKE '$table_name'" ) != $table_name ) {
        return 0;
    }

    $start_date = date( 'Y-m-d', strtotime( "-$days days" ) );

    $sql = "SELECT SUM(count) FROM $table_name WHERE post_id = %d AND view_date >= %s";
    $views = $wpdb->get_var( $wpdb->prepare( $sql, $post_id, $start_date ) );

    return $views ? (int) $views : 0;
}

/**
 * Add PV column to Admin Post List
 */
function logishift_manage_posts_columns( $columns ) {
    $columns['logishift_pv'] = __( '週間PV', 'logishift' );
    return $columns;
}
add_filter( 'manage_posts_columns', 'logishift_manage_posts_columns' );

/**
 * Render PV column content
 */
function logishift_manage_posts_custom_column( $column, $post_id ) {
    if ( 'logishift_pv' === $column ) {
        $views = logishift_get_post_views( $post_id, 7 );
        echo number_format( $views );
    }
}
add_action( 'manage_posts_custom_column', 'logishift_manage_posts_custom_column', 10, 2 );

/**
 * Style the PV column
 */
function logishift_admin_column_styling() {
    echo '<style>
        .column-logishift_pv { width: 80px; text-align: right; }
    </style>';
}
add_action( 'admin_head', 'logishift_admin_column_styling' );
