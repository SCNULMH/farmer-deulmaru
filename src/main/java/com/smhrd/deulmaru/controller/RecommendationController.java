package com.smhrd.deulmaru.controller;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.smhrd.deulmaru.dto.RecommendationDTO;
import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.service.RecommendationService;
import jakarta.servlet.http.HttpSession;

@RestController
@RequestMapping("/api/recommendation")
public class RecommendationController {

    private final RecommendationService recommendationService;
    private final HttpSession httpSession;

    public RecommendationController(RecommendationService recommendationService, HttpSession httpSession) {
        this.recommendationService = recommendationService;
        this.httpSession = httpSession;
    }

    // 로그인하지 않은 경우: 전체 추천 Top3
    @GetMapping("/overall")
    public ResponseEntity<?> getOverallRecommendations() {
        List<RecommendationDTO> recommendations = recommendationService.getOverallTopRecommendations(3);
        return ResponseEntity.ok(recommendations);
    }

    // 로그인한 경우: 개인 맞춤 추천 – 각 추천 영역에서 Top1씩, 총 3개 반환
    @GetMapping("/personal")
    public ResponseEntity<?> getPersonalRecommendations() {
        UserEntity user = (UserEntity) httpSession.getAttribute("user");
        
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인이 필요합니다.");
        }
        int currentYear = LocalDate.now().getYear();
        int userAge = currentYear - user.getUserBirth().getYear();
        int minAge = (userAge / 10) * 10;
        int maxAge = minAge + 9;
        String gender = user.getUserGender().name(); // "M" 또는 "F"
        String locate = user.getUserLocate(); // 예: "전라남도" 등이 포함된 문자열
        
        // 기존 개인 맞춤 추천 (모든 조건 적용)에서 Top1
        List<RecommendationDTO> overallPersonal = recommendationService.getPersonalRecommendations(gender, minAge, maxAge, locate, 1);
        // 연령대/성별 추천 Top1
        List<RecommendationDTO> ageGender = recommendationService.getAgeGenderRecommendations(gender, minAge, maxAge, 1);
        // 거주지역 추천 Top1
        List<RecommendationDTO> region = recommendationService.getRegionRecommendations(locate, 1);
        
        Map<String, RecommendationDTO> response = new HashMap<>();
        response.put("overall", overallPersonal.isEmpty() ? null : overallPersonal.get(0));
        response.put("ageGender", ageGender.isEmpty() ? null : ageGender.get(0));
        response.put("region", region.isEmpty() ? null : region.get(0));
        
        return ResponseEntity.ok(response);
    }
}
