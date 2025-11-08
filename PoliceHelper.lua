script_name("Police Helper")
script_author("Assistant")
script_version("1.0")

require "lib.moonloader"
local imgui = require "mimgui"
local encoding = require "encoding"
encoding.default = "CP1251"
u8 = encoding.UTF8

-- Переменные ImGui
local new = imgui.new
local mainWindow = new.bool(false)
local selectedTab = new.int(0)

-- Биндер команд
local binds = {
    {name = "Приветствие", text = "/do На груди висит бейдж с надписью '{name}' | {rank}.", enabled = true},
    {name = "Предъявить удостоверение", text = "/me достал удостоверение из кармана\\n/do Удостоверение в руке.\\n/showbadge {id}", enabled = true},
    {name = "Надеть наручники", text = "/me взял наручники с пояса\\n/me надел наручники на руки человека\\n/cuff {id}", enabled = true},
    {name = "Снять наручники", text = "/me достал ключ от наручников\\n/me снял наручники с рук человека\\n/uncuff {id}", enabled = true},
    {name = "Обыскать", text = "/me начал обыскивать человека\\n/frisk {id}", enabled = true},
    {name = "Изъять оружие", text = "/me изъял оружие у человека\\n/takegun {id}", enabled = true},
    {name = "Изъять наркотики", text = "/me изъял наркотики у человека\\n/takedrugs {id}", enabled = true},
    {name = "Посадить в авто", text = "/me открыл дверь автомобиля\\n/me посадил человека в автомобиль\\n/pull {id}", enabled = true},
    {name = "Погоня", text = "/m Всем постам! Внимание! Объявлена погоня за {vehicle}! {color}! Номер: {number}!", enabled = true},
    {name = "Запросить подкрепление", text = "/r Запрашиваю подкрепление! Моя локация: {location}", enabled = true},
}

-- Поля ввода для биндов
local bindInputs = {}
for i = 1, #binds do
    bindInputs[i] = {
        id = new.char[256](),
        name = new.char[256](),
        rank = new.char[256](),
        vehicle = new.char[256](),
        color = new.char[256](),
        number = new.char[256](),
        location = new.char[256](),
        reason = new.char[256](),
        stars = new.char[256]()
    }
end

-- Коды правонарушений
local crimeCodes = {
    {code = "01", crime = "Угон транспорта", stars = "2", fine = "1000$"},
    {code = "02", crime = "Ограбление человека", stars = "3", fine = "2000$"},
    {code = "03", crime = "Ограбление бизнеса", stars = "4", fine = "3000$"},
    {code = "04", crime = "Ограбление банка", stars = "5", fine = "4000$"},
    {code = "05", crime = "Убийство", stars = "6", fine = "5000$"},
    {code = "06", crime = "Нападение на офицера", stars = "4", fine = "3500$"},
    {code = "07", crime = "Хранение наркотиков", stars = "3", fine = "2500$"},
    {code = "08", crime = "Сбыт наркотиков", stars = "4", fine = "3500$"},
    {code = "09", crime = "Хулиганство", stars = "1", fine = "500$"},
    {code = "10", crime = "Незаконное оружие", stars = "3", fine = "2000$"},
    {code = "11", crime = "Терроризм", stars = "6", fine = "6000$"},
    {code = "12", crime = "Коррупция", stars = "5", fine = "4500$"},
    {code = "13", crime = "Побег из тюрьмы", stars = "4", fine = "3000$"},
    {code = "14", crime = "Превышение скорости", stars = "1", fine = "300$"},
    {code = "15", crime = "Проезд на красный", stars = "1", fine = "200$"},
}

-- Быстрые команды
local quickCommands = {
    {name = "Погоня", cmd = "/m Всем постам! Объявлена погоня!"},
    {name = "Подкрепление", cmd = "/r Нужно подкрепление!"},
    {name = "10-4 (Принято)", cmd = "/r 10-4"},
    {name = "10-8 (Свободен)", cmd = "/r 10-8"},
    {name = "10-6 (Занят)", cmd = "/r 10-6"},
    {name = "10-7 (Вне службы)", cmd = "/r 10-7"},
    {name = "10-20 (Местоположение)", cmd = "/r 10-20"},
    {name = "10-99 (Необходима помощь)", cmd = "/r 10-99! Нужна помощь!"},
}

-- Настройки
local settings = {
    fastArrест = new.bool(false),
    autoGreet = new.bool(false),
    showNotifications = new.bool(true),
    soundEnabled = new.bool(true),
}

-- Поля для быстрого действия
local quickAction = {
    suspectId = new.char[256](),
    wantedLevel = new.char[256](),
    crimeReason = new.char[256](),
    fine = new.char[256](),
    arrestTime = new.char[256](),
}

function main()
    if not isSampLoaded() or not isSampfuncsLoaded() then return end
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand("mhelper", function()
        mainWindow[0] = not mainWindow[0]
    end)
    
    sampAddChatMessage("[Police Helper] {FFFFFF}Скрипт успешно загружен! Используйте {00FF00}/mhelper {FFFFFF}для открытия меню", 0x00BFFF)
    
    while true do
        wait(0)
    end
end

-- Функция отправки команд с задержкой
function sendCommands(text, id, name, rank, vehicle, color, number, location, reason, stars)
    text = text:gsub("{id}", id or "")
    text = text:gsub("{name}", name or "")
    text = text:gsub("{rank}", rank or "")
    text = text:gsub("{vehicle}", vehicle or "")
    text = text:gsub("{color}", color or "")
    text = text:gsub("{number}", number or "")
    text = text:gsub("{location}", location or "")
    text = text:gsub("{reason}", reason or "")
    text = text:gsub("{stars}", stars or "")
    
    local commands = {}
    for cmd in text:gmatch("[^\n]+") do
        table.insert(commands, cmd)
    end
    
    lua_thread.create(function()
        for _, cmd in ipairs(commands) do
            sampSendChat(cmd)
            wait(1000)
        end
    end)
end

-- Функция быстрого ареста
function quickArrest(id, stars, reason, fine, time)
    lua_thread.create(function()
        sampSendChat("/me достал наручники с пояса")
        wait(1000)
        sampSendChat("/me надел наручники на руки подозреваемому")
        wait(1000)
        sampSendChat("/cuff " .. id)
        wait(1000)
        sampSendChat("/su " .. id .. " " .. stars .. " " .. reason)
        wait(1000)
        sampSendChat("/arrest " .. id)
        wait(500)
        if settings.showNotifications[0] then
            sampAddChatMessage("[Police Helper] {FFFFFF}Арест успешно выполнен!", 0x00FF00)
        end
    end)
end

-- Функция быстрого розыска
function quickWanted(id, stars, reason)
    lua_thread.create(function()
        sampSendChat("/su " .. id .. " " .. stars .. " " .. reason)
        wait(500)
        if settings.showNotifications[0] then
            sampAddChatMessage("[Police Helper] {FFFFFF}Розыск объявлен!", 0x00FF00)
        end
    end)
end

-- GUI Меню
imgui.OnFrame(function() return mainWindow[0] end,
    function(player)
        imgui.SetNextWindowPos(imgui.ImVec2(500, 300), imgui.Cond.FirstUseEver, imgui.ImVec2(0.5, 0.5))
        imgui.SetNextWindowSize(imgui.ImVec2(800, 600), imgui.Cond.FirstUseEver)
        imgui.Begin(u8"Police Helper | Помощник для полицейских", mainWindow, imgui.WindowFlags.NoCollapse)
        
        -- Табы
        if imgui.BeginTabBar("MainTabs") then
            -- Таб 1: Биндер команд
            if imgui.BeginTabItem(u8"Биндер команд") then
                imgui.Text(u8"Выберите действие и настройте параметры:")
                imgui.Separator()
                
                imgui.BeginChild("binds_list", imgui.ImVec2(750, 450), true)
                for i, bind in ipairs(binds) do
                    imgui.PushID(i)
                    imgui.Text(u8(bind.name))
                    imgui.SameLine()
                    if imgui.Button(u8"Использовать##" .. i) then
                        local id = ffi.string(bindInputs[i].id):gsub("%s+", "")
                        local name = ffi.string(bindInputs[i].name):gsub("%s+", "")
                        local rank = ffi.string(bindInputs[i].rank):gsub("%s+", "")
                        local vehicle = ffi.string(bindInputs[i].vehicle):gsub("%s+", "")
                        local color = ffi.string(bindInputs[i].color):gsub("%s+", "")
                        local number = ffi.string(bindInputs[i].number):gsub("%s+", "")
                        local location = ffi.string(bindInputs[i].location):gsub("%s+", "")
                        local reason = ffi.string(bindInputs[i].reason):gsub("%s+", "")
                        local stars = ffi.string(bindInputs[i].stars):gsub("%s+", "")
                        
                        sendCommands(bind.text, id, name, rank, vehicle, color, number, location, reason, stars)
                        
                        if settings.showNotifications[0] then
                            sampAddChatMessage("[Police Helper] {FFFFFF}Команда отправлена: " .. bind.name, 0x00BFFF)
                        end
                    end
                    
                    -- Поля ввода в зависимости от биндаа
                    if bind.text:find("{id}") then
                        imgui.InputText(u8"ID игрока##" .. i, bindInputs[i].id, 256)
                    end
                    if bind.text:find("{name}") then
                        imgui.InputText(u8"Имя##" .. i, bindInputs[i].name, 256)
                    end
                    if bind.text:find("{rank}") then
                        imgui.InputText(u8"Звание##" .. i, bindInputs[i].rank, 256)
                    end
                    if bind.text:find("{vehicle}") then
                        imgui.InputText(u8"Транспорт##" .. i, bindInputs[i].vehicle, 256)
                    end
                    if bind.text:find("{color}") then
                        imgui.InputText(u8"Цвет##" .. i, bindInputs[i].color, 256)
                    end
                    if bind.text:find("{number}") then
                        imgui.InputText(u8"Номер##" .. i, bindInputs[i].number, 256)
                    end
                    if bind.text:find("{location}") then
                        imgui.InputText(u8"Локация##" .. i, bindInputs[i].location, 256)
                    end
                    if bind.text:find("{reason}") then
                        imgui.InputText(u8"Причина##" .. i, bindInputs[i].reason, 256)
                    end
                    if bind.text:find("{stars}") then
                        imgui.InputText(u8"Звёзды##" .. i, bindInputs[i].stars, 256)
                    end
                    
                    imgui.Separator()
                    imgui.PopID()
                end
                imgui.EndChild()
                
                imgui.EndTabItem()
            end
            
            -- Таб 2: Коды правонарушений
            if imgui.BeginTabItem(u8"Коды правонарушений") then
                imgui.Text(u8"Справочник кодов правонарушений:")
                imgui.Separator()
                
                imgui.BeginChild("crimes_list", imgui.ImVec2(750, 450), true)
                imgui.Columns(4, "crimes_columns")
                imgui.SetColumnWidth(0, 80)
                imgui.SetColumnWidth(1, 300)
                imgui.SetColumnWidth(2, 100)
                imgui.SetColumnWidth(3, 150)
                
                imgui.Text(u8"Код")
                imgui.NextColumn()
                imgui.Text(u8"Правонарушение")
                imgui.NextColumn()
                imgui.Text(u8"Звёзды")
                imgui.NextColumn()
                imgui.Text(u8"Штраф")
                imgui.NextColumn()
                imgui.Separator()
                
                for _, crime in ipairs(crimeCodes) do
                    imgui.Text(crime.code)
                    imgui.NextColumn()
                    imgui.Text(u8(crime.crime))
                    imgui.NextColumn()
                    imgui.Text(crime.stars)
                    imgui.NextColumn()
                    imgui.Text(crime.fine)
                    imgui.NextColumn()
                end
                
                imgui.Columns(1)
                imgui.EndChild()
                
                imgui.EndTabItem()
            end
            
            -- Таб 3: Быстрые действия
            if imgui.BeginTabItem(u8"Быстрые действия") then
                imgui.Text(u8"Быстрые действия для работы:")
                imgui.Separator()
                
                imgui.BeginChild("quick_actions", imgui.ImVec2(750, 450), true)
                
                -- Быстрый розыск
                imgui.TextColored(imgui.ImVec4(0.2, 1.0, 0.2, 1.0), u8"БЫСТРЫЙ РОЗЫСК")
                imgui.InputText(u8"ID подозреваемого##wanted", quickAction.suspectId, 256)
                imgui.InputText(u8"Уровень розыска (1-6)##wanted", quickAction.wantedLevel, 256)
                imgui.InputText(u8"Причина##wanted", quickAction.crimeReason, 256)
                if imgui.Button(u8"Объявить розыск", imgui.ImVec2(200, 30)) then
                    local id = ffi.string(quickAction.suspectId):gsub("%s+", "")
                    local stars = ffi.string(quickAction.wantedLevel):gsub("%s+", "")
                    local reason = ffi.string(quickAction.crimeReason):gsub("%s+", "")
                    
                    if id ~= "" and stars ~= "" and reason ~= "" then
                        quickWanted(id, stars, reason)
                    else
                        sampAddChatMessage("[Police Helper] {FF0000}Заполните все поля!", 0xFF0000)
                    end
                end
                
                imgui.Separator()
                imgui.Dummy(imgui.ImVec2(0, 10))
                
                -- Быстрый арест
                imgui.TextColored(imgui.ImVec4(1.0, 0.5, 0.2, 1.0), u8"БЫСТРЫЙ АРЕСТ")
                imgui.InputText(u8"ID подозреваемого##arrest", quickAction.suspectId, 256)
                imgui.InputText(u8"Уровень розыска (1-6)##arrest", quickAction.wantedLevel, 256)
                imgui.InputText(u8"Причина##arrest", quickAction.crimeReason, 256)
                if imgui.Button(u8"Произвести арест", imgui.ImVec2(200, 30)) then
                    local id = ffi.string(quickAction.suspectId):gsub("%s+", "")
                    local stars = ffi.string(quickAction.wantedLevel):gsub("%s+", "")
                    local reason = ffi.string(quickAction.crimeReason):gsub("%s+", "")
                    
                    if id ~= "" and stars ~= "" and reason ~= "" then
                        quickArrest(id, stars, reason, "", "")
                    else
                        sampAddChatMessage("[Police Helper] {FF0000}Заполните все поля!", 0xFF0000)
                    end
                end
                
                imgui.Separator()
                imgui.Dummy(imgui.ImVec2(0, 10))
                
                -- Быстрые команды
                imgui.TextColored(imgui.ImVec4(0.2, 0.5, 1.0, 1.0), u8"БЫСТРЫЕ КОМАНДЫ")
                for i, cmd in ipairs(quickCommands) do
                    if imgui.Button(u8(cmd.name) .. "##quick" .. i, imgui.ImVec2(200, 25)) then
                        sampSendChat(cmd.cmd)
                    end
                    if i % 2 == 0 then
                        imgui.SameLine()
                    end
                end
                
                imgui.EndChild()
                
                imgui.EndTabItem()
            end
            
            -- Таб 4: Настройки
            if imgui.BeginTabItem(u8"Настройки") then
                imgui.Text(u8"Настройки скрипта:")
                imgui.Separator()
                
                imgui.BeginChild("settings", imgui.ImVec2(750, 450), true)
                
                imgui.Checkbox(u8"Быстрый арест (автоматические действия)", settings.fastArrест)
                imgui.Checkbox(u8"Автоматическое приветствие при входе", settings.autoGreet)
                imgui.Checkbox(u8"Показывать уведомления", settings.showNotifications)
                imgui.Checkbox(u8"Звуковые уведомления", settings.soundEnabled)
                
                imgui.Dummy(imgui.ImVec2(0, 20))
                imgui.Separator()
                imgui.Dummy(imgui.ImVec2(0, 10))
                
                imgui.TextColored(imgui.ImVec4(1.0, 1.0, 0.2, 1.0), u8"О СКРИПТЕ")
                imgui.Text(u8"Police Helper v1.0")
                imgui.Text(u8"Помощник для сотрудников полиции")
                imgui.Text(u8"Разработано специально для SAMP")
                
                imgui.Dummy(imgui.ImVec2(0, 10))
                imgui.Separator()
                imgui.Dummy(imgui.ImVec2(0, 10))
                
                imgui.TextColored(imgui.ImVec4(0.5, 1.0, 0.5, 1.0), u8"ГОРЯЧИЕ КЛАВИШИ")
                imgui.Text(u8"/mhelper - Открыть/закрыть меню")
                
                imgui.EndChild()
                
                imgui.EndTabItem()
            end
            
            -- Таб 5: Информация
            if imgui.BeginTabItem(u8"Информация") then
                imgui.BeginChild("info", imgui.ImVec2(750, 450), true)
                
                imgui.TextColored(imgui.ImVec4(1.0, 0.5, 0.2, 1.0), u8"ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ")
                imgui.Dummy(imgui.ImVec2(0, 5))
                
                imgui.BulletText(u8"Используйте команду /mhelper для открытия меню")
                imgui.BulletText(u8"В разделе 'Биндер команд' доступны готовые шаблоны для работы")
                imgui.BulletText(u8"В разделе 'Коды правонарушений' - справочник всех кодов")
                imgui.BulletText(u8"В разделе 'Быстрые действия' - ускоренный розыск и арест")
                imgui.BulletText(u8"Настройте скрипт под себя в разделе 'Настройки'")
                
                imgui.Dummy(imgui.ImVec2(0, 15))
                imgui.Separator()
                imgui.Dummy(imgui.ImVec2(0, 10))
                
                imgui.TextColored(imgui.ImVec4(0.2, 1.0, 1.0, 1.0), u8"ПОЛИЦЕЙСКИЕ 10-КОДЫ")
                imgui.Dummy(imgui.ImVec2(0, 5))
                
                imgui.Text(u8"10-4 - Принято, понял")
                imgui.Text(u8"10-6 - Занят")
                imgui.Text(u8"10-7 - Вне службы")
                imgui.Text(u8"10-8 - Свободен, на связи")
                imgui.Text(u8"10-20 - Местоположение")
                imgui.Text(u8"10-99 - Нужна немедленная помощь")
                
                imgui.Dummy(imgui.ImVec2(0, 15))
                imgui.Separator()
                imgui.Dummy(imgui.ImVec2(0, 10))
                
                imgui.TextColored(imgui.ImVec4(1.0, 1.0, 0.2, 1.0), u8"ОСНОВНЫЕ КОМАНДЫ ПОЛИЦИИ")
                imgui.Dummy(imgui.ImVec2(0, 5))
                
                imgui.Text(u8"/su [id] [stars] [reason] - Объявить розыск")
                imgui.Text(u8"/arrest [id] - Арестовать подозреваемого")
                imgui.Text(u8"/cuff [id] - Надеть наручники")
                imgui.Text(u8"/uncuff [id] - Снять наручники")
                imgui.Text(u8"/frisk [id] - Обыскать")
                imgui.Text(u8"/takegun [id] - Изъять оружие")
                imgui.Text(u8"/takedrugs [id] - Изъять наркотики")
                imgui.Text(u8"/m [text] - Мегафон")
                imgui.Text(u8"/r [text] - Рация департамента")
                imgui.Text(u8"/d [text] - Рация всех департаментов")
                
                imgui.EndChild()
                
                imgui.EndTabItem()
            end
            
            imgui.EndTabBar()
        end
        
        imgui.End()
    end
).HideCursor = true
