package com.smhrd.deulmaru.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.smhrd.deulmaru.service.SupportService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.Map;

@Controller
@RequestMapping("/supportApi")
public class SupportController {

    private final SupportService supportService;

    public SupportController(SupportService supportService) {
        this.supportService = supportService;
    }

    @GetMapping("/support")
    public String grantsPage() {
        return "supportApi/support";
    }

    @GetMapping("/detail/{seq}")
    public String grantDetailPage(@PathVariable String seq, Model model) {
        model.addAttribute("seq", seq);
        return "supportApi/support-detail";
    }

    @GetMapping("/api/list")
    @ResponseBody
    public ResponseEntity<?> supportList(@RequestParam Map<String, String> parameters) {
        try {
            JsonNode result = supportService.getSupportList(parameters);
            return ResponseEntity.ok(result);
        } catch (IllegalStateException exception) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(Map.of("error", "지원사업 정보를 불러오지 못했습니다."));
        }
    }

    @GetMapping("/api/detail/{seq}")
    @ResponseBody
    public ResponseEntity<?> supportDetail(@PathVariable String seq) {
        try {
            JsonNode result = supportService.getSupportDetail(seq);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException exception) {
            return ResponseEntity.badRequest().body(Map.of("error", "잘못된 지원사업 번호입니다."));
        } catch (IllegalStateException exception) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(Map.of("error", "지원사업 정보를 불러오지 못했습니다."));
        }
    }
}
