package com.smhrd.deulmaru.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomeController {

    //  기본 경로("/")를 로그인 페이지로 리다이렉트
    @GetMapping("/")
    public String redirectToLogin() {
        return "home/index";
    }
}
