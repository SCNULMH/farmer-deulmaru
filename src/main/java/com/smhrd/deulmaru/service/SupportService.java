package com.smhrd.deulmaru.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.Map;
import java.util.Set;

@Service
public class SupportService {

    private static final Set<String> ALLOWED_LIST_PARAMETERS = Set.of(
        "rowCnt", "cp", "search_keyword", "search_area1", "sd", "ed",
        "search_status", "minPrice", "maxPrice", "sort"
    );

    @Value("${api.baseurl:https://apis.data.go.kr/1390000/youngV2}")
    private String baseUrl;

    @Value("${api.serviceKey2:${SUPPORT_API_SERVICE_KEY:}}")
    private String apiKey;

    public JsonNode getSupportList(Map<String, String> parameters) {
        UriComponentsBuilder uriBuilder = requestBuilder("/policyListV2");
        parameters.forEach((key, value) -> {
            if (ALLOWED_LIST_PARAMETERS.contains(key) && value != null && !value.isBlank()) {
                uriBuilder.queryParam(key, value);
            }
        });
        return request(uriBuilder.build().encode().toUri());
    }

    public JsonNode getSupportDetail(String seq) {
        if (seq == null || !seq.matches("[A-Za-z0-9_-]+")) {
            throw new IllegalArgumentException("Invalid support sequence");
        }
        URI uri = requestBuilder("/policyViewV2")
            .queryParam("seq", seq)
            .build()
            .encode()
            .toUri();
        return request(uri);
    }

    private UriComponentsBuilder requestBuilder(String path) {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("SUPPORT_API_SERVICE_KEY is not configured");
        }
        return UriComponentsBuilder.fromHttpUrl(baseUrl)
            .path(path)
            .queryParam("typeDv", "json")
            .queryParam("serviceKey", apiKey);
    }

    private JsonNode request(URI uri) {
        try {
            RestTemplate restTemplate = new RestTemplate();
            ResponseEntity<String> response = restTemplate.getForEntity(uri, String.class);
            ObjectMapper objectMapper = new ObjectMapper();
            return objectMapper.readTree(response.getBody());
        } catch (Exception exception) {
            throw new IllegalStateException("Support API request failed", exception);
        }
    }
}
