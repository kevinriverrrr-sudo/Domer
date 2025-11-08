script_name("Police Helper Monetloader")
script_author("Assistant")
script_version("2.0")
script_properties('work-in-pause')

-- ============================================================================
-- БИБЛИОТЕКИ ДЛЯ MONETLOADER (MOBILE)
-- ============================================================================
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

-- JSON конфигурация для сохранения настроек
local effil = require 'effil'
local inicfg = require 'inicfg'

-- ============================================================================
-- КОНФИГУРАЦИЯ
-- ============================================================================
local directIni = 'moonloader/config/PoliceHelperMobile.ini'
local ini = inicfg.load({
    config = {
        showMenu = false,
        currentMenu = 1,
        autoSave = true,
        notifications = true,
        autoGreet = false,
        menuPosX = 100,
        menuPosY = 100,
        menuAlpha = 200
    },
    lastUsed = {
        playerId = "",
        wantedLevel = "",
        crimeReason = ""
    },
    colors = {
        main = 0x00BFFF,
        success = 0x00FF00,
        error = 0xFF0000,
        warning = 0xFFFF00
    }
}, directIni)

if not doesFileExist(directIni) then
    inicfg.save(ini, directIni)
end

-- ============================================================================
-- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
-- ============================================================================
local showMainMenu = false
local selectedMenu = 1  -- 1=Биндер, 2=Коды, 3=Быстрые, 4=Настройки, 5=Инфо
local selectedBind = 0
local selectedCrime = 0

-- Поля ввода
local input = {
    id = "",
    name = "",
    rank = "",
    vehicle = "",
    color = "",
    number = "",
    location = "",
    stars = "",
    reason = "",
    fine = "",
    time = ""
}

-- Временные переменные для диалогов
local showInputDialog = false
local currentInputType = ""
local inputBuffer = ""

-- ============================================================================
-- БИНДЕР КОМАНД
-- ============================================================================
local binds = {
    {
        id = 1,
        name = "Приветствие с бейджем",
        cmd = "/do На груди висит бейдж '{name}' | {rank}",
        params = {"name", "rank"},
        icon = "??",
        enabled = true
    },
    {
        id = 2,
        name = "Показать удостоверение",
        cmd = "/me достал удостоверение из кармана\\n/do Удостоверение в руке\\n/showbadge {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 3,
        name = "Надеть наручники",
        cmd = "/me взял наручники с пояса\\n/me надел наручники на руки человека\\n/cuff {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 4,
        name = "Снять наручники",
        cmd = "/me достал ключ от наручников\\n/me снял наручники с рук\\n/uncuff {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 5,
        name = "Обыскать",
        cmd = "/me начал обыскивать человека\\n/frisk {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 6,
        name = "Изъять оружие",
        cmd = "/me изъял оружие у человека\\n/takegun {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 7,
        name = "Изъять наркотики",
        cmd = "/me изъял наркотики\\n/takedrugs {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 8,
        name = "Посадить в автомобиль",
        cmd = "/me открыл дверь автомобиля\\n/me посадил человека в автомобиль\\n/pull {id}",
        params = {"id"},
        icon = "??",
        enabled = true
    },
    {
        id = 9,
        name = "Объявить погоню",
        cmd = "/m Всем постам! Объявлена погоня! {vehicle} {color}! Номер: {number}!",
        params = {"vehicle", "color", "number"},
        icon = "??",
        enabled = true
    },
    {
        id = 10,
        name = "Запросить подкрепление",
        cmd = "/r Запрашиваю подкрепление! Локация: {location}",
        params = {"location"},
        icon = "??",
        enabled = true
    },
    {
        id = 11,
        name = "Прочитать права",
        cmd = "/me начал зачитывать права\\n/do 'Вы имеете право хранить молчание...'\\n/todo продолжил зачитывание*закончил",
        params = {},
        icon = "??",
        enabled = true
    },
    {
        id = 12,
        name = "Проверить документы",
        cmd = "/me попросил предъявить документы\\n/do Жду ответа",
        params = {},
        icon = "??",
        enabled = true
    }
}

-- ============================================================================
-- КОДЫ ПРАВОНАРУШЕНИЙ
-- ============================================================================
local crimes = {
    {code = "01", name = "Угон транспортного средства", stars = 2, fine = 1000, time = 30},
    {code = "02", name = "Ограбление гражданина", stars = 3, fine = 2000, time = 45},
    {code = "03", name = "Ограбление бизнеса", stars = 4, fine = 3000, time = 60},
    {code = "04", name = "Ограбление банка", stars = 5, fine = 4000, time = 90},
    {code = "05", name = "Убийство", stars = 6, fine = 5000, time = 120},
    {code = "06", name = "Нападение на офицера", stars = 4, fine = 3500, time = 70},
    {code = "07", name = "Хранение наркотиков", stars = 3, fine = 2500, time = 50},
    {code = "08", name = "Сбыт наркотиков", stars = 4, fine = 3500, time = 80},
    {code = "09", name = "Хулиганство", stars = 1, fine = 500, time = 15},
    {code = "10", name = "Незаконное хранение оружия", stars = 3, fine = 2000, time = 40},
    {code = "11", name = "Терроризм", stars = 6, fine = 6000, time = 150},
    {code = "12", name = "Коррупция", stars = 5, fine = 4500, time = 100},
    {code = "13", name = "Побег из тюрьмы", stars = 4, fine = 3000, time = 60},
    {code = "14", name = "Превышение скорости", stars = 1, fine = 300, time = 0},
    {code = "15", name = "Проезд на красный свет", stars = 1, fine = 200, time = 0},
    {code = "16", name = "Вождение без прав", stars = 2, fine = 800, time = 20},
    {code = "17", name = "Сопротивление аресту", stars = 3, fine = 2200, time = 50},
    {code = "18", name = "Дача взятки", stars = 3, fine = 2500, time = 45}
}

-- ============================================================================
-- БЫСТРЫЕ КОМАНДЫ (10-КОДЫ)
-- ============================================================================
local quickCmds = {
    {name = "10-4 (Принято)", cmd = "/r 10-4", color = 0x00FF00},
    {name = "10-6 (Занят)", cmd = "/r 10-6", color = 0xFFFF00},
    {name = "10-7 (Вне службы)", cmd = "/r 10-7", color = 0xFF8800},
    {name = "10-8 (Свободен)", cmd = "/r 10-8", color = 0x00FF00},
    {name = "10-20 (Локация)", cmd = "/r 10-20", color = 0x00BFFF},
    {name = "10-99 (Помощь!)", cmd = "/r 10-99! СРОЧНО!", color = 0xFF0000},
    {name = "Погоня", cmd = "/m Объявлена погоня!", color = 0xFF0000},
    {name = "Подкрепление", cmd = "/r Нужно подкрепление!", color = 0xFF0000}
}

-- ============================================================================
-- ОСНОВНАЯ ФУНКЦИЯ
-- ============================================================================
function main()
    if not isSampLoaded() or not isSampfuncsLoaded() then return end
    while not isSampAvailable() do wait(100) end
    
    -- Регистрация команд
    sampRegisterChatCommand("mhelper", toggleMenu)
    sampRegisterChatCommand("mh", toggleMenu)
    sampRegisterChatCommand("mph", function() 
        showMainMenu = not showMainMenu 
    end)
    
    -- Команды быстрого доступа
    sampRegisterChatCommand("msu", cmdQuickWanted)      -- /msu [id] [stars] [reason]
    sampRegisterChatCommand("marrest", cmdQuickArrest)  -- /marrest [id]
    
    -- Приветственное сообщение
    sampAddChatMessage("{00BFFF}?????????????????????????????????????????", -1)
    sampAddChatMessage("{00BFFF}?  {FFFFFF}Police Helper Mobile v2.0{00BFFF}         ?", -1)
    sampAddChatMessage("{00BFFF}?  {FFFFFF}Команды: {00FF00}/mhelper, /mh{00BFFF}          ?", -1)
    sampAddChatMessage("{00BFFF}?  {FFFFFF}Быстрый розыск: {00FF00}/msu{00BFFF}            ?", -1)
    sampAddChatMessage("{00BFFF}?  {FFFFFF}Быстрый арест: {00FF00}/marrest{00BFFF}         ?", -1)
    sampAddChatMessage("{00BFFF}?????????????????????????????????????????", -1)
    
    -- Основной цикл
    while true do
        wait(0)
        
        -- Отрисовка меню
        if showMainMenu then
            drawMainMenu()
        end
    end
end

-- ============================================================================
-- КОМАНДЫ
-- ============================================================================

function toggleMenu()
    showMainMenu = not showMainMenu
    if showMainMenu then
        notify("Меню открыто", ini.colors.success)
    end
end

-- Быстрый розыск
function cmdQuickWanted(params)
    local id, stars, reason = params:match("(%d+)%s+(%d+)%s+(.+)")
    if id and stars and reason then
        quickWanted(id, stars, reason)
    else
        notify("Использование: /msu [id] [stars] [reason]", ini.colors.error)
    end
end

-- Быстрый арест
function cmdQuickArrest(params)
    local id = tonumber(params)
    if id then
        -- Используем последние сохранённые данные
        if ini.lastUsed.wantedLevel ~= "" and ini.lastUsed.crimeReason ~= "" then
            quickArrest(id, ini.lastUsed.wantedLevel, ini.lastUsed.crimeReason)
        else
            notify("Сначала используйте /msu для объявления розыска", ini.colors.error)
        end
    else
        notify("Использование: /marrest [id]", ini.colors.error)
    end
end

-- ============================================================================
-- ФУНКЦИИ ОТПРАВКИ КОМАНД
-- ============================================================================

-- Отправка команд с задержкой
function sendBind(bindId)
    local bind = binds[bindId]
    if not bind then return end
    
    local text = bind.cmd
    
    -- Замена параметров
    text = text:gsub("{id}", input.id)
    text = text:gsub("{name}", input.name)
    text = text:gsub("{rank}", input.rank)
    text = text:gsub("{vehicle}", input.vehicle)
    text = text:gsub("{color}", input.color)
    text = text:gsub("{number}", input.number)
    text = text:gsub("{location}", input.location)
    text = text:gsub("{stars}", input.stars)
    text = text:gsub("{reason}", input.reason)
    
    -- Разбить на команды
    local commands = {}
    for cmd in text:gmatch("[^\\n]+") do
        table.insert(commands, cmd)
    end
    
    -- Отправить с задержкой
    lua_thread.create(function()
        for i, cmd in ipairs(commands) do
            sampSendChat(cmd)
            if i < #commands then
                wait(1200)  -- Задержка между командами
            end
        end
        if ini.config.notifications then
            notify("? " .. bind.name, ini.colors.success)
        end
    end)
end

-- Быстрый розыск
function quickWanted(id, stars, reason)
    lua_thread.create(function()
        sampSendChat(string.format("/su %s %s %s", id, stars, reason))
        wait(500)
        
        -- Сохранить для быстрого ареста
        ini.lastUsed.playerId = id
        ini.lastUsed.wantedLevel = stars
        ini.lastUsed.crimeReason = reason
        if ini.config.autoSave then
            inicfg.save(ini, directIni)
        end
        
        notify("? Розыск объявлен!", ini.colors.success)
    end)
end

-- Быстрый арест
function quickArrest(id, stars, reason)
    lua_thread.create(function()
        sampSendChat("/me взял наручники с пояса")
        wait(1200)
        sampSendChat("/me надел наручники на руки подозреваемому")
        wait(1200)
        sampSendChat("/cuff " .. id)
        wait(1500)
        sampSendChat(string.format("/su %s %s %s", id, stars, reason))
        wait(1500)
        sampSendChat("/arrest " .. id)
        wait(500)
        notify("? Арест выполнен успешно!", ini.colors.success)
    end)
end

-- ============================================================================
-- ОТРИСОВКА МЕНЮ
-- ============================================================================

function drawMainMenu()
    local sX, sY = getScreenResolution()
    
    -- Адаптивные размеры для мобильных
    local menuW = math.min(sX - 40, 500)
    local menuH = math.min(sY - 100, 600)
    local menuX = (sX - menuW) / 2
    local menuY = 50
    
    -- Фон меню с тенью
    renderDrawBox(menuX + 3, menuY + 3, menuW, menuH, 0x88000000)
    renderDrawBox(menuX, menuY, menuW, menuH, 0xEE111111)
    
    -- Заголовок
    renderDrawBox(menuX, menuY, menuW, 45, 0xFF0080FF)
    renderDrawText("POLICE HELPER MOBILE", menuX + 15, menuY + 12, 0xFFFFFFFF, 0xFF000000, 2, 0x90000000)
    renderDrawText("v2.0", menuX + menuW - 60, menuY + 25, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    -- Кнопка закрытия
    renderDrawBox(menuX + menuW - 40, menuY + 5, 35, 35, 0xFFFF0000)
    renderDrawText("X", menuX + menuW - 30, menuY + 12, 0xFFFFFFFF, 0xFF000000, 2, 0x90000000)
    
    -- Навигационные табы
    local tabs = {
        {name = "Биндер", icon = "??"},
        {name = "Коды", icon = "??"},
        {name = "Быстрые", icon = "?"},
        {name = "Настройки", icon = "??"},
        {name = "Инфо", icon = "??"}
    }
    
    local tabW = menuW / #tabs
    local tabY = menuY + 50
    
    for i, tab in ipairs(tabs) do
        local tabX = menuX + (i - 1) * tabW
        local bgColor = (selectedMenu == i) and 0xFF0060CC or 0xFF333333
        
        renderDrawBox(tabX, tabY, tabW - 2, 40, bgColor)
        renderDrawText(tab.icon .. " " .. tab.name, tabX + 10, tabY + 12, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    end
    
    -- Контент
    local contentY = tabY + 45
    local contentH = menuH - 100
    
    if selectedMenu == 1 then
        drawBinderMenu(menuX, contentY, menuW, contentH)
    elseif selectedMenu == 2 then
        drawCrimesMenu(menuX, contentY, menuW, contentH)
    elseif selectedMenu == 3 then
        drawQuickMenu(menuX, contentY, menuW, contentH)
    elseif selectedMenu == 4 then
        drawSettingsMenu(menuX, contentY, menuW, contentH)
    elseif selectedMenu == 5 then
        drawInfoMenu(menuX, contentY, menuW, contentH)
    end
end

-- Меню биндера
function drawBinderMenu(x, y, w, h)
    renderDrawText("Доступные действия:", x + 15, y + 10, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    local startY = y + 35
    local btnH = 50
    local spacing = 5
    
    for i = 1, math.min(#binds, 8) do
        local bind = binds[i]
        local btnY = startY + (i - 1) * (btnH + spacing)
        
        -- Кнопка биндапа
        local btnColor = (selectedBind == i) and 0xFF0080FF or 0xFF444444
        renderDrawBox(x + 10, btnY, w - 20, btnH, btnColor)
        
        -- Иконка и название
        renderDrawText(bind.icon, x + 20, btnY + 10, 0xFFFFFFFF, 0xFF000000, 2, 0x90000000)
        renderDrawText(bind.name, x + 55, btnY + 12, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
        
        -- Параметры
        if #bind.params > 0 then
            local paramText = "Параметры: " .. table.concat(bind.params, ", ")
            renderDrawText(paramText, x + 55, btnY + 30, 0xFFCCCCCC, 0xFF000000, 1, 0x90000000)
        end
    end
    
    -- Подсказка
    renderDrawBox(x + 10, y + h - 60, w - 20, 50, 0xFF222222)
    renderDrawText("Используйте команду для быстрой отправки:", x + 20, y + h - 50, 0xFFFFFF00, 0xFF000000, 1, 0x90000000)
    renderDrawText("Нажмите на действие для выполнения", x + 20, y + h - 30, 0xFFFFFF00, 0xFF000000, 1, 0x90000000)
end

-- Меню кодов
function drawCrimesMenu(x, y, w, h)
    renderDrawText("Справочник кодов правонарушений", x + 15, y + 10, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    local startY = y + 35
    local lineH = 45
    
    for i = 1, math.min(#crimes, 10) do
        local crime = crimes[i]
        local lineY = startY + (i - 1) * lineH
        
        renderDrawBox(x + 10, lineY, w - 20, 40, 0xFF333333)
        
        -- Код
        renderDrawText("№" .. crime.code, x + 20, lineY + 5, 0xFF00BFFF, 0xFF000000, 1, 0x90000000)
        
        -- Название
        renderDrawText(crime.name, x + 70, lineY + 5, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
        
        -- Детали
        local details = string.format("?%d | $%d | %dмин", crime.stars, crime.fine, crime.time)
        renderDrawText(details, x + 70, lineY + 22, 0xFFFFFF00, 0xFF000000, 1, 0x90000000)
    end
end

-- Меню быстрых действий
function drawQuickMenu(x, y, w, h)
    renderDrawText("Быстрые действия", x + 15, y + 10, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    local startY = y + 40
    
    -- Розыск
    renderDrawBox(x + 10, startY, w - 20, 45, 0xFF00AA00)
    renderDrawText("?? ОБЪЯВИТЬ РОЗЫСК (/msu id stars reason)", x + 20, startY + 15, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    startY = startY + 55
    
    -- Арест
    renderDrawBox(x + 10, startY, w - 20, 45, 0xFFCC0000)
    renderDrawText("?? АРЕСТОВАТЬ (/marrest id)", x + 20, startY + 15, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    startY = startY + 60
    renderDrawText("10-коды и быстрые команды:", x + 15, startY, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    startY = startY + 30
    local btnW = (w - 40) / 2
    local btnH = 40
    local col = 0
    local row = 0
    
    for i, cmd in ipairs(quickCmds) do
        local btnX = x + 10 + col * (btnW + 10)
        local btnY = startY + row * (btnH + 10)
        
        renderDrawBox(btnX, btnY, btnW, btnH, 0xFF444444)
        renderDrawText(cmd.name, btnX + 10, btnY + 12, cmd.color, 0xFF000000, 1, 0x90000000)
        
        col = col + 1
        if col >= 2 then
            col = 0
            row = row + 1
        end
    end
end

-- Меню настроек
function drawSettingsMenu(x, y, w, h)
    renderDrawText("Настройки скрипта", x + 15, y + 10, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    local startY = y + 40
    local lineH = 45
    
    local settings = {
        {name = "Уведомления", key = "notifications"},
        {name = "Авто-приветствие", key = "autoGreet"},
        {name = "Авто-сохранение", key = "autoSave"}
    }
    
    for i, setting in ipairs(settings) do
        local lineY = startY + (i - 1) * lineH
        renderDrawBox(x + 10, lineY, w - 20, 40, 0xFF333333)
        
        local checkbox = ini.config[setting.key] and "?" or "?"
        local checkColor = ini.config[setting.key] and 0xFF00FF00 or 0xFFFF0000
        
        renderDrawText(checkbox, x + 20, lineY + 10, checkColor, 0xFF000000, 2, 0x90000000)
        renderDrawText(setting.name, x + 60, lineY + 10, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    end
    
    -- Сохранить настройки
    startY = startY + (#settings + 1) * lineH
    renderDrawBox(x + 10, startY, w - 20, 45, 0xFF0080FF)
    renderDrawText("?? СОХРАНИТЬ НАСТРОЙКИ", x + 20, startY + 15, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
end

-- Меню информации
function drawInfoMenu(x, y, w, h)
    renderDrawText("О скрипте", x + 15, y + 10, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    
    local startY = y + 40
    local lineH = 25
    
    local info = {
        "Police Helper Mobile v2.0",
        "",
        "Команды:",
        "/mhelper, /mh - Открыть меню",
        "/msu [id] [stars] [reason] - Розыск",
        "/marrest [id] - Арест",
        "",
        "10-коды:",
        "10-4 = Принято | 10-6 = Занят",
        "10-7 = Вне службы | 10-8 = Свободен",
        "10-20 = Локация | 10-99 = Помощь!",
        "",
        "Разработано для Monetloader",
        "Оптимизировано для Android",
        "",
        "Используйте ответственно!"
    }
    
    for i, line in ipairs(info) do
        renderDrawText(line, x + 20, startY + (i - 1) * lineH, 0xFFFFFFFF, 0xFF000000, 1, 0x90000000)
    end
end

-- ============================================================================
-- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
-- ============================================================================

function notify(text, color)
    sampAddChatMessage(string.format("{%06X}[Police Helper] {FFFFFF}%s", color or ini.colors.main, text), -1)
end

function renderDrawText(text, x, y, color, borderColor, font, shadowColor)
    font = font or 1
    borderColor = borderColor or 0xFF000000
    shadowColor = shadowColor or 0x90000000
    
    -- Тень
    if shadowColor then
        renderFontDrawText(renderCreateFont("Arial", font == 2 and 10 or 8, font == 2 and 13 or 9), text, x + 1, y + 1, shadowColor)
    end
    
    -- Текст
    renderFontDrawText(renderCreateFont("Arial", font == 2 and 10 or 8, font == 2 and 13 or 9), text, x, y, color)
end

function renderDrawBox(x, y, w, h, color)
    renderDrawBoxWithBorder(x, y, w, h, color, 1, 0xFF000000)
end
