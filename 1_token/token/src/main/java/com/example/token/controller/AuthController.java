package com.example.token.controller;

import com.example.token.model.User;
import com.example.token.util.JwtUtil;

import java.util.ArrayList;
import java.util.List;

import java.util.Map;
import java.util.HashMap;


import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;



@RestController
@RequestMapping("/api")
public class AuthController {

    private List<User> users = new ArrayList<>(); // Geçici hafıza listesi
    private JwtUtil jwtUtil = new JwtUtil();

    @PostMapping("/register")
    public String register(@RequestBody User user) {
        users.add(user);
        return "Kayıt başarılı!";
    }

    // Giriş yaparak token üretme
   @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody User loginUser) {
        for (User user : users) {
            if (user.getEmail().equals(loginUser.getEmail()) &&
                user.getPassword().equals(loginUser.getPassword())) {
                String token = jwtUtil.generateToken(user.getEmail());
                return ResponseEntity.ok(token); // 200 OK ve token döner
            }
        }
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Yanlış");
    }


    // Token doğrulama
    @PostMapping("/validate")
    public ResponseEntity<String> validateToken(@RequestBody Map<String, String> tokenRequest) {
        String token = tokenRequest.get("token"); // "token" parametresinden token'ı alıyoruz
        if (token == null || token.isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Token boş olamaz");
        }
        
        boolean isValid = jwtUtil.validateToken(token);
        if (isValid) {
            return ResponseEntity.ok("Geçerli Token");
        } else {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Geçersiz Token");
        }
    }
}
