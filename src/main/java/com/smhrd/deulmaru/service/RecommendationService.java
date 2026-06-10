package com.smhrd.deulmaru.service;

import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;
import com.smhrd.deulmaru.dto.RecommendationDTO;
import com.smhrd.deulmaru.repository.UserInterestRepository;

@Service
public class RecommendationService {

    private final UserInterestRepository userInterestRepository;

    public RecommendationService(UserInterestRepository userInterestRepository) {
        this.userInterestRepository = userInterestRepository;
    }

    // 전체 Top 추천 (로그인하지 않은 경우) – Top N개
    public List<RecommendationDTO> getOverallTopRecommendations(int limit) {
        List<Object[]> results = userInterestRepository.findOverallTopRecommendationsWithoutLimit();
        if (results.size() > limit) {
            results = results.subList(0, limit);
        }
        List<RecommendationDTO> recommendations = new ArrayList<>();
        for (Object[] row : results) {
            RecommendationDTO dto = new RecommendationDTO();
            dto.setGrantId(String.valueOf(row[0]));
            dto.setInterestCount(((Number) row[1]).longValue());
            recommendations.add(dto);
        }
        return recommendations;
    }

    // 기존 개인 맞춤 추천 (모든 조건 동시 적용) – 여기서는 Top1만 반환
    public List<RecommendationDTO> getPersonalRecommendations(String gender, int minAge, int maxAge, String locate, int limit) {
        List<Object[]> results = userInterestRepository.findPersonalTopRecommendationsWithoutLimit(gender, minAge, maxAge, locate);
        if (results.size() > limit) {
            results = results.subList(0, limit);
        }
        List<RecommendationDTO> recommendations = new ArrayList<>();
        for (Object[] row : results) {
            RecommendationDTO dto = new RecommendationDTO();
            dto.setGrantId(String.valueOf(row[0]));
            dto.setInterestCount(((Number) row[1]).longValue());
            recommendations.add(dto);
        }
        return recommendations;
    }
    
    // 새로 추가: 연령대/성별 추천 – Top1만 반환
    public List<RecommendationDTO> getAgeGenderRecommendations(String gender, int minAge, int maxAge, int limit) {
        List<Object[]> results = userInterestRepository.findAgeGenderRecommendations(gender, minAge, maxAge);
        if (results.size() > limit) {
            results = results.subList(0, limit);
        }
        List<RecommendationDTO> recommendations = new ArrayList<>();
        for (Object[] row : results) {
            RecommendationDTO dto = new RecommendationDTO();
            dto.setGrantId(String.valueOf(row[0]));
            dto.setInterestCount(((Number) row[1]).longValue());
            recommendations.add(dto);
        }
        return recommendations;
    }
    
    // 새로 추가: 거주지역 추천 – Top1만 반환
    public List<RecommendationDTO> getRegionRecommendations(String region, int limit) {
        List<Object[]> results = userInterestRepository.findRegionRecommendations(region);
        if (results.size() > limit) {
            results = results.subList(0, limit);
        }
        List<RecommendationDTO> recommendations = new ArrayList<>();
        for (Object[] row : results) {
            RecommendationDTO dto = new RecommendationDTO();
            dto.setGrantId(String.valueOf(row[0]));
            dto.setInterestCount(((Number) row[1]).longValue());
            recommendations.add(dto);
        }
        return recommendations;
    }
}
