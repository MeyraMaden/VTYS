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

    @SuppressLint("MissingInflatedId")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mAuth = FirebaseAuth.getInstance();


        editEmail = findViewById(R.id.editEmail);
        EditPassword = findViewById(R.id.editPassword);
        btnKayitOl = findViewById(R.id.btnKayitOl);
        btnGirisYap = findViewById(R.id.btnGirisYap);

        btnGirisYap.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                girisYap(editEmail.getText().toString(), EditPassword.getText().toString());
            }
        });

        btnKayitOl.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                kayitOl(editEmail.getText().toString(), EditPassword.getText().toString());
            }
        });


    }

    @Override
    public void onStart(){
        super.onStart();
        FirebaseUser currentUser=mAuth.getCurrentUser();
    }
}