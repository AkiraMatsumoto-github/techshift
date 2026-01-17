<?php
/**
 * Register Article Meta Fields for Rest API
 *
 * @package FinShift
 */

function finshift_register_post_meta_rest_fields() {
    // 1. AI Structured Summary
    register_post_meta( 'post', '_ai_structured_summary', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'string',
        'auth_callback' => '__return_true'
    ) );

    // 2. Sentiment Score
    register_post_meta( 'post', '_finshift_sentiment', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'number',
        'auth_callback' => '__return_true'
    ) );

    // 3. Market Regime
    register_post_meta( 'post', '_finshift_regime', array(
        'show_in_rest' => true,
        'single'       => true,
        'type'         => 'string',
        'auth_callback' => '__return_true'
    ) );

    // 4. Article Scenarios (Bull/Bear)
    $scenario_keys = [
        '_finshift_scenario_main',
        '_finshift_scenario_bull',
        '_finshift_scenario_bear'
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
add_action( 'init', 'finshift_register_post_meta_rest_fields' );
