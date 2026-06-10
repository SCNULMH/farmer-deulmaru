package com.smhrd.deulmaru.controller;

import java.time.LocalDate;
import java.util.Collections;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.entity.UserInterest;
import com.smhrd.deulmaru.service.UserInterestService;

import jakarta.servlet.http.HttpSession;

@RestController
@RequestMapping("/api/interest")
public class UserInterestController {

    private final UserInterestService userInterestService;

    public UserInterestController(UserInterestService userInterestService) {
        this.userInterestService = userInterestService;
    }
    
 //  관심 등록 여부 확인 API
    @GetMapping("/check")
    public ResponseEntity<?> checkInterest(HttpSession session, @RequestParam String grantId) {
        UserEntity loggedInUser = (UserEntity) session.getAttribute("user");

        if (loggedInUser == null) {
            return ResponseEntity.badRequest().body("로그인이 필요합니다.");
        }

        boolean exists = userInterestService.existsByUserIdAndGrantId(loggedInUser.getUserId(), grantId);
        return ResponseEntity.ok(Collections.singletonMap("exists", exists));
    }

    
    //  관심 등록 API (POST 요청만 허용)
    @PostMapping("/add")
    public ResponseEntity<String> addInterest(HttpSession session,
                                              @RequestParam String grantId,
                                              @RequestParam String applEdDt,
                                              @RequestParam String title) {
        UserEntity loggedInUser = (UserEntity) session.getAttribute("user");
        if (loggedInUser == null) {
            return ResponseEntity.badRequest().body("로그인이 필요합니다.");
        }

        String userId = loggedInUser.getUserId();
        LocalDate parsedDate;

        try {
            if (applEdDt.matches("^\\d{4}-\\d{2}-\\d{2}$")) {
                parsedDate = LocalDate.parse(applEdDt);  // yyyy-MM-dd
            } else if (applEdDt.matches("^\\d{4}-\\d{2}$")) {
                LocalDate firstDay = LocalDate.parse(applEdDt + "-01");
                parsedDate = firstDay.withDayOfMonth(firstDay.lengthOfMonth());
            } else {
                return ResponseEntity.badRequest().body("올바르지 않은 날짜 형식입니다.");
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("날짜 파싱 오류: " + e.getMessage());
        }

        String result = userInterestService.addInterest(userId, grantId, parsedDate, title);
        return ResponseEntity.ok(result);
    }



    
    
    // 관심 등록 취소 API (DELETE 방식, 파라미터로 grantId 사용)
    @DeleteMapping("/cancel")
    public ResponseEntity<String> cancelInterest(HttpSession session,
                                                   @RequestParam String grantId) {
        UserEntity loggedInUser = (UserEntity) session.getAttribute("user");

        if (loggedInUser == null) {
            return ResponseEntity.badRequest().body("로그인이 필요합니다.");
        }

        String userId = loggedInUser.getUserId();
        String result = userInterestService.cancelInterest(userId, grantId);
        return ResponseEntity.ok(result);
    }
    
    // 관심 목록 조회
    @GetMapping("/list")
    public ResponseEntity<?> getInterestList(HttpSession session) {
        UserEntity loggedInUser = (UserEntity) session.getAttribute("user");
        if (loggedInUser == null) {
            return ResponseEntity.badRequest().body("로그인이 필요합니다.");
        }
        List<UserInterest> interests = userInterestService.getUserInterests(loggedInUser.getUserId());
        return ResponseEntity.ok(interests);
    }
    
    
}



