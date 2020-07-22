# Copyright 2019 Atalaya Tech, Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from urllib.parse import urlparse

from google.cloud import storage

from bentoml import config
from bentoml.exceptions import YataiRepositoryException
from bentoml.yatai.proto.repository_pb2 import BentoUri
from bentoml.yatai.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class GCSRepository(BaseRepository):
    def __init__(self, base_url, s3_endpoint_url=None):
        self.uri_type = BentoUri.GCS

        parse_result = urlparse(base_url)
        self.bucket = parse_result.netloc
        self.base_path = parse_result.path.lstrip('/')
        # gcs_client_args = {}
        # signature_version = config('yatai_service').get('GCS_SIGNATURE_VERSION')
        # gcs_client_args['config'] = boto3.session.Config(
        #     signature_version=signature_version
        # )
        # if s3_endpoint_url is not None:
        #     gcs_client_args['endpoint_url'] = s3_endpoint_url
        self.gcs_client = storage.Client()

    @property
    def _expiration(self):
        return config('yatai').getint('bento_uri_default_expiration')

    def _get_object_name(self, bento_name, bento_version):
        if self.base_path:
            return "/".join([self.base_path, bento_name, bento_version]) + '.tar.gz'
        else:
            return "/".join([bento_name, bento_version]) + '.tar.gz'

    def add(self, bento_name, bento_version):
        object_name = self._get_object_name(bento_name, bento_version)
        try:
            bucket = self.gcs_client.bucket(self.bucket)
            blob = bucket.blob(object_name)
            # TODO: Fix this
            # blob.upload_from_filename(source_file_name)
            # response = self.gcs_client.generate_presigned_url(
            #     'put_object',
            #     Params={'Bucket': self.bucket, 'Key': object_name},
            #     ExpiresIn=self._expiration,
            # )
        except Exception as e:
            raise YataiRepositoryException(
                "Not able to get pre-signed URL on GCS. Error: {}".format(e)
            )

        return BentoUri(
            type=self.uri_type,
            uri='gcs://{}/{}'.format(self.bucket, object_name),
            gcs_presigned_url=response,
        )

    def get(self, bento_name, bento_version):
        # Return gcs path containing uploaded Bento files

        object_name = self._get_object_name(bento_name, bento_version)

        try:
            response = self.gcs_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=self._expiration,
            )
            return response
        except Exception:  # pylint: disable=broad-except
            logger.error(
                "Failed generating presigned URL for downloading saved bundle from gcs,"
                "falling back to using gcs path and client side credential for"
                "downloading with boto3"
            )
            return 'gcs://{}/{}'.format(self.bucket, object_name)

    def dangerously_delete(self, bento_name, bento_version):
        return