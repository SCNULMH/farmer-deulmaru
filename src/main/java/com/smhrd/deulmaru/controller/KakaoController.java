package com.smhrd.deulmaru.controller;

import com.smhrd.deulmaru.config.KakaoConfig;
import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.repository.UserRepository;
import com.smhrd.deulmaru.service.KakaoAuthService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.Map;
import java.util.Optional;

@Controller
@RequestMapping("/auth/kakao")
public class KakaoController {

    @Autowired
    private KakaoAuthService kakaoAuthService;

    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private KakaoConfig kakaoConfig;

    //  카카오 로그인 페이지
    @GetMapping("/login")
    public String kakaoLoginPage() {
        return "auth/deulmaru_SignIn";
    }
    
    //  로그아웃 처리
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/";
    }
    
    //  카카오 로그인 후 콜백 처리 (회원가입/연동 여부 확인 포함)
    @GetMapping("/callback")
    public String kakaoCallback(@RequestParam("code") String code, HttpSession session, Model model) {
        String accessToken = kakaoAuthService.getKakaoAccessToken(code);
        if (accessToken == null) {
            return "redirect:/error";
        }
        session.setAttribute("kakaoAccessToken", accessToken);

        //  카카오 사용자 정보 가져오기
        Map<String, Object> kakaoUserInfo = kakaoAuthService.getKakaoUserInfo(accessToken);
        if (kakaoUserInfo == null || !kakaoUserInfo.containsKey("kakaoId")) {
            return "redirect:/error";
        }

        Long kakaoId = ((Number) kakaoUserInfo.get("kakaoId")).longValue();
        String email = (String) kakaoUserInfo.getOrDefault("email", "");
        String nickname = (String) kakaoUserInfo.getOrDefault("nickname", "카카오사용자");

        //  기존 회원이 로그인한 상태에서 카카오 연동을 시도한 경우 → 자동 연동
        UserEntity loggedUser = (UserEntity) session.getAttribute("user");
        if (loggedUser != null) {
            // 이미 카카오 연동된 경우 예외 처리
            if (loggedUser.getKakaoId() != null) {
                return "redirect:/mypage";
            }
            // 카카오 ID 등록 후 저장
            loggedUser.setKakaoId(kakaoId);
            userRepository.save(loggedUser);

            // 세션 업데이트 후 마이페이지 이동
            session.setAttribute("user", loggedUser);
            return "redirect:/mypage";
        }

        // 기존 회원 여부 확인: 카카오 ID로 기존 계정 찾기
        Optional<UserEntity> existingUser = userRepository.findByKakaoId(kakaoId);
        if (existingUser.isPresent()) {
            session.setAttribute("user", existingUser.get());
            return "redirect:/mypage";
        }

        // 기존 회원 여부 확인: 이메일 기반 자동 연동
        Optional<UserEntity> normalUser = userRepository.findByUserId(email);
        if (normalUser.isPresent()) {
            UserEntity user = normalUser.get();
            user.setKakaoId(kakaoId);
            userRepository.save(user);
            session.setAttribute("user", user);
            return "redirect:/mypage";
        }

        // 기존 회원이 아니면 → 카카오 회원가입 페이지로 이동
        session.setAttribute("kakaoUserInfo", kakaoUserInfo);
        return "redirect:/auth/deulmaru_SignIn";
    }


    //  카카오 회원가입 페이지
 //  카카오 회원가입 페이지
    @GetMapping("/register")
    public String kakaoRegisterPage(HttpSession session, Model model) {
        Map<String, Object> kakaoUserInfo = (Map<String, Object>) session.getAttribute("kakaoUserInfo");

        //  디버깅 로그 추가 (카카오 정보 확인)
        System.out.println("세션에서 가져온 kakaoUserInfo: " + kakaoUserInfo);

        //  예외 처리: 세션에 정보가 없으면 로그인 페이지로 리디렉트
        if (kakaoUserInfo == null || !kakaoUserInfo.containsKey("kakaoId")) {
            System.out.println("🔴 kakaoUserInfo가 존재하지 않음. 로그인 페이지로 리디렉트");
            return "redirect:/auth/kakao/login";
        }

        model.addAttribute("kakaoUserInfo", kakaoUserInfo);
        return "auth/deulmaru_SignIn";
    }


    //  카카오 회원가입 처리
    @PostMapping("/register")
    public String kakaoRegister(
            @RequestParam String userId,
            @RequestParam String userEmail,
            @RequestParam String userPw,
            @RequestParam String userNickname,
            @RequestParam(required = false) String userLocate,
            @RequestParam(required = false) String userBirth,
            @RequestParam(required = false) String userGender,
            HttpSession session, Model model) {

        Map<String, Object> kakaoUserInfo = (Map<String, Object>) session.getAttribute("kakaoUserInfo");
        if (kakaoUserInfo == null || !kakaoUserInfo.containsKey("kakaoId")) {
            return "redirect:/auth/kakao/login";
        }

        Long kakaoId = ((Number) kakaoUserInfo.get("kakaoId")).longValue();

        //  중복 체크: userId(로그인용 아이디)가 이미 존재하면 오류 처리
        if (userRepository.findByUserId(userId).isPresent()) {
            model.addAttribute("error", "이미 존재하는 아이디입니다.");
            return "auth/deulmaru_SignIn";
        }

        UserEntity newUser = new UserEntity();
        newUser.setUserId(userId);
        newUser.setUserPw(userPw);
        newUser.setUserNickname(userNickname);
        newUser.setUserEmail(userEmail);
        newUser.setKakaoId(kakaoId);
        newUser.setUserLocate(userLocate != null ? userLocate : "");

        if (userBirth != null && !userBirth.isEmpty()) {
            newUser.setUserBirth(LocalDate.parse(userBirth));
        } else {
            newUser.setUserBirth(LocalDate.of(2000, 1, 1)); // 기본 생년월일 설정
        }
        
        if (userGender != null && !userGender.isEmpty()) {
            newUser.setUserGender(UserEntity.Gender.valueOf(userGender.toUpperCase()));
        } else {
            newUser.setUserGender(UserEntity.Gender.M);
        }
        
        userRepository.save(newUser);
        session.setAttribute("user", newUser);
        model.addAttribute("user", newUser);

        return "redirect:/mypage";
    }

    //  카카오 연동 (일반 회원용)
    @GetMapping("/link")
    public String linkKakaoRedirect(HttpSession session) {
        UserEntity user = (UserEntity) session.getAttribute("user");
        if (user == null) {
            return "redirect:/auth/login";
        }
        if (user.getKakaoId() != null) {
            return "redirect:/mypage";
        }

        session.setAttribute("linking", true);

        // 카카오 OAuth URL 구성
        String oauthUrl = "https://kauth.kakao.com/oauth/authorize"
                + "?client_id=" + kakaoConfig.getClientId()
                + "&redirect_uri=" + kakaoConfig.getRedirectUri()
                + "&response_type=code";

        return "redirect:" + oauthUrl;
    }

    //  카카오 연동 해제
    @PostMapping("/unlink")
    public String unlinkKakao(HttpSession session, Model model) {
        UserEntity user = (UserEntity) session.getAttribute("user");
        if (user == null) {
            return "redirect:/auth/login";
        }
        user.setKakaoId(null);
        userRepository.save(user);
        session.setAttribute("user", user);
        return "redirect:/mypage";
    }
}
