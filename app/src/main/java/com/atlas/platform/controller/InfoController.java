package com.atlas.platform.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/info")
@RequiredArgsConstructor
public class InfoController {

    @Value("${spring.profiles.active:default}")
    private String environment;

    @Value("${application.version:1.0.0}")
    private String version;

    @GetMapping
    public ResponseEntity<Map<String, String>> getInfo() {
        Map<String, String> info = Map.of(
                "environment", environment,
                "version", version
        );
        return ResponseEntity.ok(info);
    }
}
