package com.smhrd.deulmaru.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Service
public class SupportService {

    @Value("${api.baseurl}")
    private String BASE_URL;

    @Value("${api.serviceKey2}")
    private String API_KEY;
    

    public JsonNode getSupportList() {
        try {
            // ✅ URL 인코딩된 서비스 키 생성
            String encodedApiKey = URLEncoder.encode(API_KEY, StandardCharsets.UTF_8);
            String url = BASE_URL + "/policyListV2?typeDv=json&serviceKey=" + encodedApiKey;

            // 📌 로그 추가: 요청 URL 출력
            System.out.println("📌 API 요청 URL: " + url);

            RestTemplate restTemplate = new RestTemplate();
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

            // 📌 로그 추가: 응답 코드 및 데이터 확인
            System.out.println("📌 응답 상태 코드: " + response.getStatusCode());
            System.out.println("📌 응답 데이터: " + response.getBody());

            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode jsonResponse = objectMapper.readTree(response.getBody());

            return jsonResponse;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public JsonNode getSupportDetail(String seq) {
        try {
            String encodedApiKey = URLEncoder.encode(API_KEY, StandardCharsets.UTF_8);
            String url = BASE_URL + "/policyViewV2?typeDv=json&serviceKey=" + encodedApiKey + "&seq=" + seq;

            // 📌 로그 추가: 요청 URL 출력
            System.out.println("📌 API 요청 URL: " + url);

            RestTemplate restTemplate = new RestTemplate();
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

            // 📌 로그 추가: 응답 코드 및 데이터 확인
            System.out.println("📌 응답 상태 코드: " + response.getStatusCode());
            System.out.println("📌 응답 데이터: " + response.getBody());

            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode jsonResponse = objectMapper.readTree(response.getBody());

            return jsonResponse;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
