package com.smhrd.deulmaru.controller;

import com.smhrd.deulmaru.service.CropScheduleService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/crop-schedule")
public class CropScheduleController {

    private final CropScheduleService cropScheduleService;

    public CropScheduleController(CropScheduleService cropScheduleService) {
        this.cropScheduleService = cropScheduleService;
    }

    // 예: /api/crop-schedule?cropName=가지
    @GetMapping("")
    public ResponseEntity<?> getCropSchedule(@RequestParam String cropName) {
        String scheduleHtml = cropScheduleService.getCropSchedule(cropName);
        if (scheduleHtml == null) {
            return ResponseEntity.status(404).body("선택한 작물에 해당하는 일정 정보를 찾을 수 없습니다.");
        }
        return ResponseEntity.ok()
                .header("Content-Type", "text/html; charset=UTF-8")
                .body(scheduleHtml);
    }
}
