package com.smhrd.deulmaru.controller;

import com.smhrd.deulmaru.service.NcpmsService;
import org.springframework.http.ResponseEntity;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ncpms")
@CrossOrigin(origins = "*") // CORS 허용
public class NcpmsController {

    private final NcpmsService ncpmsService;

    public NcpmsController(NcpmsService ncpmsService) {
        this.ncpmsService = ncpmsService;
    }
    
    
    
    @GetMapping(value = "/search", produces = "application/xml")
    public ResponseEntity<String> search(@RequestParam String query, @RequestParam(defaultValue = "sick") String type) {
        return ResponseEntity.ok(ncpmsService.search(query, type));
    }

    @GetMapping(value = "/sick_detail", produces = "application/xml")
    public ResponseEntity<String> sickDetail(@RequestParam String sick_key) {
        return ResponseEntity.ok(ncpmsService.getSickDetail(sick_key));
    }

    @GetMapping("/consult")
    public ResponseEntity<String> getConsultData(
            @RequestParam String query,
            @RequestParam(defaultValue = "1") int page
    ) {
        int resultsPerPage = 10;
        int displayCount = 50;
        int startPoint = (page - 1) * resultsPerPage + 1;

        String result = ncpmsService.getConsult(query, startPoint, displayCount);
        return ResponseEntity.ok(result);
    }


    @GetMapping("/consult_detail")
    public ResponseEntity<String> consultDetail(@RequestParam String consult_id) {
        return ResponseEntity.ok(ncpmsService.getConsultDetail(consult_id));
    }
}