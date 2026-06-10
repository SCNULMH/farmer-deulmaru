package com.smhrd.deulmaru.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import jakarta.annotation.PostConstruct;

@Service
public class NcpmsService {
    @Value("${ncpms.api.base-url}")
    private String apiBaseUrl;

    @Value("${ncpms.api.key}")
    private String apiKey;

    private final RestTemplate restTemplate = new RestTemplate();

    public String search(String query, String type) {
        String url = apiBaseUrl + "?apiKey=" + apiKey +
                "&serviceCode=SVC01&serviceType=AA001&displayCount=30&startPoint=1" +
                (type.equals("crop") ? "&cropName=" + query : "&sickNameKor=" + query);
        return restTemplate.getForObject(url, String.class);
    }

    public String getSickDetail(String sickKey) {
        String url = apiBaseUrl + "?apiKey=" + apiKey + "&serviceCode=SVC05&serviceType=AA001&sickKey=" + sickKey;
        return restTemplate.getForObject(url, String.class);
    }

    public String getConsult(String query, int startPoint, int displayCount) {
        String url = apiBaseUrl + "?apiKey=" + apiKey + "&serviceCode=SVC41&serviceType=AA001" +
                "&dgnssReqSj=" + query +
                "&displayCount=" + displayCount +
                "&startPoint=" + startPoint;
        return restTemplate.getForObject(url, String.class);
    }


    public String getConsultDetail(String consultId) {
        String url = apiBaseUrl + "?apiKey=" + apiKey + "&serviceCode=SVC42&serviceType=AA001&dgnssReqNo=" + consultId;
        return restTemplate.getForObject(url, String.class);
    }
}