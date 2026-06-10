package com.smhrd.deulmaru.service;

import com.smhrd.deulmaru.entity.UserInterest;
import com.smhrd.deulmaru.repository.UserInterestRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
public class UserInterestService {

    private final UserInterestRepository userInterestRepository;

    public UserInterestService(UserInterestRepository userInterestRepository) {
        this.userInterestRepository = userInterestRepository;
    }
    
    // ✅ 관심 등록 여부 확인
    public boolean existsByUserIdAndGrantId(String userId, String grantId) {
        return userInterestRepository.existsByUserIdAndGrantId(userId, grantId);
    }
    
    // ✅ 관심 지원금 등록
    @Transactional
    public String addInterest(String userId, String grantId, LocalDate applEdDt, String title) {
        if (userInterestRepository.existsByUserIdAndGrantId(userId, grantId)) {
            return "이미 관심 등록된 지원금입니다.";
        }
        // 기본적으로 alarmEnabled는 true, notifyYn은 false로 설정합니다.
        UserInterest interest = new UserInterest(null, userId, grantId, applEdDt, true, null, false, title);
        interest.setTitle(title);
        userInterestRepository.save(interest);
        return "관심 등록이 완료되었습니다.";
    }


    // 관심 지원금 목록 조회
    public List<UserInterest> getUserInterests(String userId) {
        // 업데이트 후 조회하면, 마감 임박 알림이 활성화된 항목을 확인할 수 있음.
        updateImminentNotifications(userId);
        return userInterestRepository.findByUserId(userId);
    }

    // ✅ 관심 지원금 삭제
    @Transactional
    public String cancelInterest(String userId, String grantId) {
        if (!userInterestRepository.existsByUserIdAndGrantId(userId, grantId)) {
            return "관심 등록된 지원금이 없습니다.";
        }
        userInterestRepository.deleteByUserIdAndGrantId(userId, grantId);
        return "관심 등록이 취소되었습니다.";
    }
    
    // 알람 기능
    @Transactional
    public void updateImminentNotifications(String userId) {
        List<UserInterest> interests = userInterestRepository.findByUserId(userId);
        LocalDate today = LocalDate.now();
        
        for (UserInterest interest : interests) {
            long remainingDays = java.time.temporal.ChronoUnit.DAYS.between(today, interest.getApplEdDt());
            // alarmEnabled 체크는 필요하다면 추가
            if (interest.isAlarmEnabled() && remainingDays <= 14 && remainingDays >= 0) {
                // 마감 임박 상태이면 알림을 활성화 (notifyYn = true)
                interest.setNotifyYn(true);
            } else {
                // 조건에 맞지 않으면 알림 비활성화 (옵션)
                interest.setNotifyYn(false);
            }
        }
        // 변경된 interest들은 Transaction 내에서 자동으로 flush됨.
    }
    
    


}
