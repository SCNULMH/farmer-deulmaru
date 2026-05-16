from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_secret_key: str = "change-this-for-local-demo"
    database_backend: str = "sqlite"
    support_api_base_url: str = "http://apis.data.go.kr/1390000/youngV2"
    support_api_service_key: str = ""
    ncpms_api_base_url: str = "http://ncpms.rda.go.kr/npmsAPI/service"
    ncpms_api_key: str = ""
    nongsaro_api_key: str = ""
    kakao_client_id: str = ""
    kakao_redirect_uri: str = "http://127.0.0.1:8000/auth/kakao/callback"
    firebase_credentials_json: str = ""
    google_application_credentials: str = ""
    use_demo_data: bool = True
    diagnosis_model_path: str = "app/ml_models/model.pth"
    max_image_upload_bytes: int = 5 * 1024 * 1024
    diagnosis_timeout_seconds: int = 25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig", extra="ignore")


settings = Settings()
