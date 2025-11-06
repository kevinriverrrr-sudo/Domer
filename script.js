// Базовые библиотеки для всех скриптов
const BASE_LIBS = `local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8`;

// Карта клавиш для F-клавиш
const KEY_MAP = {
    'F1': 112,
    'F2': 113,
    'F3': 114,
    'F4': 115,
    'F5': 116,
    'F6': 117,
    'F7': 118,
    'F8': 119
};

// Карта цветов для SAMP
const COLOR_MAP = {
    'white': '{FFFFFF}',
    'red': '{FF0000}',
    'green': '{00FF00}',
    'blue': '{0000FF}',
    'yellow': '{FFFF00}',
    'pink': '{FF69B4}'
};

// Функция для экранирования строк Lua
function escapeLuaString(str) {
    return str
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/'/g, "\\'")
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t');
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    const scriptTypeButtons = document.querySelectorAll('.script-type-btn');
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    
    let currentScriptType = 'flooder';
    
    // Переключение типов скриптов
    scriptTypeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            scriptTypeButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentScriptType = this.dataset.type;
            showSettings(currentScriptType);
            generateScript();
        });
    });
    
    // Показ соответствующих настроек
    function showSettings(type) {
        document.querySelectorAll('.settings-group').forEach(group => {
            group.classList.add('hidden');
        });
        
        const settingsId = type + '-settings';
        const settingsGroup = document.getElementById(settingsId);
        if (settingsGroup) {
            settingsGroup.classList.remove('hidden');
        }
    }
    
    // Генерация скрипта
    function generateScript() {
        let script = BASE_LIBS + '\n\n';
        
        switch(currentScriptType) {
            case 'flooder':
                script += generateFlooderScript();
                break;
            case 'advert':
                script += generateAdvertScript();
                break;
            case 'auto-answer':
                script += generateAutoAnswerScript();
                break;
            case 'spam-protection':
                script += generateSpamProtectionScript();
                break;
            case 'custom':
                script += generateCustomScript();
                break;
        }
        
        document.getElementById('generated-code').textContent = script;
    }
    
    // Генератор флудера
    function generateFlooderScript() {
        const messages = document.getElementById('flood-messages').value.split('\n').filter(m => m.trim());
        const delay = parseInt(document.getElementById('flood-delay').value) || 1000;
        const key = document.getElementById('flood-key').value;
        const keyCode = KEY_MAP[key];
        
        if (messages.length === 0) {
            return '-- Ошибка: Введите хотя бы одно сообщение для флуда';
        }
        
        const messagesArray = messages.map(m => `    "${escapeLuaString(m.trim())}"`).join(',\n');
        
        return `-- Флудер скрипт
local messages = {
${messagesArray}
}
local currentIndex = 1
local isFlooding = false
local delay = ${delay}

function main()
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand('flood', function()
        isFlooding = not isFlooding
        if isFlooding then
            sampAddChatMessage('{00FF00}Флудер активирован', -1)
        else
            sampAddChatMessage('{FF0000}Флудер деактивирован', -1)
        end
    end)
    
    while true do
        wait(0)
        if isFlooding then
            if currentIndex > #messages then
                currentIndex = 1
            end
            sampSendChat(messages[currentIndex])
            currentIndex = currentIndex + 1
            wait(delay)
        end
    end
end`;
    }
    
    // Генератор пиара/рекламы
    function generateAdvertScript() {
        const message = document.getElementById('advert-message').value.trim();
        const interval = parseInt(document.getElementById('advert-interval').value) || 60;
        const color = COLOR_MAP[document.getElementById('advert-color').value] || '{FFFFFF}';
        const autostart = document.getElementById('advert-autostart').checked;
        
        if (!message) {
            return '-- Ошибка: Введите рекламное сообщение';
        }
        
        const coloredMessage = color + escapeLuaString(message);
        const startCondition = autostart ? 'true' : 'false';
        
        return `-- Пиар/Реклама скрипт
local advertMessage = "${coloredMessage}"
local interval = ${interval * 1000} -- в миллисекундах
local isActive = ${startCondition}
local lastSendTime = 0

function main()
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand('advert', function()
        isActive = not isActive
        if isActive then
            sampAddChatMessage('{00FF00}Реклама активирована', -1)
        else
            sampAddChatMessage('{FF0000}Реклама деактивирована', -1)
        end
    end)
    
    while true do
        wait(0)
        if isActive then
            local currentTime = os.clock() * 1000
            if currentTime - lastSendTime >= interval then
                sampSendChat(advertMessage)
                lastSendTime = currentTime
            end
        end
    end
end`;
    }
    
    // Генератор автоответчика
    function generateAutoAnswerScript() {
        const keywords = document.getElementById('answer-keywords').value.split('\n').filter(k => k.trim());
        const answer = document.getElementById('answer-text').value.trim();
        const caseInsensitive = document.getElementById('answer-case-insensitive').checked;
        
        if (keywords.length === 0 || !answer) {
            return '-- Ошибка: Введите ключевые слова и ответ';
        }
        
        const keywordsArray = keywords.map(k => {
            const escapedKeyword = escapeLuaString(k.trim());
            return `    "${escapedKeyword}"`;
        }).join(',\n');
        
        const checkFunction = caseInsensitive ? 
            `local function containsKeyword(text)
    local lowerText = string.lower(text)
    for _, keyword in ipairs(keywords) do
        if string.find(lowerText, string.lower(keyword), 1, true) then
            return true
        end
    end
    return false
end` :
            `local function containsKeyword(text)
    for _, keyword in ipairs(keywords) do
        if string.find(text, keyword, 1, true) then
            return true
        end
    end
    return false
end`;
        
        return `-- Автоответчик скрипт
local keywords = {
${keywordsArray}
}
local answerMessage = "${escapeLuaString(answer)}"
local caseInsensitive = ${caseInsensitive}

${checkFunction}

function main()
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand('autoanswer', function()
        isActive = not isActive
        if isActive then
            sampAddChatMessage('{00FF00}Автоответчик активирован', -1)
        else
            sampAddChatMessage('{FF0000}Автоответчик деактивирован', -1)
        end
    end)
    
    local isActive = true
    
    se.onShowDialog = function(dialogId, style, title, button1, button2, text)
        -- Обработка диалогов если нужно
    end
    
    se.onServerMessage = function(color, text)
        if isActive and text and containsKeyword(text) then
            wait(500) -- Небольшая задержка перед ответом
            sampSendChat(answerMessage)
        end
    end
    
    se.onChatMessage = function(playerId, text)
        if isActive and text and containsKeyword(text) then
            wait(500) -- Небольшая задержка перед ответом
            sampSendChat(answerMessage)
        end
    end
    
    while true do
        wait(0)
    end
end`;
    }
    
    // Генератор защиты от спама
    function generateSpamProtectionScript() {
        const limit = parseInt(document.getElementById('spam-limit').value) || 3;
        const blockTime = parseInt(document.getElementById('spam-block-time').value) || 30;
        const blockMessage = escapeLuaString(document.getElementById('spam-block-message').value.trim());
        
        return `-- Защита от спама скрипт
local maxMessagesPerSecond = ${limit}
local blockTime = ${blockTime} * 1000 -- в миллисекундах
local blockMessage = "${blockMessage}"
local messageHistory = {}
local isBlocked = false
local blockEndTime = 0

local function cleanOldMessages()
    local currentTime = os.clock() * 1000
    for i = #messageHistory, 1, -1 do
        if currentTime - messageHistory[i] > 1000 then
            table.remove(messageHistory, i)
        end
    end
end

local function checkSpam()
    local currentTime = os.clock() * 1000
    
    if isBlocked then
        if currentTime >= blockEndTime then
            isBlocked = false
            sampAddChatMessage('{00FF00}Блокировка снята', -1)
        else
            return true
        end
    end
    
    cleanOldMessages()
    
    if #messageHistory >= maxMessagesPerSecond then
        isBlocked = true
        blockEndTime = currentTime + blockTime
        sampAddChatMessage('{FF0000}' .. blockMessage, -1)
        return true
    end
    
    table.insert(messageHistory, currentTime)
    return false
end

function main()
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand('spamprotect', function()
        isBlocked = false
        messageHistory = {}
        sampAddChatMessage('{00FF00}Защита от спама сброшена', -1)
    end)
    
    -- Перехват отправки сообщений
    local originalSendChat = sampSendChat
    sampSendChat = function(text)
        if not checkSpam() then
            originalSendChat(text)
        end
    end
    
    while true do
        wait(0)
    end
end`;
    }
    
    // Генератор кастомного скрипта
    function generateCustomScript() {
        const customCode = document.getElementById('custom-code').value.trim();
        
        if (!customCode) {
            return BASE_LIBS + '\n\n-- Введите ваш кастомный код выше';
        }
        
        // Если пользователь уже включил базовые библиотеки, не дублируем
        if (customCode.includes("require 'mimgui'") || customCode.includes('require "mimgui"')) {
            return customCode;
        }
        
        return BASE_LIBS + '\n\n' + customCode;
    }
    
    // Обработчики событий для автоматической генерации при изменении настроек
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('input', generateScript);
        input.addEventListener('change', generateScript);
    });
    
    // Кнопка генерации
    generateBtn.addEventListener('click', generateScript);
    
    // Кнопка копирования
    copyBtn.addEventListener('click', function() {
        const code = document.getElementById('generated-code').textContent;
        navigator.clipboard.writeText(code).then(() => {
            showToast('✅ Скрипт скопирован в буфер обмена!');
        }).catch(() => {
            // Fallback для старых браузеров
            const textarea = document.createElement('textarea');
            textarea.value = code;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('✅ Скрипт скопирован!');
        });
    });
    
    // Кнопка скачивания
    downloadBtn.addEventListener('click', function() {
        const code = document.getElementById('generated-code').textContent;
        const scriptType = currentScriptType;
        const filename = `script_${scriptType}_${Date.now()}.lua`;
        
        const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('💾 Скрипт скачан!');
    });
    
    // Функция показа уведомлений
    function showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    // Первоначальная генерация
    generateScript();
});
