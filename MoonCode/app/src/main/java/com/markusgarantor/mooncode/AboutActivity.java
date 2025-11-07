package com.markusgarantor.mooncode;

import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class AboutActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_about);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        TextView aboutText = findViewById(R.id.aboutText);
        aboutText.setText(getAboutInfo());
    }

    private String getAboutInfo() {
        return "🌙 MoonCode\n\n" +
               "Версия: 1.0\n\n" +
               "Разработчик: @MarkusGarantor\n\n" +
               "Описание:\n" +
               "MoonCode - это мощный редактор кода для создания и редактирования Lua скриптов " +
               "для San Andreas Multiplayer с поддержкой Moonloader.\n\n" +
               "Возможности:\n" +
               "✓ Редактирование Lua кода\n" +
               "✓ Сохранение файлов\n" +
               "✓ Компиляция в Luac\n" +
               "✓ Форматирование кода\n" +
               "✓ Файловый менеджер\n" +
               "✓ Темная/светлая тема\n" +
               "✓ Автосохранение\n" +
               "✓ Шаблоны кода\n\n" +
               "Для работы скриптов на устройстве Android требуется:\n" +
               "- GTA San Andreas\n" +
               "- SAMP Mobile\n" +
               "- Moonloader\n\n" +
               "© 2024 @MarkusGarantor\n" +
               "Все права защищены.";
    }
}
