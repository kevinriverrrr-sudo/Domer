package com.example.fakemodmenu;

import android.app.Service;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.IBinder;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import androidx.annotation.Nullable;

public class OverlayService extends Service {
    private WindowManager windowManager;
    private View overlayView;
    private LinearLayout contentContainer;
    private String currentTab = "visuals";

    @Override
    public void onCreate() {
        super.onCreate();
        
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        overlayView = LayoutInflater.from(this).inflate(R.layout.overlay_menu, null);

        int layoutFlag;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutFlag = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutFlag = WindowManager.LayoutParams.TYPE_PHONE;
        }

        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                layoutFlag,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);

        params.gravity = Gravity.TOP | Gravity.START;
        params.x = 50;
        params.y = 100;

        windowManager.addView(overlayView, params);

        setupDraggableOverlay(overlayView, params);
        setupButtons();
        showVisualsTab();
    }

    private void setupDraggableOverlay(final View overlay, final WindowManager.LayoutParams params) {
        View header = overlay.findViewById(R.id.hideButton).getParent() instanceof View ? 
                (View) overlay.findViewById(R.id.hideButton).getParent() : overlay;
        
        header.setOnTouchListener(new View.OnTouchListener() {
            private int initialX;
            private int initialY;
            private float initialTouchX;
            private float initialTouchY;

            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        initialX = params.x;
                        initialY = params.y;
                        initialTouchX = event.getRawX();
                        initialTouchY = event.getRawY();
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        params.x = initialX + (int) (event.getRawX() - initialTouchX);
                        params.y = initialY + (int) (event.getRawY() - initialTouchY);
                        windowManager.updateViewLayout(overlayView, params);
                        return true;
                }
                return false;
            }
        });
    }

    private void setupButtons() {
        contentContainer = overlayView.findViewById(R.id.contentContainer);
        
        Button hideButton = overlayView.findViewById(R.id.hideButton);
        hideButton.setOnClickListener(v -> {
            overlayView.setVisibility(overlayView.getVisibility() == View.VISIBLE ? 
                    View.GONE : View.VISIBLE);
        });

        Button tabVisuals = overlayView.findViewById(R.id.tabVisuals);
        Button tabAimBot = overlayView.findViewById(R.id.tabAimBot);
        Button tabMisc = overlayView.findViewById(R.id.tabMisc);
        Button tabPlayer = overlayView.findViewById(R.id.tabPlayer);
        Button tabSettings = overlayView.findViewById(R.id.tabSettings);

        tabVisuals.setOnClickListener(v -> showVisualsTab());
        tabAimBot.setOnClickListener(v -> showAimBotTab());
        tabMisc.setOnClickListener(v -> showMiscTab());
        tabPlayer.setOnClickListener(v -> showPlayerTab());
        tabSettings.setOnClickListener(v -> showSettingsTab());
    }

    private void showVisualsTab() {
        currentTab = "visuals";
        contentContainer.removeAllViews();
        
        addFeatureSwitch("ESP Box", "Показывает коробки вокруг игроков");
        addFeatureSwitch("ESP Name", "Показывает имена игроков");
        addFeatureSwitch("ESP Health", "Показывает здоровье игроков");
        addFeatureSwitch("ESP Distance", "Показывает дистанцию до игроков");
        addFeatureSwitch("ESP Line", "Рисует линии к игрокам");
        addFeatureSwitch("Skeleton ESP", "Показывает скелет игроков");
        addFeatureSwitch("Crosshair", "Кастомный прицел");
        addFeatureSwitch("FOV Circle", "Круг обзора");
        addFeatureSwitch("Night Mode", "Ночной режим");
        addFeatureSwitch("No Flash", "Убирает ослепление");
        addSeekBarFeature("ESP Thickness", 1, 10);
        addSeekBarFeature("ESP Distance Limit", 10, 500);
    }

    private void showAimBotTab() {
        currentTab = "aimbot";
        contentContainer.removeAllViews();
        
        addFeatureSwitch("Enable AimBot", "Включает автонаведение");
        addFeatureSwitch("Auto Shoot", "Автоматическая стрельба");
        addFeatureSwitch("Silent Aim", "Незаметное наведение");
        addFeatureSwitch("Aim at Head", "Наведение на голову");
        addFeatureSwitch("Aim at Body", "Наведение на тело");
        addFeatureSwitch("Ignore Team", "Игнорировать команду");
        addFeatureSwitch("Aim Through Walls", "Наведение через стены");
        addFeatureSwitch("Target Lock", "Блокировка цели");
        addSeekBarFeature("AimBot FOV", 1, 360);
        addSeekBarFeature("AimBot Smooth", 1, 100);
        addSeekBarFeature("AimBot Speed", 1, 100);
        addSeekBarFeature("Max Distance", 10, 500);
    }

    private void showMiscTab() {
        currentTab = "misc";
        contentContainer.removeAllViews();
        
        addFeatureSwitch("Speed Hack", "Увеличивает скорость передвижения");
        addFeatureSwitch("No Recoil", "Убирает отдачу оружия");
        addFeatureSwitch("No Spread", "Убирает разброс");
        addFeatureSwitch("Fast Reload", "Быстрая перезарядка");
        addFeatureSwitch("Infinite Ammo", "Бесконечные патроны");
        addFeatureSwitch("Rapid Fire", "Быстрая стрельба");
        addFeatureSwitch("Jump Hack", "Высокие прыжки");
        addFeatureSwitch("Fly Mode", "Режим полета");
        addFeatureSwitch("Teleport", "Телепортация");
        addFeatureSwitch("Anti Ban", "Защита от бана");
        addSeekBarFeature("Speed Multiplier", 1, 10);
        addSeekBarFeature("Jump Height", 1, 20);
    }

    private void showPlayerTab() {
        currentTab = "player";
        contentContainer.removeAllViews();
        
        addFeatureSwitch("God Mode", "Бессмертие");
        addFeatureSwitch("Infinite Health", "Бесконечное здоровье");
        addFeatureSwitch("Infinite Armor", "Бесконечная броня");
        addFeatureSwitch("Auto Heal", "Автоматическое лечение");
        addFeatureSwitch("Super Damage", "Увеличенный урон");
        addFeatureSwitch("One Shot Kill", "Убийство с одного выстрела");
        addFeatureSwitch("No Fall Damage", "Нет урона от падения");
        addFeatureSwitch("No Fire Damage", "Нет урона от огня");
        addFeatureSwitch("Stealth Mode", "Режим невидимости");
        addSeekBarFeature("Health Amount", 0, 1000);
        addSeekBarFeature("Armor Amount", 0, 1000);
        addSeekBarFeature("Damage Multiplier", 1, 50);
    }

    private void showSettingsTab() {
        currentTab = "settings";
        contentContainer.removeAllViews();
        
        addFeatureSwitch("Show FPS", "Показывать FPS");
        addFeatureSwitch("Show Ping", "Показывать пинг");
        addFeatureSwitch("Panic Button", "Кнопка паники (скрывает все)");
        addFeatureSwitch("Save Config", "Сохранять конфигурацию");
        addFeatureSwitch("Auto Update", "Автоматическое обновление");
        addSeekBarFeature("Menu Opacity", 10, 100);
        addSeekBarFeature("Font Size", 8, 24);
        
        addInfoText("\n⚠️ ВНИМАНИЕ ⚠️\n\nЭто демонстрационное приложение!\nВсе функции НЕ работают.\n\nСоздано только в образовательных целях.");
    }

    private void addFeatureSwitch(String title, String description) {
        LinearLayout item = new LinearLayout(this);
        item.setOrientation(LinearLayout.VERTICAL);
        item.setPadding(16, 12, 16, 12);
        
        LinearLayout headerLayout = new LinearLayout(this);
        headerLayout.setOrientation(LinearLayout.HORIZONTAL);
        
        LinearLayout textLayout = new LinearLayout(this);
        textLayout.setOrientation(LinearLayout.VERTICAL);
        textLayout.setLayoutParams(new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        
        TextView titleText = new TextView(this);
        titleText.setText(title);
        titleText.setTextColor(0xFFFFFFFF);
        titleText.setTextSize(16);
        titleText.setTypeface(null, android.graphics.Typeface.BOLD);
        
        TextView descText = new TextView(this);
        descText.setText(description);
        descText.setTextColor(0xFFCCCCCC);
        descText.setTextSize(12);
        
        textLayout.addView(titleText);
        textLayout.addView(descText);
        
        Switch toggle = new Switch(this);
        toggle.setOnCheckedChangeListener((buttonView, isChecked) -> {
            // Non-functional - just visual feedback
        });
        
        headerLayout.addView(textLayout);
        headerLayout.addView(toggle);
        item.addView(headerLayout);
        
        View divider = new View(this);
        divider.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1));
        divider.setBackgroundColor(0xFF444444);
        item.addView(divider);
        
        contentContainer.addView(item);
    }

    private void addSeekBarFeature(String title, int min, int max) {
        LinearLayout item = new LinearLayout(this);
        item.setOrientation(LinearLayout.VERTICAL);
        item.setPadding(16, 12, 16, 12);
        
        TextView titleText = new TextView(this);
        titleText.setText(title + ": " + min);
        titleText.setTextColor(0xFFFFFFFF);
        titleText.setTextSize(14);
        titleText.setTypeface(null, android.graphics.Typeface.BOLD);
        
        SeekBar seekBar = new SeekBar(this);
        seekBar.setMax(max - min);
        seekBar.setProgress(0);
        seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                titleText.setText(title + ": " + (min + progress));
            }
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });
        
        item.addView(titleText);
        item.addView(seekBar);
        
        View divider = new View(this);
        divider.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1));
        divider.setBackgroundColor(0xFF444444);
        item.addView(divider);
        
        contentContainer.addView(item);
    }

    private void addInfoText(String text) {
        TextView infoText = new TextView(this);
        infoText.setText(text);
        infoText.setTextColor(0xFFFF5555);
        infoText.setTextSize(14);
        infoText.setTypeface(null, android.graphics.Typeface.BOLD);
        infoText.setPadding(16, 24, 16, 24);
        infoText.setGravity(Gravity.CENTER);
        
        contentContainer.addView(infoText);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (overlayView != null) {
            windowManager.removeView(overlayView);
        }
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
