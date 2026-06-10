package com.smhrd.deulmaru.repository;

import com.smhrd.deulmaru.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<UserEntity, String> {  //  User ID는 String

    //  사용자 ID(userId)로 회원 검색 (username → userId로 변경)
    Optional<UserEntity> findByUserId(String userId);

    //  카카오 ID(kakao_id)로 회원 검색 (Long 타입 유지)
    Optional<UserEntity> findByKakaoId(Long kakaoId);
}
