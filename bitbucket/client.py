import requests
from bitbucket.exceptions import UnknownError, InvalidIDError, NotFoundIDError, NotAuthenticatedError, PermissionError


class Client(object):
    BASE_URL = 'https://api.bitbucket.org/'

    def __init__(self, user, password):
        self.user = user
        self.password = password

        user_data = self.get_user()
        self.username = user_data.get('username')

    def get_user(self, params=None):
        """Returns the currently logged in user.

        Args:
            params:

        Returns:

        """
        return self._get('2.0/user', params=params)

    def get_privileges(self, params=None):
        """Gets a list of all the privilege across all an account's repositories.
        If a repository has no individual users with privileges, it does not appear in this list.
        Only the repository owner, a team account administrator, or an account with administrative
        rights on the repository can make this call. This method has the following parameters:


        Args:
            params:

        Returns:

        """
        return self._get('1.0/privileges/{}'.format(self.username), params=params)

    def get_repositories(self, params=None):
        """Returns a paginated list of all repositories owned by the specified account or UUID.

        The result can be narrowed down based on the authenticated user's role.

        E.g. with ?role=contributor, only those repositories that the authenticated user has write access to are
        returned (this includes any repo the user is an admin on, as that implies write access).

        This endpoint also supports filtering and sorting of the results. See filtering and sorting for more details.

        Args:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}'.format(self.username), params=params)

    def get_repository(self, repository_slug, params=None):
        """Returns the object describing this repository.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}'.format(self.username, repository_slug), params=params)

    def get_repository_branches(self, repository_slug, params=None):
        return self._get('2.0/repositories/{}/{}/refs/branches'.format(self.username, repository_slug), params=params)

    def get_repository_tags(self, repository_slug, params=None):
        return self._get('2.0/repositories/{}/{}/refs/tags'.format(self.username, repository_slug), params=params)

    def get_repository_components(self, repository_slug, params=None):
        """Returns the components that have been defined in the issue tracker.

        This resource is only available on repositories that have the issue tracker enabled.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/components'.format(self.username, repository_slug), params=params)

    def get_repository_milestones(self, repository_slug, params=None):
        """Returns the milestones that have been defined in the issue tracker.

        This resource is only available on repositories that have the issue tracker enabled.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/milestones'.format(self.username, repository_slug), params=params)

    def get_repository_versions(self, repository_slug, params=None):
        """Returns the versions that have been defined in the issue tracker.

        This resource is only available on repositories that have the issue tracker enabled.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/versions'.format(self.username, repository_slug), params=params)

    def create_webhook(self, repository_slug, params=None):
        """Updates the specified webhook subscription.

        The following properties can be mutated:
        description
        url
        active
        events

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._put('2.0/repositories/{}/{}/hooks'.format(self.username, repository_slug), params=params)

    def get_webhook(self, repository_slug, webhook_uid, params=None):
        """Returns the webhook with the specified id installed on the specified repository.

        Args:
            repository_slug:
            webhook_uid:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/hooks/{}'.format(self.username, repository_slug, webhook_uid),
                         params=params)

    def delete_webhook(self, repository_slug, webhook_uid, params=None):
        """Deletes the specified webhook subscription from the given repository.

        Args:
            repository_slug:
            webhook_uid:
            params:

        Returns:

        """
        return self._delete('2.0/repositories/{}/{}/hooks/{}'.format(self.username, repository_slug, webhook_uid),
                            params=params)

    def _get(self, endpoint, params=None):
        response = requests.get(self.BASE_URL + endpoint, params=params, auth=(self.user, self.password))
        return self._parse(response)

    def _post(self, endpoint, params=None, data=None):
        response = requests.post(self.BASE_URL + endpoint, params=params, json=data, auth=(self.user, self.password))
        return self._parse(response)

    def _put(self, endpoint, params=None, data=None):
        response = requests.put(self.BASE_URL + endpoint, params=params, json=data, auth=(self.user, self.password))
        return self._parse(response)

    def _delete(self, endpoint, params=None):
        response = requests.delete(self.BASE_URL + endpoint, params=params, auth=(self.user, self.password))
        return self._parse(response)

    def _parse(self, response):
        status_code = response.status_code
        if status_code == 200 or status_code == 201:
            return response.json()
        if status_code == 204:
            return None
        message = None
        try:
            _json = response.json()
            if 'errorMessages' in _json:
                message = _json['errorMessages']
        except Exception:
            message = 'No error message.'
        if status_code == 400:
            raise InvalidIDError(message)
        if status_code == 401:
            raise NotAuthenticatedError(message)
        if status_code == 403:
            raise PermissionError(message)
        if status_code == 404:
            raise NotFoundIDError(message)
        raise UnknownError(message)
