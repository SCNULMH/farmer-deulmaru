package com.smhrd.deulmaru.entity;

import lombok.Data;
import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "tb_identi")
@Data
public class IdentiEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // 사용자 ID (마이페이지 연동 시 활용)
    private String userId;
    
    // 업로드된 이미지 파일 경로
    private String imagePath;
    
    // 판별된 병명
    private String diseaseName;
    
    // 작물명
    private String cropName;
    
    // 신뢰도
    private double confidenceScore; 
   
    // 판별 시간
    private LocalDateTime identificationTime;
}
