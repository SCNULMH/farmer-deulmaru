package com.smhrd.deulmaru.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/supportApi")
public class SupportController {

	@Value("${api.serviceKey}")
	private String apiServiceKey;

	@GetMapping("/support")
	public String grantsPage(Model model) {
		model.addAttribute("serviceKey", apiServiceKey); // 뷰에서 사용하기 위해 추가
		return "supportApi/support"; // templates/support.html 반환
	}

	@GetMapping("/detail/{seq}")
	public String grantDetailPage(@PathVariable String seq, Model model) {
		model.addAttribute("seq", seq);
		model.addAttribute("serviceKey", apiServiceKey); // 뷰에서 사용하기 위해 추가
		return "supportApi/support-detail"; // templates/support-detail.html 반환
	}
}
