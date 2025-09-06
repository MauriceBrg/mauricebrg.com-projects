resource "aws_cloudfront_response_headers_policy" "production_static_response_headers" {
  name = "${local.app_name}-production-response-headers"

  # Empty for demo purposes
  custom_headers_config {
    items {
      header   = "Cache-Control"
      override = false
      value    = "max-age=10"
    }

    items {
      header   = "Environment"
      override = false
      value    = "Production"
    }
  }
}

resource "aws_cloudfront_response_headers_policy" "staging_static_response_headers" {
  name = "${local.app_name}-staging-response-headers"

  # Empty for demo purposes
  custom_headers_config {
    items {
      header   = "Cache-Control"
      override = false
      value    = "max-age=10"
    }

    items {
      header   = "Environment"
      override = false
      value    = "Staging"
    }
  }
}

resource "aws_cloudfront_cache_policy" "static_cache_policy" {
  name        = "${local.app_name}-caching"
  default_ttl = 0
  max_ttl     = 31536000
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {

    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "none"
    }

    query_strings_config {
      query_string_behavior = "none"
    }

    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

resource "aws_cloudfront_origin_access_control" "oac" {

  name                              = "${local.app_name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "production_distribution" {

  origin {
    domain_name              = aws_s3_bucket.static.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
    origin_id                = "static"
  }

  enabled             = true
  is_ipv6_enabled     = true
  http_version        = "http2" # HTTP 3 is not supported for Continuous Deployments.
  default_root_object = "index.html"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "static"
    viewer_protocol_policy = "redirect-to-https"
    cache_policy_id        = aws_cloudfront_cache_policy.static_cache_policy.id

    compress = true

    response_headers_policy_id = aws_cloudfront_response_headers_policy.production_static_response_headers.id
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  comment = "${local.app_name}-production"

  tags = {
    Name = "${local.app_name}-production"
  }

  # NOTE: A continuous deployment policy cannot be associated to distribution
  # on creation. Set this argument once the resource exists.
  continuous_deployment_policy_id = aws_cloudfront_continuous_deployment_policy.weighted.id

  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
  }
}


resource "aws_cloudfront_continuous_deployment_policy" "weighted" {
  enabled = true

  staging_distribution_dns_names {
    items    = [aws_cloudfront_distribution.staging_distribution.domain_name]
    quantity = 1
  }

  traffic_config {
    type = "SingleWeight"
    single_weight_config {
      weight = "0.15"

      # For tests with sticky sessions.
      # If enabled, we need to wait at least 5 mins between test runs!
      # Enabling them did NOT meaningfully change the metrics!
      # session_stickiness_config {
      #   idle_ttl    = 300
      #   maximum_ttl = 300
      # }
    }


  }
}

resource "aws_cloudfront_distribution" "staging_distribution" {

  origin {
    domain_name              = aws_s3_bucket.static.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
    origin_id                = "static"
  }

  enabled             = true
  is_ipv6_enabled     = true
  http_version        = "http2" # HTTP 3 is not supported for Continuous Deployments.
  default_root_object = "index.html"

  staging = true

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "static"
    viewer_protocol_policy = "redirect-to-https"
    cache_policy_id        = aws_cloudfront_cache_policy.static_cache_policy.id

    compress = true

    response_headers_policy_id = aws_cloudfront_response_headers_policy.staging_static_response_headers.id
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  comment = "${local.app_name}-staging"

  tags = {
    Name = "${local.app_name}-staging"
  }

  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
  }
}