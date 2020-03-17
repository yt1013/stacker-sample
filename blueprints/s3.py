from stacker.blueprints.base import Blueprint
from troposphere_mate import s3, Retain, Output, Ref, AWS_ACCOUNT_ID, Join


class S3(Blueprint):
    VARIABLES = {
        'ProjectId': {
            'type': str
        },
        'Environment': {
            'type': str
        },
        'FrontBucketName': {
            'type': str
        }
    }

    def create_template(self):
        var = self.get_variables()
        project_id = var.get('ProjectId')
        environment = var.get('Environment')
        front_bucket_name = var.get('FrontBucketName')

        self.template.description = 'S3 Bucket Stack'

        # Front S3 Bucket
        front_bucket = self.template.add_resource(
            s3.Bucket(
                'FrontBucket',
                BucketName=Join('-', [front_bucket_name, Ref(AWS_ACCOUNT_ID)]),
            )
        )
        sample2_bucket = self.template.add_resource(
            s3.Bucket(
                'WeatherBucket',
                BucketName=Join('-', ['sample2', Ref(AWS_ACCOUNT_ID)]),
            )
        )
        sample3_bucket = self.template.add_resource(
            s3.Bucket(
                'LaravelAssetsBucket',
                BucketName=Join('-', ['sample3', Ref(AWS_ACCOUNT_ID)]),
            )
        )
        sample4_bucket = self.template.add_resource(
            s3.Bucket(
                'FromKajimaBucket',
                BucketName=Join('-', ['sample4', Ref(AWS_ACCOUNT_ID)]),
            )
        )
        self.template.add_output(Output('FrontBucketName', Ref(front_bucket)))
        self.template.add_output(Output('WeatherBucketName', Ref(sample2_bucket)))
        self.template.add_output(Output('LaravelAssetsBucketName', Ref(sample3_bucket)))
        self.template.add_output(Output('FromKajimaBucketName', Ref(sample4_bucket)))