package com.example.token.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;

import java.util.Date;

public class JwtUtil {
    private String secretKey = "meyrameyrameyrameyrameyrameyrame"; // Gerçek projelerde daha güvenli bir anahtar kullanın.

    // Token üretme
    public String generateToken(String email) {
        try {
            Date now = new Date();
            Date expiryDate = new Date(now.getTime() + 60 * 1000); // 1 dakika süre
    
        
            return Jwts.builder()
                    .setSubject(email)
                    .setIssuedAt(now)
                    .setExpiration(expiryDate)
                    .signWith(Keys.hmacShaKeyFor(secretKey.getBytes())) // Key nesnesi ile imzalama
                    .compact();
        } catch (Exception e) {
            e.printStackTrace(); // Hata logunu konsola yazdır
            throw new RuntimeException("Token oluşturulurken bir hata oluştu"); // Hata mesajı
        }
    }

   // Token doğrulama
    public boolean validateToken(String token) {
        try {
            // Token'ı çözümle
            Jws<Claims> claimsJws = Jwts.parserBuilder()
                    .setSigningKey(secretKey.getBytes())
                    .build()
                    .parseClaimsJws(token); // Token'ı çözümleyip doğrulama yapıyoruz

            // Son kullanma tarihini kontrol et
            Date expiration = claimsJws.getBody().getExpiration();
            if (expiration.before(new Date())) {
                System.out.println("Geçersiz Token: Token süresi dolmuş.");
                return false; // Token süresi dolmuşsa geçersiz
            }

            System.out.println("Geçerli Token.");
            return true; // Token geçerli
        } catch (JwtException | IllegalArgumentException e) {
            System.out.println("Geçersiz Token: Hata oluştu - " + e.getMessage());
            e.printStackTrace(); // Hata logunu yazdır
            return false; // Token geçersiz
        }
}


    // Token'dan kullanıcı bilgilerini çıkarma
    public String extractUsername(String token) {
        try{
            return Jwts.parserBuilder()
                    .setSigningKey(secretKey.getBytes()) // Burada da getBytes() ekledik
                    .build()
                    .parseClaimsJws(token)
                    .getBody()
                    .getSubject();
        }
        catch (JwtException | IllegalArgumentException e) {
            e.printStackTrace();  // Hata logunu yazdır
            return null;
        }
    }
}