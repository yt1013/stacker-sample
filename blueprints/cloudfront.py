import troposphere_mate.cloudfront as cf
from stacker.blueprints.base import Blueprint
from troposphere_mate import s3, Retain, Ref, AWS_REGION, Join, AWS_STACK_NAME, GetAtt


class CloudFront(Blueprint):
    VARIABLES = {
        'ProjectId': {
            'type': str
        },
        'Environment': {
            'type': str
        },
        'FrontBucketName':{
            'type': str
        },
        'WeatherBucketName': {
            'type': str
        },
        'LaravelAssetsBucketName': {
            'type': str
        }
    }

    @property
    def front_bucket_name(self):
        return self.get_variables()['FrontBucketName']
    @property
    def weather_bucket_name(self):
        return self.get_variables()['WeatherBucketName']
    @property
    def larvel_assets_bucket_name(self):
        return self.get_variables()['LaravelAssetsBucketName']

    def create_s3_oai(self) -> cf.CloudFrontOriginAccessIdentity:
        return self.template.add_resource(
            cf.CloudFrontOriginAccessIdentity(
                'FrontS3OAI',
                CloudFrontOriginAccessIdentityConfig=cf.CloudFrontOriginAccessIdentityConfig(
                    Comment=Ref(AWS_STACK_NAME)
                ),
            )
        )

    def create_s3_bucket_policy(self, bucket_key, bucket_name, oai: cf.CloudFrontOriginAccessIdentity):
        self.template.add_resource(
            s3.BucketPolicy(
                f'{bucket_key}S3CfPolicy',
                Bucket=bucket_name,
                PolicyDocument={
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Action': 's3:GetObject',
                            'Resource': f'arn:aws:s3:::{bucket_name}/*',
                            'Principal': {
                                'CanonicalUser': GetAtt(oai, 'S3CanonicalUserId')
                            }
                        }
                    ]
                }
            )
        )

    def create_cloudfront_s3_origin(self, bucket_name, oai: cf.CloudFrontOriginAccessIdentity) -> cf.Origin:
        return cf.Origin(
            Id=f'S3Origin-{bucket_name}',
            DomainName=Join('', [f'{bucket_name}.s3-', Ref(AWS_REGION), '.amazonaws.com']),
            S3OriginConfig=cf.S3OriginConfig(
                OriginAccessIdentity=Join('', ['origin-access-identity/cloudfront/', Ref(oai)])
            )
        )

    def create_default_cache_behavior(self, bucket_name) -> cf.DefaultCacheBehavior:
        return cf.DefaultCacheBehavior(
            TargetOriginId=f'S3Origin-{bucket_name}',
            ViewerProtocolPolicy='redirect-to-https',
            ForwardedValues=cf.ForwardedValues(
                QueryString=False
            ),
        )
    def create_cache_behavior(self, bucket_name, path) -> cf.CacheBehavior:
        return cf.CacheBehavior(
            TargetOriginId=f'S3Origin-{bucket_name}',
            ViewerProtocolPolicy='redirect-to-https',
            PathPattern=path,
            ForwardedValues=cf.ForwardedValues(
                QueryString=False
            ),
        )

    def create_cloudfront_distribution(self, s3_origin, default_cache_behavior: cf.DefaultCacheBehavior, cache_behavior):
        self.template.add_resource(
            cf.Distribution(
                'CloudFrontDistribution',
                DistributionConfig=cf.DistributionConfig(
                    Enabled=True,
                    DefaultRootObject='index.html',
                    Origins=s3_origin,
                    DefaultCacheBehavior=default_cache_behavior,
                    CacheBehaviors=cache_behavior,
                )
            )
        )

    def create_template(self):
        self.template.description = 'CloudFront Stack'

        bucket_names = {
            'Front': self.front_bucket_name,
            'Weather': self.weather_bucket_name,
            'Assets': self.larvel_assets_bucket_name
        }

        s3_origin = []
        cache_behavior = []

        front_s3_oai = self.create_s3_oai()
        for bucket_key, bucket_name in bucket_names.items():
            self.create_s3_bucket_policy(bucket_key, bucket_name, front_s3_oai)
            s3_origin.append(self.create_cloudfront_s3_origin(bucket_name, front_s3_oai))
        default_cache_behavior = self.create_default_cache_behavior(self.front_bucket_name)
        cache_behavior.append(self.create_cache_behavior(self.weather_bucket_name, '/weather/*'))
        cache_behavior.append(self.create_cache_behavior(self.larvel_assets_bucket_name, '/laravel-assets/*'))
        self.create_cloudfront_distribution(s3_origin, default_cache_behavior, cache_behavior)