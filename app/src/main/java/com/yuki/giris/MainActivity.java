package com.yuki.giris;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

public class MainActivity extends AppCompatActivity {

    private FirebaseAuth mAuth;
    String name, mail;
    boolean emailVerified;
    String uid;

    EditText editEmail, EditPassword;
    Button btnKayitOl, btnGirisYap;

    public void kayitOl(String email, String password){


            mAuth.createUserWithEmailAndPassword(email,password).addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
                @Override
                public void onComplete(@NonNull Task<AuthResult> task) {
                    if(task.isSuccessful()){
                        Log.d("", "createUserWithEmail: success");
                        FirebaseUser user=mAuth.getCurrentUser();

                        if(user!=null){
                            name=user.getDisplayName();
                            mail= user.getEmail();
                            emailVerified=user.isEmailVerified();
                            uid=user.getUid();

                            Intent intent=new Intent(getApplicationContext(),SecondActivity.class);
                            intent.putExtra("name",name);
                            intent.putExtra("mail",mail);
                            intent.putExtra("emailVerified",emailVerified);
                            intent.putExtra("uid",uid);
                            startActivity(intent);
                        }
                    }else{
                        Log.w("", "createUserWithEmail: failure", task.getException());
                        Toast.makeText(MainActivity.this, "Authentication failed.", Toast.LENGTH_SHORT).show();
                    }
                }
            });
    }


    public void girisYap(String email, String password){
        mAuth.signInWithEmailAndPassword(email, password).addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
            @Override
            public void onComplete(@NonNull Task<AuthResult> task) {
                if(task.isSuccessful()){
                    Log.d("","signInWithEmail:success");
                    FirebaseUser user=mAuth.getCurrentUser();

                    if(user!=null){
                        name=user.getDisplayName();
                        mail= user.getEmail();
                        emailVerified=user.isEmailVerified();
                        uid=user.getUid();

                        Intent intent=new Intent(getApplicationContext(),SecondActivity.class);
                        intent.putExtra("name",name);
                        intent.putExtra("mail",mail);
                        intent.putExtra("emailVerified",emailVerified);
                        intent.putExtra("uid",uid);
                        startActivity(intent);
                    }


                }else{
                    Log.d("","signInWithEmail:failure",task.getException());
                    Toast.makeText(MainActivity.this, "Authentication failed.", Toast.LENGTH_SHORT).show();

                }
            }
        });
    }
}