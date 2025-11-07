package com.example.fakemodmenu;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_OVERLAY_PERMISSION = 1;
    private Button launchButton;
    private Button stopButton;
    private TextView statusText;
    private boolean isServiceRunning = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        launchButton = findViewById(R.id.launchButton);
        stopButton = findViewById(R.id.stopButton);
        statusText = findViewById(R.id.statusText);

        launchButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    if (!Settings.canDrawOverlays(MainActivity.this)) {
                        Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:" + getPackageName()));
                        startActivityForResult(intent, REQUEST_OVERLAY_PERMISSION);
                    } else {
                        startOverlayService();
                    }
                } else {
                    startOverlayService();
                }
            }
        });

        stopButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopOverlayService();
            }
        });
    }

    private void startOverlayService() {
        Intent intent = new Intent(this, OverlayService.class);
        startService(intent);
        isServiceRunning = true;
        statusText.setText("Статус: Запущен");
        Toast.makeText(this, "Мод меню запущено!", Toast.LENGTH_SHORT).show();
    }

    private void stopOverlayService() {
        Intent intent = new Intent(this, OverlayService.class);
        stopService(intent);
        isServiceRunning = false;
        statusText.setText("Статус: Остановлен");
        Toast.makeText(this, "Мод меню остановлено!", Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_OVERLAY_PERMISSION) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                if (Settings.canDrawOverlays(this)) {
                    startOverlayService();
                } else {
                    Toast.makeText(this, getString(R.string.permission_required), 
                            Toast.LENGTH_LONG).show();
                }
            }
        }
    }
}
