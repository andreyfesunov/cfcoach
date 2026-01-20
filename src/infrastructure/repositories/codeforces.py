import secrets
import httpx
import jwt
from pydantic import BaseModel, HttpUrl, SecretStr
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

from domain.repositories.codeforces import CodeforcesRepository


class CodeforcesRepositoryImpl(BaseModel, CodeforcesRepository):
    issuer: HttpUrl
    redirect_uri: HttpUrl
    client_id: str
    client_secret: SecretStr

    def get_auth_url(self) -> HttpUrl:
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

        # we must get provider config to retrieve oauth endpoints
        _ = client.provider_config(str(self.issuer))

        redirect_uri_str = str(self.redirect_uri)

        state = secrets.token_urlsafe(32)

        args = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": [redirect_uri_str],
            "state": state,
        }

        auth_req = client.construct_AuthorizationRequest(request_args=args)
        login_url = auth_req.request(client.authorization_endpoint)

        return HttpUrl(login_url)

    def exchange_code_for_tokens(self, code: str, state: str | None = None) -> dict:
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

        # we must get provider config to retrieve oauth endpoints
        _ = client.provider_config(str(self.issuer))

        token_endpoint = client.token_endpoint
        if not token_endpoint:
            raise ValueError("Token endpoint not found in provider config")

        token_endpoint_str = str(token_endpoint)
        if not token_endpoint_str.startswith(("http://", "https://")):
            issuer_str = str(self.issuer)
            token_endpoint_str = (
                f"{issuer_str}{token_endpoint_str}"
                if token_endpoint_str.startswith("/")
                else f"{issuer_str}/{token_endpoint_str}"
            )

        redirect_uri_str = str(self.redirect_uri)

        request_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri_str,
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
        }

        with httpx.Client() as http_client:
            response = http_client.post(
                token_endpoint_str,
                data=request_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if isinstance(error_json, dict):
                        error_msg = error_json.get("error", "unknown_error")
                        error_desc = error_json.get("error_description", "")
                        if error_desc:
                            error_detail = f"{error_msg}: {error_desc}"
                        else:
                            error_detail = error_msg
                    else:
                        error_detail = str(error_json)
                except Exception:
                    pass
                raise ValueError(f"{response.status_code}: {error_detail}")

            result = response.json()
            if "access_token" not in result:
                raise ValueError(f"Token response missing access_token: {result}")

            return result

    def get_user_info(self, access_token: str, id_token: str | None = None) -> dict:
        user_info = {}

        if id_token:
            try:
                decoded_token = jwt.decode(
                    id_token, options={"verify_signature": False}
                )
                user_info.update(decoded_token)
            except Exception:
                pass

        try:
            client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
            _ = client.provider_config(str(self.issuer))

            userinfo_endpoint = client.userinfo_endpoint
            if userinfo_endpoint:
                userinfo_endpoint_str = str(userinfo_endpoint)
                if not userinfo_endpoint_str.startswith(("http://", "https://")):
                    issuer_str = str(self.issuer)
                    userinfo_endpoint_str = (
                        f"{issuer_str}{userinfo_endpoint_str}"
                        if userinfo_endpoint_str.startswith("/")
                        else f"{issuer_str}/{userinfo_endpoint_str}"
                    )

                with httpx.Client() as http_client:
                    response = http_client.get(
                        userinfo_endpoint_str,
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    if response.status_code == 200:
                        user_info.update(response.json())
        except Exception:
            pass

        external_id = (
            user_info.get("sub") or user_info.get("id") or user_info.get("handle")
        )

        if external_id and not user_info.get("handle"):
            try:
                with httpx.Client() as http_client:
                    api_response = http_client.get(
                        f"https://codeforces.com/api/user.info",
                        params={"handles": external_id},
                        headers={"Authorization": f"Bearer {access_token}"}
                        if access_token
                        else None,
                        timeout=10.0,
                    )
                    if api_response.status_code == 200:
                        api_data = api_response.json()
                        if api_data.get("status") == "OK" and api_data.get("result"):
                            cf_user = api_data["result"][0]
                            user_info["handle"] = cf_user.get("handle")
                            user_info["username"] = cf_user.get("handle")
                            user_info["firstName"] = cf_user.get("firstName")
                            user_info["lastName"] = cf_user.get("lastName")
                            user_info["country"] = cf_user.get("country")
                            user_info["city"] = cf_user.get("city")
                            user_info["organization"] = cf_user.get("organization")
            except Exception:
                pass

        return user_info

    def get_user_submissions(
        self,
        handle: str,
        access_token: str = "",
        from_index: int = 1,
        count: int = 1000,
    ) -> list[dict]:
        with httpx.Client() as http_client:
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            response = http_client.get(
                "https://codeforces.com/api/user.status",
                params={"handle": handle, "from": from_index, "count": count},
                headers=headers if headers else None,
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "OK":
                return result.get("result", [])
            raise ValueError(
                f"Failed to get submissions: {result.get('comment', 'Unknown error')}"
            )

    def get_user_rating(self, handle: str, access_token: str) -> list[dict]:
        with httpx.Client() as http_client:
            response = http_client.get(
                "https://codeforces.com/api/user.rating",
                params={"handle": handle},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "OK":
                return result.get("result", [])
            raise ValueError(
                f"Failed to get rating: {result.get('comment', 'Unknown error')}"
            )

    def get_contest_list(self, gym: bool = False) -> list[dict]:
        with httpx.Client() as http_client:
            response = http_client.get(
                "https://codeforces.com/api/contest.list",
                params={"gym": str(gym).lower()},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "OK":
                return result.get("result", [])
            raise ValueError(
                f"Failed to get contest list: {result.get('comment', 'Unknown error')}"
            )

    def get_problem_set(self) -> list[dict]:
        with httpx.Client() as http_client:
            response = http_client.get(
                "https://codeforces.com/api/problemset.problems",
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "OK":
                problems = result.get("result", {}).get("problems", [])
                return problems
            raise ValueError(
                f"Failed to get problem set: {result.get('comment', 'Unknown error')}"
            )

    def get_rated_users(self, active_only: bool = True) -> list[dict]:
        with httpx.Client() as http_client:
            response = http_client.get(
                "https://codeforces.com/api/user.ratedList",
                params={"activeOnly": str(active_only).lower()},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "OK":
                return result.get("result", [])
            raise ValueError(
                f"Failed to get rated users: {result.get('comment', 'Unknown error')}"
            )

    def get_contest_standings(
        self, contest_id: int, from_index: int = 1, count: int = 100
    ) -> list[dict]:
        with httpx.Client() as http_client:
            response = http_client.get(
                "https://codeforces.com/api/contest.standings",
                params={
                    "contestId": contest_id,
                    "from": from_index,
                    "count": count,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "OK":
                return result.get("result", {}).get("rows", [])
            raise ValueError(
                f"Failed to get contest standings: {result.get('comment', 'Unknown error')}"
            )
