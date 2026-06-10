package com.smhrd.deulmaru.controller;

import com.smhrd.deulmaru.entity.IdentiEntity;
import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.service.IdentiService;
import jakarta.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/ident")
public class IdentiController {
	
	@Autowired
    IdentiService identiService;

    public IdentiController(IdentiService identiService) {
        this.identiService = identiService;
    }

    @PostMapping("/save")
    public ResponseEntity<?> saveIdenti(HttpSession session,
                                        @RequestParam String diseaseName,
                                        @RequestParam String confidenceScore,
                                        @RequestParam String cropName,
                                        @RequestPart("file") MultipartFile file,
                                        @RequestParam(defaultValue = "true") boolean overwrite) {
        try {
            UserEntity user = (UserEntity) session.getAttribute("user");
            if (user == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인 정보가 없습니다.");
            }

            String userId = user.getUserId();
            diseaseName = diseaseName.replace("병해충 진단 결과:", "").replace("예측 결과:", "").trim();
            double confidenceScoreValue = Double.parseDouble(confidenceScore.replace("%", "").trim());
            String imagePath = identiService.storeImage(file, overwrite);
            IdentiEntity entity = identiService.saveIdentiResult(userId, diseaseName, cropName, confidenceScoreValue, imagePath);

            Map<String, Object> response = new HashMap<>();
            response.put("message", "저장 완료");
            response.put("data", entity);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("저장 실패: " + e.getMessage());
        }
    }
    // 진단이력 불러오기
    @GetMapping("/history")
    public List<IdentiEntity> getDiagnosisHistory(HttpSession session) {
        UserEntity user = (UserEntity) session.getAttribute("user");
        if (user == null) {
            return new ArrayList<>(); // 혹은 HTTP 401 에러 응답 처리 가능
        }
        return identiService.getHistoryByUserId(user.getUserId());
    }

    // 진단이력 삭제하기
    @DeleteMapping("/delete/{id}")
    public ResponseEntity<?> deleteDiagnosis(@PathVariable Long id, HttpSession session) {
        UserEntity user = (UserEntity) session.getAttribute("user");

        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인 필요");
        }

        boolean deleted = identiService.deleteByIdAndUser(id, user.getUserId());

        if (deleted) {
            return ResponseEntity.ok("삭제 완료");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("삭제할 이력이 없거나 권한 없음");
        }
    }














}
