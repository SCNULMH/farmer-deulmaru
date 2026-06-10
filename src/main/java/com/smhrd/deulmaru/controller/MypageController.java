package com.smhrd.deulmaru.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.smhrd.deulmaru.entity.UserEntity;
import com.smhrd.deulmaru.repository.UserRepository;

import jakarta.servlet.http.HttpSession;

@Controller
@RequestMapping("/mypage")
public class MypageController {

    private final UserRepository userRepository;

    public MypageController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    //  마이페이지 이동
    @GetMapping("")
    public String myPage(HttpSession session, Model model) {
        UserEntity user = (UserEntity) session.getAttribute("user");
        if (user == null) {
            return "redirect:/auth/deulmaru_Login";
        }
        model.addAttribute("user", user);
        return "/auth/deulmaru_Mypage";
    }

    //  회원정보 수정 (기존 업데이트)
    @PostMapping("/update-profile")
    public String updateProfile(@RequestParam String userNickname,
                                @RequestParam(required = false) String userPw,
                                @RequestParam String userLocate,
                                @RequestParam(required = false) String userCrop, // 추가된 부분
                                HttpSession session) {
        UserEntity user = (UserEntity) session.getAttribute("user");
        if (user == null) {
            return "redirect:/auth/login";
        }

        // 닉네임 변경
        user.setUserNickname(userNickname);
        
        // 주소지 변경
        user.setUserLocate(userLocate);
        
        // 재배작물 변경 (userCrop가 null이 아니면 업데이트)
        if (userCrop != null && !userCrop.isEmpty()) {
            user.setUserCrop(userCrop);
        }
         
        // 비밀번호 변경이 입력되었을 경우에만 적용
        if (userPw != null && !userPw.isEmpty()) {
            user.setUserPw(userPw);
        }

        userRepository.save(user);
        session.setAttribute("user", user);
        return "redirect:/auth/mypage";
    }

    //  재배작물만 업데이트하는 새 엔드포인트 (AJAX 호출용)
    @PostMapping("/update-crop")
    @ResponseBody
    public ResponseEntity<String> updateCrop(@RequestParam String userCrop, HttpSession session) {
        UserEntity user = (UserEntity) session.getAttribute("user");
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인이 필요합니다.");
        }

        user.setUserCrop(userCrop);
        userRepository.save(user);
        session.setAttribute("user", user);
        return ResponseEntity.ok("재배작물 정보가 업데이트되었습니다.");
    }

}