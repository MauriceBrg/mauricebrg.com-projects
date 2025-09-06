output "cloudfront_domain" {
  value = aws_cloudfront_distribution.production_distribution.domain_name
}