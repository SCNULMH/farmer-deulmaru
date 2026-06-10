package com.smhrd.deulmaru.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.HashMap;
import java.util.Map;

@Controller
public class FileUploadController {

    // 기존 프로퍼티 사용 (upload.path)
    @Value("${upload.path}")
    private String uploadDir;

    @Value("${predict.script.path}")
    private String pythonScriptPath;

    @Value("${python.interpreter.path}")
    private String pythonInterpreterPath;

    /**
     * 파일 업로드 및 예측 실행 (작물명 포함)
     * 클라이언트에서 file과 함께 cropName을 전달받습니다.
     */
    @PostMapping("/upload")
    @ResponseBody
    public Map<String, String> uploadImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam("cropName") String cropName
    ) {
        Map<String, String> response = new HashMap<>();

        if (file.isEmpty()) {
            response.put("message", "🚨 파일이 선택되지 않았습니다.");
            return response;
        }

        try {
            // uploadDir가 절대경로가 아니라면 현재 사용자 홈 디렉터리를 기준으로 변환
            Path path = Paths.get(uploadDir);
            if (!path.isAbsolute()) {
                path = Paths.get(System.getProperty("user.dir"), uploadDir);
            }
            if (!Files.exists(path)) {
                Files.createDirectories(path);
            }

            // 업로드된 파일 저장
            String filename = file.getOriginalFilename();
            Path filePath = path.resolve(filename);
            Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);


            // Python 스크립트 실행 (작물명과 파일 경로를 전달)
            String predictionResult = predictImage(pythonScriptPath, cropName, filePath.toString());

            response.put("prediction", predictionResult);
            response.put("imageUrl", "/uploads/" + filename);

        } catch (IOException e) {
            response.put("message", "🚨 파일 업로드 오류: " + e.getMessage());
        }

        return response;
    }

    /**
     * predict.py 스크립트를 실행하여 예측 결과를 얻습니다.
     * 인자 순서는: cropName, imagePath
     */
    private String predictImage(String scriptPath, String cropName, String imagePath) {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(
                    pythonInterpreterPath,
                    scriptPath,
                    cropName,
                    imagePath
            );

            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            return output.toString().trim();

        } catch (IOException e) {
            return "예측 실패: " + e.getMessage();
        }
    }
}
