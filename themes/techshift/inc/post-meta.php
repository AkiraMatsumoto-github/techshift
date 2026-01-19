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

    // 4. TechShift Analysis Detail (Catalyst, Next Wall, Signal)
    $analysis_keys = [
        '_techshift_catalyst',
        '_techshift_next_wall',
        '_techshift_signal'
    ];

    foreach ( $analysis_keys as $key ) {
        register_post_meta( 'post', $key, array(
            'show_in_rest' => true,
            'single'       => true,
            'type'         => 'string',
            'auth_callback' => '__return_true'
        ) );
    }
}
add_action( 'init', 'techshift_register_post_meta_rest_fields' );
