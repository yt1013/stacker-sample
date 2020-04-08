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
        'AssetsBucketName': {
            'type': str
        }
    }

    def create_template(self):
        var = self.get_variables()
        project_id = var.get('ProjectId')
        environment = var.get('Environment')
        assets_bucket_name = var.get('AssetsBucketName')

        self.template.description = 'S3 Bucket Stack'

        # Front S3 Bucket
        assets_bucket = self.template.add_resource(
            s3.Bucket(
                'AssetsBucket', #primary name
                BucketName=Join('-', [assets_bucket_name, Ref(AWS_ACCOUNT_ID)]),
                DeletionPolicy=Retain
            )
        )
        self.template.add_output(Output('AssetsBucketName', Ref(assets_bucket)))