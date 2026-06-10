package com.smhrd.deulmaru.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Configuration
public class KakaoConfig {

    @Value("${kakao.api.client-id}")
    private String clientId;

    @Value("${kakao.api.redirect-uri}")
    private String redirectUri;

    @Value("${kakao.api.token-url}")
    private String tokenUrl;

    @Value("${kakao.api.user-info-url}")
    private String userInfoUrl;

    // ✅ Getter 메서드 추가 (Thymeleaf에서 사용 가능)
    public String getClientId() {
        return clientId;
    }

    public String getRedirectUri() {
        return redirectUri;
    }

    public String getTokenUrl() {
        return tokenUrl;
    }

    public String getUserInfoUrl() {
        return userInfoUrl;
    }
}
