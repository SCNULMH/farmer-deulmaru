package com.smhrd.deulmaru.service;

import com.smhrd.deulmaru.entity.IdentiEntity;
import com.smhrd.deulmaru.repository.IdentiRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class IdentiService {
	@Autowired
    IdentiRepository repository;

    @Value("${file.upload-dir:${user.home}/uploads}")
    private String uploadDir;

    public IdentiService(IdentiRepository repository) {
        this.repository = repository;
    }

    public String storeImage(MultipartFile file, boolean overwrite) throws IOException {
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        String originalFilename = file.getOriginalFilename();
        Path filePath = uploadPath.resolve(originalFilename);
        if (Files.exists(filePath) && !overwrite) {
            throw new IOException("파일이 이미 존재합니다.");
        }

        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
        return originalFilename; // 경로 말고 파일명만 저장
    }
    
    
    public IdentiEntity saveIdentiResult(String userId, String diseaseName, String cropName, double confidenceScore, String imagePath) {
        IdentiEntity entity = new IdentiEntity();
        entity.setUserId(userId);
        entity.setDiseaseName(diseaseName);
        entity.setCropName(cropName);
        entity.setConfidenceScore(confidenceScore);
        entity.setImagePath(imagePath);
        entity.setIdentificationTime(LocalDateTime.now());
        return repository.save(entity);
    }

    //진단이력 불러오기
    public List<IdentiEntity> getHistoryByUserId(String userId) {
        return repository.findByUserIdOrderByIdentificationTimeDesc(userId);
    }

    //진단이력 삭제하기
    public boolean deleteByIdAndUser(Long id, String userId) {
        Optional<IdentiEntity> optional = repository.findById(id);
        if (optional.isPresent()) {
            IdentiEntity entity = optional.get();
            if (entity.getUserId().equals(userId)) {
            	repository.deleteById(id);
                return true;
            }
        }
        return false;
    }

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

}
