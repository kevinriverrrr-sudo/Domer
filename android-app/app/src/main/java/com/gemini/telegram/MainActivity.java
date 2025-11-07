package com.gemini.telegram;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.UpdatesListener;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.request.SendMessage;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    private static final String GEMINI_API_KEY = "AIzaSyC-u6Of5R3wYfXXie6kwh5yAcyDq1HCNAc";
    private static final String TELEGRAM_BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU";
    private static final String GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY;

    private EditText inputMessage;
    private TextView responseText;
    private TextView statusText;
    private Button sendButton;
    
    private TelegramBot telegramBot;
    private ExecutorService executorService;
    private OkHttpClient httpClient;
    private Handler mainHandler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize views
        inputMessage = findViewById(R.id.inputMessage);
        responseText = findViewById(R.id.responseText);
        statusText = findViewById(R.id.statusText);
        sendButton = findViewById(R.id.sendButton);

        // Initialize components
        executorService = Executors.newFixedThreadPool(2);
        httpClient = new OkHttpClient();
        mainHandler = new Handler(Looper.getMainLooper());

        // Initialize Telegram Bot
        initTelegramBot();

        // Set up send button click listener
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String message = inputMessage.getText().toString().trim();
                if (!message.isEmpty()) {
                    sendToGemini(message);
                } else {
                    Toast.makeText(MainActivity.this, "Please enter a message", Toast.LENGTH_SHORT).show();
                }
            }
        });

        updateStatus("App initialized. Telegram bot running...");
    }

    private void initTelegramBot() {
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    telegramBot = new TelegramBot(TELEGRAM_BOT_TOKEN);
                    
                    // Set up listener for incoming messages
                    telegramBot.setUpdatesListener(updates -> {
                        for (Update update : updates) {
                            if (update.message() != null && update.message().text() != null) {
                                String userMessage = update.message().text();
                                long chatId = update.message().chat().id();
                                
                                // Process message with Gemini
                                processMessageWithGemini(userMessage, chatId);
                            }
                        }
                        return UpdatesListener.CONFIRMED_UPDATES_ALL;
                    });
                    
                    mainHandler.post(() -> updateStatus("Telegram Bot Online ✓"));
                } catch (Exception e) {
                    e.printStackTrace();
                    mainHandler.post(() -> updateStatus("Telegram Bot Error: " + e.getMessage()));
                }
            }
        });
    }

    private void sendToGemini(String message) {
        sendButton.setEnabled(false);
        responseText.setText("Processing with Gemini AI...");
        
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    String response = callGeminiAPI(message);
                    mainHandler.post(() -> {
                        responseText.setText("Gemini Response:\n\n" + response);
                        sendButton.setEnabled(true);
                        inputMessage.setText("");
                    });
                } catch (Exception e) {
                    e.printStackTrace();
                    mainHandler.post(() -> {
                        responseText.setText("Error: " + e.getMessage());
                        sendButton.setEnabled(true);
                    });
                }
            }
        });
    }

    private void processMessageWithGemini(String message, long chatId) {
        executorService.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    String geminiResponse = callGeminiAPI(message);
                    
                    // Send response back to Telegram user
                    SendMessage request = new SendMessage(chatId, geminiResponse);
                    telegramBot.execute(request);
                    
                    mainHandler.post(() -> {
                        updateStatus("Message processed from Telegram user: " + chatId);
                    });
                } catch (Exception e) {
                    e.printStackTrace();
                    try {
                        SendMessage errorMsg = new SendMessage(chatId, "Sorry, I encountered an error: " + e.getMessage());
                        telegramBot.execute(errorMsg);
                    } catch (Exception ex) {
                        ex.printStackTrace();
                    }
                }
            }
        });
    }

    private String callGeminiAPI(String prompt) throws IOException {
        try {
            // Create JSON request body
            JSONObject requestJson = new JSONObject();
            JSONArray contentsArray = new JSONArray();
            JSONObject contentObj = new JSONObject();
            JSONArray partsArray = new JSONArray();
            JSONObject partObj = new JSONObject();
            
            partObj.put("text", prompt);
            partsArray.put(partObj);
            contentObj.put("parts", partsArray);
            contentsArray.put(contentObj);
            requestJson.put("contents", contentsArray);

            RequestBody body = RequestBody.create(
                requestJson.toString(),
                MediaType.parse("application/json; charset=utf-8")
            );

            Request request = new Request.Builder()
                .url(GEMINI_API_URL)
                .post(body)
                .build();

            try (Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    throw new IOException("Unexpected response code: " + response.code());
                }

                String responseBody = response.body().string();
                JSONObject jsonResponse = new JSONObject(responseBody);
                
                // Parse Gemini response
                JSONArray candidates = jsonResponse.getJSONArray("candidates");
                if (candidates.length() > 0) {
                    JSONObject candidate = candidates.getJSONObject(0);
                    JSONObject content = candidate.getJSONObject("content");
                    JSONArray parts = content.getJSONArray("parts");
                    if (parts.length() > 0) {
                        return parts.getJSONObject(0).getString("text");
                    }
                }
                
                return "No response from Gemini";
            }
        } catch (Exception e) {
            e.printStackTrace();
            throw new IOException("Error calling Gemini API: " + e.getMessage());
        }
    }

    private void updateStatus(String status) {
        statusText.setText(status);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (telegramBot != null) {
            telegramBot.removeGetUpdatesListener();
        }
        if (executorService != null) {
            executorService.shutdown();
        }
    }
}
