from pydantic import BaseModel, HttpUrl, SecretStr
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

class CodeforcesRepository(BaseModel):
    issuer: HttpUrl
    redirect_uri: HttpUrl
    client_id: str
    client_secret: SecretStr

    def get_auth_url(self) -> HttpUrl:
        client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

        # we must get provider config to retrieve oauth endpoints
        _ = client.provider_config(str(self.issuer))

        args = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": ["openid"],
            "redirect_uri": [self.redirect_uri],
        }

        auth_req = client.construct_AuthorizationRequest(request_args=args)
        login_url = auth_req.request(client.authorization_endpoint)

        return HttpUrl(login_url)