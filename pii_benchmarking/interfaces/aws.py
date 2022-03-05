import os
import json
import boto3

from pii_benchmarking import utils


class Masker:

    def __init__(self):
        try:
            aws_access_key_id = os.environ['aws_access_key_id']
            aws_secret_access_key = os.environ['aws_secret_access_key']
        except KeyError as e:
            print('AWS access key and secret key not found in environment.')
            raise e

        self.masker = boto3.client('comprehend',
                                   region_name='us-west-2',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

        self.s3_client = boto3.client('s3',
                                      region_name='us-west-2',
                                      aws_access_key_id=aws_access_key_id,
                                      aws_secret_access_key=aws_secret_access_key)
        self.bucket_name = 'lp-pii'
        self.input_key = 'pii_input'
        self.iam_arn = '350151172143'

    def mask_text(self, text):
        result = self.masker.detect_pii_entities(Text=text, LanguageCode='en')
        return self._standardize_result(text, result)

    def batch_mask(self, list_of_text, cleanup=True):
        self._upload_data(list_of_text, self.input_key)
        job_id = self._run_job()
        output_key = self.iam_arn + '-PII-' + job_id + '/output/' + self.input_key + '.out'
        result = self._retrieve_data(list_of_text, output_key)

        if cleanup:
            self._remove_data([self.input_key, output_key])

        return result

    def _upload_data(self, list_of_text, input_key):
        text = '\n'.join(list_of_text)
        text_encoded = text.encode('utf-8')
        response = self.s3_client.put_object(Body=text_encoded,
                                             Bucket=self.bucket_name,
                                             Key=input_key)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise ValueError('Upload text to aws s3 bucket failed.')  # TODO: get some custom exceptions classes

    def _run_job(self):
        input_uri = self._get_uri(self.input_key)
        output_uri = self._get_uri()
        response = self.masker.start_pii_entities_detection_job(InputDataConfig={'S3Uri': input_uri,
                                                                                 'InputFormat': 'ONE_DOC_PER_LINE'
                                                                                 },
                                                                OutputDataConfig={'S3Uri': output_uri},
                                                                Mode='ONLY_OFFSETS',
                                                                DataAccessRoleArn=f'arn:aws:iam::{self.iam_arn}:role/comprehendTopicModel',
                                                                LanguageCode='en')

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise ValueError('Upload text to aws s3 bucket failed.')

        job_id = response['JobId']
        print(f'Polling aws with job id: {job_id}')
        utils.poll_api('COMPLETED', self._get_polling_status, job_id)
        return job_id

    def _get_polling_status(self, job_id):  # set this up to return status of the job
        status = self.masker.describe_pii_entities_detection_job(JobId=job_id)
        return status['PiiEntitiesDetectionJobProperties']['JobStatus']

    def _retrieve_data(self, list_of_text, output_key):
        result = self.s3_client.get_object(Bucket=self.bucket_name,
                                           Key=output_key)
        processed_result = result['Body'].read().decode()
        processed_result = processed_result.split('\n')[:-1]  # Remove trailing newline
        processed_result = [json.loads(x) for x in processed_result]
        return [self._standardize_result(x, y) for x, y in list(zip(list_of_text, processed_result))]

    def _remove_data(self, key_list):
        for key in key_list:
            response = self.s3_client.delete_object(Bucket=self.bucket_name,
                                                    Key=key)
            https_status = response['ResponseMetadata']['HTTPStatusCode']
            if https_status != 204:
                print(f'Clean up aws s3 bucket failed: code {https_status}')

    def _get_uri(self, key=''):
        return 's3://' + self.bucket_name + '/' + key

    @staticmethod
    def _standardize_result(text, result):
        key_map = {'Type': 'entity_label', 'BeginOffset': 'start_char', 'EndOffset': 'end_char', 'Score': 'score'}
        entities = list()
        for r in result['Entities']:
            r = {key_map[k]: v for (k, v) in r.items() if k in key_map.keys()}
            r = utils.standardized_person_ent(r)
            entities.append(r)
        return utils.get_standardized_result('aws', text, entities)

# input_uri = f's3://lp-pii/{input_key}'
# output_uri = 's3://lp-pii/'
# response = masker.start_pii_entities_detection_job(InputDataConfig={'S3Uri': input_uri, 'InputFormat': 'ONE_DOC_PER_LINE'}, OutputDataConfig={'S3Uri': output_uri}, Mode='ONLY_OFFSETS', DataAccessRoleArn=f'arn:aws:iam::{iam_arn}:role/comprehendTopicModel', LanguageCode='en')
