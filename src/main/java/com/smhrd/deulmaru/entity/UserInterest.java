package com.smhrd.deulmaru.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "TB_USER_INTEREST", uniqueConstraints = {
        @UniqueConstraint(columnNames = {"USER_ID", "GRANT_ID"})
}) //  기존 복합 키는 UNIQUE 제약으로 유지
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UserInterest {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 단일 기본 키 (AUTO_INCREMENT)
    @Column(name = "INTEREST_IDX")
    private Long interestIdx;

    @Column(name = "USER_ID", nullable = false)
    private String userId;

    @Column(name = "GRANT_ID", nullable = false)
    private String grantId;

    @Column(name = "APPL_ED_DT", nullable = false)
    private LocalDate applEdDt;

    @Column(name = "ALARM_ENABLED", nullable = false)
    private boolean alarmEnabled = true;

    @Column(name = "ADDED_AT", nullable = false, updatable = false, insertable = false)
    private LocalDateTime addedAt = LocalDateTime.now();
    
    // 신규 추가: 알림 표시 여부 (마감 임박 알림 활성화 여부)
    @Column(name = "NOTIFY_YN", nullable = false)
    private boolean notifyYn = false;
    
    @Column(name = "TITLE")
    private String title;
}
