package com.smhrd.deulmaru.service;

import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.repository.UserRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.Optional;

@Service
public class UserService {

	private final UserRepository userRepository;

	public UserService(UserRepository userRepository) {
		this.userRepository = userRepository;
	}

	// 회원가입 (세션 설정 추가)
	public UserEntity registerUser(String userId, String userPw, String userNickname, String userEmail,
			String userLocate, String userBirth, String userGender, Long kakaoId) {
		if (userRepository.findById(userId).isPresent()) {
			throw new RuntimeException("이미 존재하는 아이디입니다.");
		}

		UserEntity user = new UserEntity();
		user.setUserId(userId);
		user.setUserPw(userPw);
		user.setUserNickname(userNickname);
		user.setUserEmail(userEmail);
		user.setUserLocate(userLocate);
		user.setUserBirth(LocalDate.parse(userBirth));
		user.setUserGender(UserEntity.Gender.valueOf(userGender.toUpperCase()));
		user.setKakaoId(kakaoId);

		userRepository.save(user);

	// 회원가입 성공 로그
		System.out.println("회원 저장 완료: " + user.getUserId());

		return user;
	}

	// 로그인 (세션 설정 추가)
	public Optional<UserEntity> loginUser(String userId, String userPw, HttpSession session) {
		Optional<UserEntity> user = userRepository.findById(userId);
		if (user.isPresent() && user.get().getUserPw().equals(userPw)) {
			session.setAttribute("user", user.get()); // 세션에 user 정보 저장
			return user;
		}
		return Optional.empty();
	}

	// 프로필 업데이트
	public void updateUserProfile(String userId, String userPw, String userNickname) {
		Optional<UserEntity> userOpt = userRepository.findById(userId);
		if (userOpt.isPresent()) {
			UserEntity user = userOpt.get();
			if (!userPw.isEmpty()) {
				user.setUserPw(userPw); // 일반 텍스트 저장
			}
			user.setUserNickname(userNickname);
			userRepository.save(user);
		}
	}
	
	

	// 카카오 회원가입 처리 메서드 추가
	public UserEntity registerKakaoUser(String kakaoId, String userNickname, HttpSession session) {
		Optional<UserEntity> existingUser = userRepository.findByKakaoId(Long.parseLong(kakaoId));

		if (existingUser.isPresent()) {
			throw new RuntimeException("이미 가입된 카카오 계정입니다.");
		}

		UserEntity user = new UserEntity();
		user.setKakaoId(Long.parseLong(kakaoId));
		user.setUserNickname(userNickname);
		userRepository.save(user);

		session.setAttribute("user", user); // 세션 저장
		return user;
	}
}
