import requests
import json

from bitbucket.exceptions import UnknownError, InvalidIDError, NotFoundIDError, NotAuthenticatedError, PermissionError


class Client(object):
    BASE_URL = 'https://api.bitbucket.org/'
    TOKEN_URL = 'https://bitbucket.org/site/oauth2/access_token'

    def __init__(self, user=None, password=None, token=None, client_id=None, client_secret=None):
        """Initial session with user/password, and setup repository owner

        Args:
            params:

        Returns:

        """

        self.user = user
        self.password = password
        self.use_password = False
        self.use_token = False
        if user and password:
            self.use_password = True
        self.token = token
        if token:
            self.use_token = True
        elif client_id and client_secret:
            token_req_payload = {'grant_type': 'client_credentials'}
            response = requests.post(self.TOKEN_URL, data=token_req_payload, allow_redirects=False, auth=(client_id, client_secret))
            response = self._parse(response)
            self.token = response['access_token']
            self.use_token = True

        if not (self.use_password or self.token):
            raise NotAuthenticatedError("Insufficient credentials")

    def initialize(self, owner=None):
        user_data = self.get_user()
        # for shared repo, set baseURL to owner
        if owner is None:
            owner = user_data.get('username')
        self.username = owner

    def get_commit_statuses(self, repository_slug, commit_hash, params=None):
        """Returns the statuses for a specific commit.

        Args:
            repository_slug:
            commit_hash:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/commit/{}/statuses'.format(self.username, repository_slug, commit_hash),
                         params=params)

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

    def create_repository(self, params=None, data=None, name=None, team=None):
        """Creates a new repository.

        Example:
            {
              "scm": "git",
              "description": "Repository Description",
              "is_private": boolean,
              "project": [
                "key": "Project key"
              ]
            }

        Args:
            data:
            params:
            Name: 
            team:
        Returns: Repository
        """
        return self._post('2.0/repositories/{}/{}'.format(team, name), params, data)

    def create_commit_status(self, repository_slug, commit_hash, data, params=None):
        """Creates a new commit status.

        This call requires authentication. Private repositories or private issue trackers require
        the caller to authenticate with an account that has appropriate authorisation.

        The authenticated user is used for the status' creator.

        Args:
            repository_slug:
            commit_hash:
            data:
            params:

        Returns:

        """
        return self._post('2.0/repositories/{}/{}/commit/{}/statuses/build'.format(self.username, repository_slug,
                                                                              commit_hash), params=params, data=data)

    def get_repository_branches(self, repository_slug, params=None):
        return self._get('2.0/repositories/{}/{}/refs/branches'.format(self.username, repository_slug), params=params)

    def get_repository_tags(self, repository_slug, params=None):
        return self._get('2.0/repositories/{}/{}/refs/tags'.format(self.username, repository_slug), params=params)

    def get_repository_commits(self, repository_slug, params=None):
        """Returns the commits from the repository.

        Params can be used to return commits from a branch like this:

            params={'include': 'branch'}

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/commits'.format(self.username, repository_slug), params=params)

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

    def get_repository_source_code(self, repository_slug, params=None):
        """Returns data about the source code of given repository.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/src'.format(self.username, repository_slug), params=params)

    def get_repository_commit_path_source_code(self, repository_slug, commit_hash, path, params=None):
        """Returns source code of given path at specified commit_hash of given repository.

        Args:
            repository_slug:
            commit_hash:
            path:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/src/{}/{}'.format(
            self.username,
            repository_slug,
            commit_hash,
            path
        ), params=params)

    def create_issue(self, repository_slug, data, params=None):
        """Creates a new issue.

        This call requires authentication. Private repositories or private issue trackers require
        the caller to authenticate with an account that has appropriate authorisation.

        The authenticated user is used for the issue's reporter field.

        Args:
            repository_slug:
            data:
            params:

        Returns:

        """
        return self._post('2.0/repositories/{}/{}/issues'.format(self.username, repository_slug), data=data,
                          params=params)

    def get_issue(self, repository_slug, issue_id, params=None):
        """Returns the specified issue.

        Args:
            repository_slug:
            issue_id:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/issues/{}'.format(self.username, repository_slug, issue_id),
                         params=params)

    def get_issues(self, repository_slug, params=None):
        """Returns the issues in the issue tracker.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/issues'.format(self.username, repository_slug), params=params)

    def delete_issue(self, repository_slug, issue_id, params=None):
        """Deletes the specified issue. This requires write access to the repository.

        Args:
            repository_slug:
            issue_id:
            params:

        Returns:

        """
        return self._delete('2.0/repositories/{}/{}/issues/{}'.format(self.username, repository_slug, issue_id),
                            params=params)

    def create_webhook(self, repository_slug, data, params=None):
        """Creates a new webhook on the specified repository.

        Example:
            {
              "description": "Webhook Description",
              "url": "https://example.com/",
              "active": true,
              "events": [
                "repo:push",
                "issue:created",
                "issue:updated"
              ]
            }

        Note that this call requires the webhook scope, as well as any scope that applies to the events
        that the webhook subscribes to. In the example above that means: webhook, repository and issue.
        Also note that the url must properly resolve and cannot be an internal, non-routed address.

        Args:
            repository_slug:
            data:
            params:

        Returns:

        """
        return self._post('2.0/repositories/{}/{}/hooks'.format(self.username, repository_slug), data=data,
                          params=params)

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

    def get_webhooks(self, repository_slug, params=None):
        """Returns a paginated list of webhooks installed on this repository.

        Args:
            repository_slug:
            params:

        Returns:

        """
        return self._get('2.0/repositories/{}/{}/hooks'.format(self.username, repository_slug), params=params)

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
    
    def get_diff_stat(self, commit, repo_slug, parent=None):
        """
        Returns diff stat for given commits
        """
        if parent:
            return self._get(f'2.0/repositories/{self.username}/{repo_slug}/diffstat/{commit}..{parent}')
        else:
            return self._get(f'2.0/repositories/{self.username}/{repo_slug}/diffstat/{commit}')

    def _get(self, endpoint, params=None):
        if self.use_password:
            response = requests.get(self.BASE_URL + endpoint, params=params, auth=(self.user, self.password))
        elif self.use_token:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.request(
                "GET",
                self.BASE_URL + endpoint,
                params=params,
                headers=headers
            )
        else:
            raise NotAuthenticatedError("Insufficient credentials")
        return self._parse(response)

    def _post(self, endpoint, params=None, data=None):
        if self.use_password:
            response = requests.post(self.BASE_URL + endpoint, params=params, json=data, auth=(self.user, self.password))
        elif self.use_token:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.request(
                "POST",
                self.BASE_URL + endpoint,
                params=params, json=data,
                headers=headers
            )
        else:
            raise NotAuthenticatedError("Insufficient credentials")
        return self._parse(response)

    def _put(self, endpoint, params=None, data=None):
        if self.use_password:
            response = requests.put(self.BASE_URL + endpoint, params=params, json=data, auth=(self.user, self.password))
        elif self.use_token:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.request(
                "PUT",
                self.BASE_URL + endpoint,
                params=params, json=data,
                headers=headers
            )
        else:
            raise NotAuthenticatedError("Insufficient credentials")
        return self._parse(response)

    def _delete(self, endpoint, params=None):
        if self.use_password:
            response = requests.delete(self.BASE_URL + endpoint, params=params, auth=(self.user, self.password))
        elif self.use_token:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.request(
                "DELETE",
                self.BASE_URL + endpoint,
                params=params,
                headers=headers
            )
        else:
            raise NotAuthenticatedError("Insufficient credentials")
        return self._parse(response)

    def _parse(self, response):
        status_code = response.status_code
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.text
        if status_code in (200, 201):
            return r
        if status_code == 204:
            return None
        message = None
        try:
            if 'errorMessages' in r:
                message = r['errorMessages']
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
