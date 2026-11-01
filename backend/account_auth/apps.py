from django.apps import AppConfig


class account_authConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account_auth'

    def ready(self):
        from django.conf import settings

        from .oidc import logger, sign_algo_supported, tls_settings_problem

        if not settings.OIDC_ENABLED:
            return
        # oidc_enabled() turns OIDC off for an unusable setup; say so once instead of failing silently.
        if not sign_algo_supported():
            logger.error(
                "OIDC login is disabled: OIDC_SIGN_ALGO %r is not supported (RS256/384/512 or ES256/384/512; "
                "HS256/384/512 are not, select a signing key at the provider instead).",
                settings.OIDC_RP_SIGN_ALGO,
            )
        problem = tls_settings_problem()
        if problem:
            logger.error("OIDC login is disabled: %s", problem)
        elif settings.OIDC_SKIP_SSL_VERIFICATION:
            logger.warning(
                "OIDC_SKIP_SSL_VERIFICATION is set: provider certificates are not checked, so anyone on the "
                "network path can read the client secret and log in as any user. Prefer OIDC_CA_BUNDLE."
            )
