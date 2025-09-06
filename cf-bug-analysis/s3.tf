# S3 Bucket and CloudFront permissions

resource "aws_s3_bucket" "static" {
  bucket_prefix = "static-content-${local.app_name}-"

  force_destroy = true
}

data "aws_iam_policy_document" "static" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.static.arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values = [
        aws_cloudfront_distribution.production_distribution.arn,
        aws_cloudfront_distribution.staging_distribution.arn
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "static" {
  bucket = aws_s3_bucket.static.id

  policy = data.aws_iam_policy_document.static.json
}

# Synching static files to S3

module "static_files" {
  source = "hashicorp/dir/template"

  version = "1.0.2"

  base_dir = "${path.module}/static"
}

resource "aws_s3_object" "static_files" {
  for_each = module.static_files.files

  bucket       = aws_s3_bucket.static.bucket
  key          = each.key
  content_type = each.value.content_type

  source  = each.value.source_path
  content = each.value.content

  source_hash = each.value.digests.base64sha256

}