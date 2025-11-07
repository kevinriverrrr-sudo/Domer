package com.markusgarantor.mooncode;

import android.content.Intent;
import android.os.Bundle;
import android.os.Environment;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class FileManagerActivity extends AppCompatActivity {
    private ListView listView;
    private File currentDir;
    private List<File> files;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_file_manager);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        listView = findViewById(R.id.fileListView);
        
        // Start from MoonCode directory or external storage
        File moonCodeDir = new File(Environment.getExternalStorageDirectory(), "MoonCode");
        if (moonCodeDir.exists() && moonCodeDir.isDirectory()) {
            currentDir = moonCodeDir;
        } else {
            currentDir = Environment.getExternalStorageDirectory();
        }

        loadFiles();

        listView.setOnItemClickListener((parent, view, position, id) -> {
            File selectedFile = files.get(position);
            if (selectedFile.isDirectory()) {
                currentDir = selectedFile;
                loadFiles();
            } else if (selectedFile.getName().endsWith(".lua")) {
                Intent resultIntent = new Intent();
                resultIntent.putExtra("filePath", selectedFile.getAbsolutePath());
                setResult(RESULT_OK, resultIntent);
                finish();
            } else {
                Toast.makeText(this, "Выберите .lua файл", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void loadFiles() {
        files = new ArrayList<>();
        
        // Add parent directory option
        if (currentDir.getParentFile() != null) {
            files.add(currentDir.getParentFile());
        }

        // Add all files and directories
        File[] fileList = currentDir.listFiles();
        if (fileList != null) {
            Arrays.sort(fileList, (f1, f2) -> {
                if (f1.isDirectory() && !f2.isDirectory()) return -1;
                if (!f1.isDirectory() && f2.isDirectory()) return 1;
                return f1.getName().compareToIgnoreCase(f2.getName());
            });
            Collections.addAll(files, fileList);
        }

        FileAdapter adapter = new FileAdapter();
        listView.setAdapter(adapter);
        
        if (getSupportActionBar() != null) {
            getSupportActionBar().setSubtitle(currentDir.getAbsolutePath());
        }
    }

    private class FileAdapter extends ArrayAdapter<File> {
        FileAdapter() {
            super(FileManagerActivity.this, R.layout.file_item, files);
        }

        @NonNull
        @Override
        public View getView(int position, View convertView, @NonNull ViewGroup parent) {
            if (convertView == null) {
                convertView = getLayoutInflater().inflate(R.layout.file_item, parent, false);
            }

            File file = files.get(position);
            TextView nameView = convertView.findViewById(R.id.fileName);
            TextView infoView = convertView.findViewById(R.id.fileInfo);

            if (position == 0 && file.equals(currentDir.getParentFile())) {
                nameView.setText("📁 ..");
                infoView.setText("Назад");
            } else if (file.isDirectory()) {
                nameView.setText("📁 " + file.getName());
                infoView.setText("Папка");
            } else {
                nameView.setText("📄 " + file.getName());
                long size = file.length();
                String sizeStr = size < 1024 ? size + " B" : 
                                 size < 1024*1024 ? (size/1024) + " KB" : 
                                 (size/(1024*1024)) + " MB";
                infoView.setText(sizeStr);
            }

            return convertView;
        }
    }

    @Override
    public void onBackPressed() {
        if (currentDir.getParentFile() != null) {
            currentDir = currentDir.getParentFile();
            loadFiles();
        } else {
            super.onBackPressed();
        }
    }
}
