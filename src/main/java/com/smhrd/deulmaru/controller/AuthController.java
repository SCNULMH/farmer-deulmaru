package com.smhrd.deulmaru.controller;

import com.smhrd.deulmaru.entity.IdentiEntity;
import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.service.IdentiService;
import com.smhrd.deulmaru.service.UserService;
import jakarta.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@Controller
@RequestMapping("/auth") // 공통 URL Prefix 적용
public class AuthController {

	@Autowired
	IdentiService identiService;
	
	@Autowired
	UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    //  로그인 페이지
    @GetMapping("/login")
    public String loginPage() {
        return "auth/deulmaru_Login";
    }



    // 로그인 처리 (일반 로그인)
    @PostMapping("/login")
    public String login(@RequestParam String userId, @RequestParam String userPw, HttpSession session, Model model) {
        Optional<UserEntity> user = userService.loginUser(userId, userPw, session);
        if (user.isPresent()) {
            model.addAttribute("user", user.get());
            return "redirect:/";
        } else {
            model.addAttribute("error", "로그인 실패: 아이디 또는 비밀번호가 틀립니다.");
            return "auth/deulmaru_Login";
        }
    }

    //  로그아웃 처리
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/";
    }

    //  회원가입 선택 페이지
    @GetMapping("/register-options")
    public String showRegisterOptions() {
        return "auth/deulmaru_SignIn_Main";
    }

    // ✅ 일반 회원가입 페이지
    @GetMapping("/register")
    public String registerPage() {
        return "auth/deulmaru_SignIn";
    }

    // ✅ 일반 회원가입 처리
    @PostMapping("/register")
    public String register(@RequestParam String userId, 
                           @RequestParam String userPw, 
                           @RequestParam String userNickname, 
                           @RequestParam String userEmail,
                           @RequestParam String userLocate,
                           @RequestParam String userBirth,
                           @RequestParam String userGender,
                           HttpSession session, 
                           @RequestParam(required = false) Long kakaoId,
                           Model model) {
        try {
            // 회원가입 요청이 올바르게 들어오는지 로그 확인
            System.out.println("회원가입 요청 수신: " + userId + ", " + userEmail);

            UserEntity user = userService.registerUser(userId, userPw, userNickname, userEmail, userLocate, userBirth, userGender, kakaoId);
            session.setAttribute("user", user);
            model.addAttribute("user", user);

            // 회원가입 성공 로그
            System.out.println("회원가입 성공: " + user.getUserId());

            return "redirect:/"; // 회원가입 후 마이페이지로 이동
        } catch (RuntimeException e) {
            model.addAttribute("error", e.getMessage());

            // 회원가입 실패 로그
            System.out.println("회원가입 실패: " + e.getMessage());

            return "auth/deulmaru_SignIn";
        }
    }


    @GetMapping("/deulmaru_Login")
    public String deulmaru_Login() {
        return "auth/deulmaru_Login";
    }

    @GetMapping("/signin")
    public String signInPage() {
        return "auth/deulmaru_SignIn_Main";
    }
 
    @GetMapping("/deulmaru_SignIn")
    public String deulmaruSignIn() {
        return "auth/deulmaru_SignIn";
    }

    @GetMapping("/deulmaru_dictionary")
    public String deulmaru_dictionary(HttpSession session) {
        if (session.getAttribute("user") == null) {
            
        	return "redirect:/auth/login";
            
        }
        return "ncpms/deulmaru_dictionary";
    }

    @GetMapping("/deulmaru_QnA")
    public String deulmaru_QnA(HttpSession session) {
        if (session.getAttribute("user") == null) {
            return "redirect:/auth/login";
        }
        return "ncpms/deulmaru_QnA";
    }

    @GetMapping("/deulmaru_Diagnosis")
    public String deulmaru_Diagnosis(HttpSession session) {
        if (session.getAttribute("user") == null) {
            return "redirect:/auth/login";
        }
        return "ncpms/deulmaru_Diagnosis";
    }
    
    
    
}
