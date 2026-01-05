package repositories

import (
	"context"

	"github.com/andreyfesunov/cfcoach/auth/internal/domain/repositories"
	oidc "github.com/coreos/go-oidc/v3/oidc"
	"golang.org/x/oauth2"
)

type AuthRepositoryImpl struct {
	oidcProvider *oidc.Provider
	oauth2Config oauth2.Config
}

type AuthConfig struct {
	ClientID     string
	ClientSecret string
	RedirectURL  string
	Scopes       []string
	ProviderURL  string
}

const (
	CodeforcesProviderURL = "https://codeforces.com"
)

func NewCodeforcesOAuth2Config(
	clientID, clientSecret string,
) AuthConfig {
	return AuthConfig{
		ClientID:     clientID,
		ClientSecret: clientSecret,
		Scopes:       []string{oidc.ScopeOpenID},
		ProviderURL:  CodeforcesProviderURL,
	}
}

func NewAuthRepository(
	ctx context.Context,
	config AuthConfig,
) (repositories.AuthRepository, error) {
	oidcProvider, err := oidc.NewProvider(ctx, config.ProviderURL)

	if err != nil {
		return nil, err
	}

	return &AuthRepositoryImpl{
		oidcProvider: oidcProvider,
		oauth2Config: oauth2.Config{
			ClientID:     config.ClientID,
			ClientSecret: config.ClientSecret,
			RedirectURL:  config.RedirectURL,
			Scopes:       config.Scopes,
			Endpoint:     oidcProvider.Endpoint(),
		},
	}, nil
}
