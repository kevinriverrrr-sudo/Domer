local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

local config = {
    enabled = false,
    auto_pickup = true,
    pickup_distance = 3.0,
    show_info = true,
    check_interval = 100,
    sound_notification = true,
    video_card_model = 1271, -- ID модели видеокарты (нужно уточнить для вашего сервера)
    pickup_command = '/pickup' -- Команда для подбора (может быть /pickup, /take, /grab и т.д.)
}

local configPath = getWorkingDirectory() .. '\\config\\video_card_catcher.ini'
local ini = inicfg.load({
    main = config
}, configPath)

if ini then
    config = ini.main
end

local videoCards = {}
local lastCheck = 0
local windowState = imgui.ImBool(false)
local collectedCount = 0
local lastPickupTime = 0

function saveConfig()
    inicfg.save({main = config}, configPath)
end

function main()
    if not isSampLoaded() or not isSampfuncsLoaded() then return end
    while not isSampAvailable() do wait(0) end
    
    sampRegisterChatCommand('vid', function()
        windowState.v = not windowState.v
    end)
    
    sampAddChatMessage(u8('[Video Card Catcher] Скрипт загружен. Используйте /vid для открытия настроек.'), 0x00FF00)
    
    while true do
        wait(0)
        
        if config.enabled then
            local currentTime = os.clock() * 1000
            if currentTime - lastCheck >= config.check_interval then
                lastCheck = currentTime
                checkForVideoCards()
            end
        end
    end
end

function checkForVideoCards()
    if not config.enabled then return end
    
    local playerPed = PLAYER_PED
    if not doesCharExist(playerPed) then return end
    
    local playerX, playerY, playerZ = getCharCoordinates(playerPed)
    
    -- Оптимизированный поиск объектов видеокарт
    -- Используем samp функции для получения объектов в радиусе
    local searchRadius = config.pickup_distance + 5.0 -- Небольшой запас для поиска
    
    -- Поиск ближайшего объекта нужной модели
    local closestObject = -1
    local closestDistance = searchRadius
    
    -- Проверяем объекты в разумных пределах (обычно на сервере не более 200-500 объектов)
    local maxObjects = 500
    for i = 0, maxObjects do
        if isObjectHandleValid(i) then
            local modelId = getObjectModel(i)
            
            if modelId == config.video_card_model then
                local objX, objY, objZ = getObjectCoordinates(i)
                local distance = getDistanceBetweenCoords3d(playerX, playerY, playerZ, objX, objY, objZ)
                
                if distance <= config.pickup_distance then
                    if config.show_info then
                        drawText3d(objX, objY, objZ + 0.5, u8('Видеокарта [' .. string.format('%.1f', distance) .. 'м]'), 0x00FF00FF)
                    end
                    
                    -- Находим ближайший объект для подбора
                    if distance < closestDistance then
                        closestDistance = distance
                        closestObject = i
                    end
                end
            end
        end
    end
    
    -- Подбираем ближайшую видеокарту
    if config.auto_pickup and closestObject ~= -1 and (os.clock() * 1000 - lastPickupTime) > 1000 then
        pickupVideoCard(closestObject)
        lastPickupTime = os.clock() * 1000
    end
end

function pickupVideoCard(objectId)
    -- Отправка команды для подбора видеокарты
    sampSendChat(config.pickup_command)
    
    collectedCount = collectedCount + 1
    
    if config.sound_notification then
        playSoundFrontend(-1, 'PICKUP_WEAPON_MOD', 'HUD_FRONTEND_WEAPONS_PICKUPS_SOUNDSET', false)
    end
    
    sampAddChatMessage(u8('[Video Card Catcher] Подобрано видеокарт: ' .. collectedCount), 0x00FF00)
end

function drawText3d(x, y, z, text, color)
    local onScreen, _x, _y = convert3DCoordsToScreen(x, y, z)
    if onScreen then
        drawText(_x, _y, text, 1.0, color, true, true, true, true)
    end
end

-- ImGui окно настроек
local function renderWindow()
    imgui.SetNextWindowSize(imgui.ImVec2(350, 350), imgui.Cond.FirstUseEver)
    
    if imgui.Begin(u8('Ловец видеокарт'), windowState, imgui.WindowFlags.NoResize) then
        imgui.Text(u8('Настройки ловца видеокарт'))
        imgui.Separator()
        
        -- Статистика
        imgui.Text(u8('Собрано видеокарт: ' .. collectedCount))
        if imgui.Button(u8('Сбросить счетчик'), imgui.ImVec2(-1, 0)) then
            collectedCount = 0
        end
        imgui.Separator()
        
        local enabled = imgui.ImBool(config.enabled)
        if imgui.Checkbox(u8('Включить ловец'), enabled) then
            config.enabled = enabled.v
            saveConfig()
            if config.enabled then
                sampAddChatMessage(u8('[Video Card Catcher] Ловец активирован'), 0x00FF00)
            else
                sampAddChatMessage(u8('[Video Card Catcher] Ловец деактивирован'), 0xFF0000)
            end
        end
        
        local autoPickup = imgui.ImBool(config.auto_pickup)
        if imgui.Checkbox(u8('Автоподбор'), autoPickup) then
            config.auto_pickup = autoPickup.v
            saveConfig()
        end
        
        local showInfo = imgui.ImBool(config.show_info)
        if imgui.Checkbox(u8('Показывать информацию'), showInfo) then
            config.show_info = showInfo.v
            saveConfig()
        end
        
        local soundNotif = imgui.ImBool(config.sound_notification)
        if imgui.Checkbox(u8('Звуковое уведомление'), soundNotif) then
            config.sound_notification = soundNotif.v
            saveConfig()
        end
        
        imgui.Separator()
        
        local distance = imgui.ImFloat(config.pickup_distance)
        if imgui.SliderFloat(u8('Дистанция подбора'), distance, 1.0, 10.0, '%.1f м') then
            config.pickup_distance = distance.v
            saveConfig()
        end
        
        local interval = imgui.ImInt(config.check_interval)
        if imgui.SliderInt(u8('Интервал проверки (мс)'), interval, 50, 500) then
            config.check_interval = interval.v
            saveConfig()
        end
        
        local modelId = imgui.ImInt(config.video_card_model)
        if imgui.InputInt(u8('ID модели видеокарты'), modelId) then
            config.video_card_model = modelId.v
            saveConfig()
        end
        
        imgui.Spacing()
        
        local pickupCmd = imgui.ImBuffer(config.pickup_command, 256)
        if imgui.InputText(u8('Команда подбора'), pickupCmd) then
            config.pickup_command = pickupCmd.v
            saveConfig()
        end
        
        imgui.Separator()
        imgui.TextWrapped(u8('Примечание: Укажите правильный ID модели видеокарты и команду подбора для вашего сервера'))
        
        imgui.Separator()
        
        if imgui.Button(u8('Закрыть'), imgui.ImVec2(-1, 0)) then
            windowState.v = false
        end
        
        imgui.End()
    end
end

function imgui.OnDrawFrame()
    if windowState.v then
        renderWindow()
    end
end

function onScriptTerminate(script, quitGame)
    if script == thisScript() then
        saveConfig()
    end
end
