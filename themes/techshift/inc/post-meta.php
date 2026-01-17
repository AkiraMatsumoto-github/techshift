<?php
/**
 * Register Article Meta Fields for Rest API
 *
 * @package TechShift
 */

function techshift_register_post_meta_rest_fields() {
    // 1. AI Structured Summary
    register_post_meta( 'post', '_ai_structured_summary', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'string',
        'auth_callback' => '__return_true'
    ) );

    // 2. Timeline Impact (formerly Sentiment)
    register_post_meta( 'post', '_techshift_impact', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'number',
        'auth_callback' => '__return_true'
    ) );

    // 3. Evolution Phase (formerly Regime)
    register_post_meta( 'post', '_techshift_phase', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'string',
        'auth_callback' => '__return_true'
    ) );

    // 4. Article Scenarios (Main/Bull/Bear)
    $scenario_keys = [
        '_techshift_scenario_main',
        '_techshift_scenario_bull',
        '_techshift_scenario_bear'
    ];

    foreach ( $scenario_keys as $key ) {
        register_post_meta( 'post', $key, array(
            'show_in_rest' => true,
            'single'       => true,
            'type'         => 'string',
            'auth_callback' => function() { return current_user_can( 'edit_posts' ); } // stricter auth for scenarios
        ) );
    }
}
add_action( 'init', 'techshift_register_post_meta_rest_fields' );
