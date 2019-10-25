import hashlib
import json
import os

import requests
from six import string_types

# from six.moves.urllib.parse import urlparse, urlunparse, parse_q

from urllib import parse
# from socketIO_client import SocketIO, BaseNamespace

# Disable useless warnings
# Works with requests==2.6.0, fails with some other versions
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass

BASE_URL = 'https://app.amigocloud.com'
CHUNK_SIZE = 100000  # 100kB
MAX_SIZE_SIMPLE_UPLOAD = 8000000  # 8MB


class AmigoCloudError(Exception):

    def __init__(self, message, response=None):
        self.message = message
        self.response = response
        self.text = getattr(self.response, 'text', None)

    def __str__(self):
        if self.text:
            return self.message + '\n' + self.text
        return self.message


class AmigoCloud(object):
    """
    Client for the AmigoCloud REST API.
    Uses API tokens for authentication. To generate yours, go to:
        https://app.amigocloud.com/accounts/tokens
    """

    def __init__(self, settings, base_url, project_url=None):
        """
        :param QSettings settings: global settings
        :param str base_url: points to https://app.amigocloud.com by default
        :param str project_url: Specify it if you are using a project token
        """
        self.settings = settings
        # Urls
        if base_url.endswith('/'):
            self.base_url = base_url[:-1]
        else:
            self.base_url = base_url
        self.api_url = self.base_url + '/api/v1'

        self._user_id = None
        self._project_id = None
        self._project_url = None
        self._user_email = None
        self.authenticate(project_url)

    def get_token(self):
        return self.settings.value('tokenValue')

    def get_user_id(self):
        return self._user_id

    def get_user_email(self):
        if not self._user_email:
            response = self.get('/me')
            if response is not None:
                if 'email' in response:
                    self._user_email = response['email']
                if 'id' in response:
                    self._user_id = response['id']
        return str(self._user_email)

    def build_url(self, url):
        if url.startswith('http'):
            # User already specified the full url
            return url
        # User wants to use the api_url
        if url.startswith('/'):
            return self.api_url + url
        return '/'.join(
            s.strip('/') for s in (self._project_url or self.api_url, url))

    def is_good(self, response):
        try:
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as exc:
            print('Exception: ', str(exc))
            return False

    def authenticate(self, project_url=None):
        self._project_url = (self.build_url(project_url) if project_url
                             else None)
        if not self._project_url:
            response = self.get('/me')
            if response is not None and 'id' in response.values():
                self._user_id = response['id']
        else:
            response = self.get('')
            if response is not None and 'id' in response.values():
                self._project_id = response['id']

    def logout(self):
        self._user_id = None
        self._project_id = None
        self._project_url = None

    def get(self, url, params=None, raw=False, stream=False, **request_kwargs):
        """
        GET request to AmigoCloud endpoint.
        """

        full_url = self.build_url(url)
        params = params or {}

        # Add token (if it's not already there)
        token = self.get_token()
        if token:
            params.setdefault('token', token)
        response = requests.get(full_url, params=params, stream=stream,
                                **request_kwargs)
        if self.is_good(response):  # Raise exception if something failed
            if stream:
                return response
            if raw or not response.content:
                return response.content
            return json.loads(response.text)
        else:
            return None

    def _secure_request(self, url, method, data=None, files=None, headers=None,
                        raw=False, send_as_json=True, content_type=None,
                        **request_kwargs):

        full_url = self.build_url(url)

        # Add token (if it's not already there)
        token = self.get_token()
        if token:
            parsed = list(parse.urlparse(full_url))
            if not parsed[4]:  # query
                parsed[4] = 'token=%s' % token
                full_url = parse.urlunparse(parsed)
            elif 'token' not in parse.parse_qs(parsed[4]):
                parsed[4] += '&token=%s' % token
                full_url = parse.urlunparse(parsed)
        headers = headers or {}

        # If files are being sent, we cannot encode data as JSON
        if send_as_json and not files:
            headers['content-type'] = 'application/json'
            data = json.dumps(data or {})
        else:
            if content_type:
                headers['content-type'] = content_type
            data = data or ''

        method = getattr(requests, method, None)
        response = method(full_url, data=data, files=files, headers=headers,
                          **request_kwargs)
        if self.is_good(response):  # Raise exception if something failed
            if raw or not response.content:
                return response.content
            return json.loads(response.text)
        else:
            return None

    def post(self, url, data=None, files=None, headers=None, raw=False,
             send_as_json=True, content_type=None, **request_kwargs):
        """
        POST request to AmigoCloud endpoint.
        """

        return self._secure_request(
            url, 'post', data=data, files=files, headers=headers, raw=raw,
            send_as_json=send_as_json, content_type=content_type,
            **request_kwargs
        )

    def put(self, url, data=None, files=None, headers=None, raw=False,
            send_as_json=True, content_type=None, **request_kwargs):
        """
        PUT request to AmigoCloud endpoint.
        """

        return self._secure_request(
            url, 'put', data=data, files=files, headers=headers, raw=raw,
            send_as_json=send_as_json, content_type=content_type,
            **request_kwargs
        )

    def patch(self, url, data=None, files=None, headers=None, raw=False,
              send_as_json=True, content_type=None, **request_kwargs):
        """
        PATCH request to AmigoCloud endpoint.
        """

        return self._secure_request(
            url, 'patch', data=data, files=files, headers=headers, raw=raw,
            send_as_json=send_as_json, content_type=content_type,
            **request_kwargs
        )

    def delete(self, url, data=None, files=None, headers=None, raw=False,
               send_as_json=True, content_type=None, **request_kwargs):
        """
        DELETE request to AmigoCloud endpoint.
        """

        return self._secure_request(
            url, 'delete', data=data, files=files, headers=headers, raw=raw,
            send_as_json=send_as_json, content_type=content_type,
            **request_kwargs
        )

    def upload_file(self, simple_upload_url, chunked_upload_url, file_obj,
                    chunk_size=CHUNK_SIZE, force_chunked=False,
                    extra_data=None):
        """
        Generic method to upload files to AmigoCloud. Can be used for different
        API endpoints.
        `file_obj` could be a file-like object or a filepath.
        If the size of the file is greater than MAX_SIZE_SIMPLE_UPLOAD (8MB)
        `chunked_upload_url` will be used, otherwise `simple_upload_url` will
        be.
        If `simple_upload_url` evaluates to False, or `force_chunked` is True,
        the `chunked_upload_url` will always be used.
        """

        if isinstance(file_obj, string_types):
            # file_obj is a filepath: open file and close it at the end
            file_obj = open(file_obj, 'rb')
            close_file = True
        else:
            # assume file_obj is a file-like object
            close_file = False

        # Get file size
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)

        try:
            # Simple upload?
            if (simple_upload_url and not force_chunked
                    and file_size < MAX_SIZE_SIMPLE_UPLOAD):
                return self.post(simple_upload_url, data=extra_data,
                                 files={'datafile': file_obj})
            # Chunked upload
            data = {}
            md5_hash = hashlib.md5()
            start_byte = 0
            while True:
                chunk = file_obj.read(chunk_size)
                md5_hash.update(chunk)
                end_byte = start_byte + len(chunk) - 1
                content_range = 'bytes %d-%d/%d' % (start_byte, end_byte,
                                                    file_size)
                ret = self.post(chunked_upload_url, data=data,
                                files={'datafile': chunk},
                                headers={'Content-Range': content_range})
                data.setdefault('upload_id', ret['upload_id'])
                start_byte = end_byte + 1
                if start_byte == file_size:
                    break
            # Complete request
            if chunked_upload_url.endswith('/'):
                chunked_upload_complete_url = chunked_upload_url + 'complete'
            else:
                chunked_upload_complete_url = chunked_upload_url + '/complete'
            data['md5'] = md5_hash.hexdigest()
            if extra_data:
                data.update(extra_data)
            return self.post(chunked_upload_complete_url, data=data)
        finally:
            if close_file:
                file_obj.close()

    def upload_datafile(self, project_owner, project_id, file_obj,
                        chunk_size=CHUNK_SIZE, force_chunked=False):
        """
        Upload datafile to a project. The file must be a supported format or a
        zip file containing supported formats.
        To see the formats we support, go to this URL:
        http://help.amigocloud.com/hc/en-us/articles/202413410-Supported-Format
        """

        simple_upload_url = 'users/%s/projects/%s/datasets/upload' % (
            project_owner, project_id
        )
        chunked_upload_url = 'users/%s/projects/%s/datasets/chunked_upload' % (
            project_owner, project_id
        )

        return self.upload_file(simple_upload_url, chunked_upload_url,
                                file_obj, chunk_size=chunk_size,
                                force_chunked=force_chunked)

    def upload_gallery_photo(self, gallery_id, source_amigo_id, file_obj,
                             chunk_size=CHUNK_SIZE, force_chunked=False,
                             metadata=None):
        """
        Upload a photo to a dataset's gallery.
        """

        simple_upload_url = 'related_tables/%s/upload' % gallery_id
        chunked_upload_url = 'related_tables/%s/chunked_upload' % gallery_id

        data = {'source_amigo_id': source_amigo_id}
        if isinstance(file_obj, basestring):
            data['filename'] = os.path.basename(file_obj)
        else:
            data['filename'] = os.path.basename(file_obj.name)
        if metadata:
            data.update(metadata)

        return self.upload_file(simple_upload_url, chunked_upload_url,
                                file_obj, chunk_size=chunk_size,
                                force_chunked=force_chunked, extra_data=data)
