from gitlab import GitlabHttpError
from requests.exceptions import ConnectTimeout, ReadTimeout

sync_errors = ConnectTimeout, ReadTimeout, GitlabHttpError
