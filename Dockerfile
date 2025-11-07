FROM ubuntu:22.04

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    wget \
    unzip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools

RUN mkdir -p ${ANDROID_HOME} && \
    cd ${ANDROID_HOME} && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mkdir -p cmdline-tools && \
    mv cmdline-tools latest && \
    mv latest cmdline-tools/

# Установка Android SDK компонентов
RUN yes | ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager \
    "platform-tools" \
    "platforms;android-33" \
    "build-tools;33.0.0" \
    "cmdline-tools;latest"

# Установка Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

# Копирование файлов проекта
COPY package.json capacitor.config.json ./
COPY dist/ ./dist/
COPY android/ ./android/

# Установка зависимостей
RUN npm install

# Сборка APK
CMD cd android && ./gradlew assembleRelease && \
    cp app/build/outputs/apk/release/app-release.apk /app/lua-script-generator.apk
