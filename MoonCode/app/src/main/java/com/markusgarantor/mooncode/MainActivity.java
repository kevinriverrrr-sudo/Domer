package com.markusgarantor.mooncode;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.Settings;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.EditText;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import java.io.*;

public class MainActivity extends AppCompatActivity {
    private EditText codeEditor;
    private String currentFilePath = null;
    private static final int STORAGE_PERMISSION_CODE = 100;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Apply theme
        prefs = getSharedPreferences("MoonCodePrefs", MODE_PRIVATE);
        boolean isDarkTheme = prefs.getBoolean("dark_theme", true);
        AppCompatDelegate.setDefaultNightMode(
            isDarkTheme ? AppCompatDelegate.MODE_NIGHT_YES : AppCompatDelegate.MODE_NIGHT_NO
        );

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        setSupportActionBar(findViewById(R.id.toolbar));

        codeEditor = findViewById(R.id.codeEditor);
        FloatingActionButton fabSave = findViewById(R.id.fabSave);
        FloatingActionButton fabCompile = findViewById(R.id.fabCompile);
        FloatingActionButton fabNew = findViewById(R.id.fabNew);
        FloatingActionButton fabOpen = findViewById(R.id.fabOpen);

        checkPermissions();

        // Set default Lua template
        if (savedInstanceState == null && codeEditor.getText().toString().isEmpty()) {
            codeEditor.setText(getDefaultLuaTemplate());
        }

        fabNew.setOnClickListener(v -> newFile());
        fabOpen.setOnClickListener(v -> openFileManager());
        fabSave.setOnClickListener(v -> saveFile());
        fabCompile.setOnClickListener(v -> compileToLuac());
    }

    private String getDefaultLuaTemplate() {
        return "-- MoonCode Editor\n" +
               "-- Created by @MarkusGarantor\n" +
               "-- San Andreas Multiplayer Lua Moonloader\n\n" +
               "script_name('MyScript')\n" +
               "script_author('@MarkusGarantor')\n" +
               "script_version('1.0')\n\n" +
               "function main()\n" +
               "    if not isSampLoaded() or not isSampfuncsLoaded() then return end\n" +
               "    while not isSampAvailable() do wait(100) end\n\n" +
               "    sampAddChatMessage('Скрипт загружен!', -1)\n\n" +
               "    while true do\n" +
               "        wait(0)\n" +
               "        -- Ваш код здесь\n" +
               "    end\n" +
               "end\n";
    }

    private void checkPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                try {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                    startActivity(intent);
                } catch (Exception e) {
                    Toast.makeText(this, "Необходимо разрешение на доступ к файлам", Toast.LENGTH_LONG).show();
                }
            }
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE,
                                Manifest.permission.READ_EXTERNAL_STORAGE},
                        STORAGE_PERMISSION_CODE);
            }
        }
    }

    private void newFile() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Новый файл");
        builder.setMessage("Создать новый файл? Несохраненные изменения будут потеряны.");
        builder.setPositiveButton("Да", (dialog, which) -> {
            currentFilePath = null;
            codeEditor.setText(getDefaultLuaTemplate());
            Toast.makeText(this, "Новый файл создан", Toast.LENGTH_SHORT).show();
        });
        builder.setNegativeButton("Отмена", null);
        builder.show();
    }

    private void openFileManager() {
        Intent intent = new Intent(this, FileManagerActivity.class);
        startActivityForResult(intent, 200);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 200 && resultCode == RESULT_OK && data != null) {
            String filePath = data.getStringExtra("filePath");
            if (filePath != null) {
                loadFile(filePath);
            }
        }
    }

    private void loadFile(String filePath) {
        try {
            File file = new File(filePath);
            BufferedReader br = new BufferedReader(new FileReader(file));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line).append("\n");
            }
            br.close();
            codeEditor.setText(sb.toString());
            currentFilePath = filePath;
            Toast.makeText(this, "Файл загружен: " + file.getName(), Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(this, "Ошибка загрузки файла: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void saveFile() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Сохранить файл");
        
        final EditText input = new EditText(this);
        input.setHint("имя_файла.lua");
        if (currentFilePath != null) {
            input.setText(new File(currentFilePath).getName());
        }
        builder.setView(input);

        builder.setPositiveButton("Сохранить", (dialog, which) -> {
            String fileName = input.getText().toString().trim();
            if (fileName.isEmpty()) {
                Toast.makeText(this, "Введите имя файла", Toast.LENGTH_SHORT).show();
                return;
            }
            if (!fileName.endsWith(".lua")) {
                fileName += ".lua";
            }
            saveFileToStorage(fileName);
        });
        builder.setNegativeButton("Отмена", null);
        builder.show();
    }

    private void saveFileToStorage(String fileName) {
        try {
            File dir = new File(Environment.getExternalStorageDirectory(), "MoonCode");
            if (!dir.exists()) {
                dir.mkdirs();
            }
            File file = new File(dir, fileName);
            FileWriter writer = new FileWriter(file);
            writer.write(codeEditor.getText().toString());
            writer.close();
            currentFilePath = file.getAbsolutePath();
            Toast.makeText(this, "Файл сохранен: " + file.getAbsolutePath(), Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(this, "Ошибка сохранения: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void compileToLuac() {
        if (currentFilePath == null || codeEditor.getText().toString().isEmpty()) {
            Toast.makeText(this, "Сначала сохраните файл", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            // Save current content first
            File sourceFile = new File(currentFilePath);
            FileWriter writer = new FileWriter(sourceFile);
            writer.write(codeEditor.getText().toString());
            writer.close();

            // Compile to luac
            String luacPath = currentFilePath.replace(".lua", ".luac");
            boolean success = LuaCompiler.compile(this, currentFilePath, luacPath);
            
            if (success) {
                Toast.makeText(this, "Скомпилировано: " + luacPath, Toast.LENGTH_LONG).show();
            } else {
                Toast.makeText(this, "Ошибка компиляции", Toast.LENGTH_LONG).show();
            }
        } catch (Exception e) {
            Toast.makeText(this, "Ошибка: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            startActivity(new Intent(this, SettingsActivity.class));
            return true;
        } else if (id == R.id.action_about) {
            startActivity(new Intent(this, AboutActivity.class));
            return true;
        } else if (id == R.id.action_run) {
            runScript();
            return true;
        } else if (id == R.id.action_format) {
            formatCode();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private void runScript() {
        Toast.makeText(this, "Функция запуска скрипта (требуется Moonloader на устройстве)", Toast.LENGTH_SHORT).show();
    }

    private void formatCode() {
        String code = codeEditor.getText().toString();
        String formatted = LuaFormatter.format(code);
        codeEditor.setText(formatted);
        Toast.makeText(this, "Код отформатирован", Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onPause() {
        super.onPause();
        // Auto-save current work
        if (currentFilePath != null && !codeEditor.getText().toString().isEmpty()) {
            prefs.edit().putString("last_code", codeEditor.getText().toString()).apply();
            prefs.edit().putString("last_file", currentFilePath).apply();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Restore last work if editor is empty
        if (codeEditor.getText().toString().isEmpty()) {
            String lastCode = prefs.getString("last_code", null);
            String lastFile = prefs.getString("last_file", null);
            if (lastCode != null) {
                codeEditor.setText(lastCode);
                currentFilePath = lastFile;
            }
        }
    }
}
