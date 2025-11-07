local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

-- Состояние скрипта
local afkEnabled = false
local lastMoveTime = 0
local moveInterval = 5000 -- интервал движения в миллисекундах (5 секунд)
local moveDuration = 500 -- длительность движения в миллисекундах (0.5 секунды)
local isMoving = false
local currentMoveDirection = 0
local moveStartTime = 0
local initialized = false

-- ImGui окно
local window = imgui.ImBool(false)
local config = {
    enabled = false,
    interval = 5000,
    duration = 500,
    randomMovement = true
}

-- Загрузка конфигурации
local function loadConfig()
    local ini = inicfg.load({
        main = {
            enabled = false,
            interval = 5000,
            duration = 500,
            randomMovement = true
        }
    }, 'anti_afk')
    config = ini.main
    afkEnabled = config.enabled
    moveInterval = config.interval
    moveDuration = config.duration
end

-- Сохранение конфигурации
local function saveConfig()
    local ini = {
        main = config
    }
    inicfg.save(ini, 'anti_afk')
end

-- Инициализация ImGui
local function initImGui()
    imgui.OnInitialize(function()
        imgui.StyleColorsDark()
    end)
end

-- Отрисовка меню
local function renderMenu()
    if window.v then
        imgui.SetNextWindowSize(imgui.ImVec2(350, 250), imgui.Cond.FirstUseEver)
        if imgui.Begin(u8('Анти-АФК Настройки'), window, imgui.WindowFlags.None) then
            imgui.Text(u8('Настройки анти-АФК скрипта'))
            imgui.Separator()
            
            -- Включено/выключено
            local enabledBool = imgui.ImBool(config.enabled)
            imgui.Checkbox(u8('Включить анти-АФК'), enabledBool)
            if enabledBool.v ~= config.enabled then
                config.enabled = enabledBool.v
                afkEnabled = config.enabled
                saveConfig()
            end
            
            imgui.Spacing()
            
            -- Интервал движения (секунды)
            local intervalSeconds = config.interval / 1000
            local intervalFloat = imgui.ImFloat(intervalSeconds)
            imgui.SliderFloat(u8('Интервал движения (сек)'), intervalFloat, 1.0, 30.0, '%.1f')
            if intervalFloat.v ~= intervalSeconds then
                config.interval = math.floor(intervalFloat.v * 1000)
                moveInterval = config.interval
                saveConfig()
            end
            
            -- Длительность движения (секунды)
            local durationSeconds = config.duration / 1000
            local durationFloat = imgui.ImFloat(durationSeconds)
            imgui.SliderFloat(u8('Длительность движения (сек)'), durationFloat, 0.1, 2.0, '%.1f')
            if durationFloat.v ~= durationSeconds then
                config.duration = math.floor(durationFloat.v * 1000)
                moveDuration = config.duration
                saveConfig()
            end
            
            imgui.Spacing()
            
            -- Случайное движение
            local randomBool = imgui.ImBool(config.randomMovement)
            imgui.Checkbox(u8('Случайное движение'), randomBool)
            if randomBool.v ~= config.randomMovement then
                config.randomMovement = randomBool.v
                saveConfig()
            end
            
            imgui.Spacing()
            imgui.Separator()
            
            -- Статус
            local statusText = afkEnabled and u8('Анти-АФК активен') or u8('Анти-АФК неактивен')
            imgui.Text(statusText)
            
            imgui.End()
        end
    end
end

-- Выбор случайного направления движения
local function getRandomDirection()
    local directions = {
        0, -- влево
        1, -- вправо
        2, -- вперед
        3, -- назад
        4, -- влево-вперед
        5, -- вправо-вперед
        6, -- влево-назад
        7  -- вправо-назад
    }
    return directions[math.random(1, #directions)]
end

-- Выполнение движения
local function performMovement(direction)
    local playerPed = getPlayerChar(PLAYER_PED)
    if not playerPed or not isCharOnFoot(playerPed) then
        return
    end
    
    local left = false
    local right = false
    local forward = false
    local backward = false
    
    -- Определяем направление движения
    if direction == 0 then -- влево
        left = true
    elseif direction == 1 then -- вправо
        right = true
    elseif direction == 2 then -- вперед
        forward = true
    elseif direction == 3 then -- назад
        backward = true
    elseif direction == 4 then -- влево-вперед
        left = true
        forward = true
    elseif direction == 5 then -- вправо-вперед
        right = true
        forward = true
    elseif direction == 6 then -- влево-назад
        left = true
        backward = true
    elseif direction == 7 then -- вправо-назад
        right = true
        backward = true
    end
    
    -- Применяем движение
    if left then
        setGameKeyState(21, 255) -- KEY_LEFT
    end
    if right then
        setGameKeyState(22, 255) -- KEY_RIGHT
    end
    if forward then
        setGameKeyState(32, 255) -- KEY_UP
    end
    if backward then
        setGameKeyState(33, 255) -- KEY_DOWN
    end
end

-- Остановка движения
local function stopMovement()
    setGameKeyState(21, 0) -- KEY_LEFT
    setGameKeyState(22, 0) -- KEY_RIGHT
    setGameKeyState(32, 0) -- KEY_UP
    setGameKeyState(33, 0) -- KEY_DOWN
end

-- Основной цикл анти-АФК
local function afkLoop()
    while true do
        wait(0)
        
        if not initialized then
            lastMoveTime = getTickCount()
            initialized = true
        end
        
        if afkEnabled and isSampAvailable() and not isGamePaused() then
            local currentTime = getTickCount()
            
            if isMoving then
                -- Продолжаем движение каждый кадр
                performMovement(currentMoveDirection)
                
                -- Проверяем, нужно ли остановить движение
                if currentTime - moveStartTime >= moveDuration then
                    stopMovement()
                    isMoving = false
                    lastMoveTime = currentTime
                end
            else
                -- Проверяем, нужно ли начать движение
                if currentTime - lastMoveTime >= moveInterval then
                    local direction = config.randomMovement and getRandomDirection() or currentMoveDirection
                    currentMoveDirection = direction
                    isMoving = true
                    moveStartTime = currentTime
                end
            end
        else
            -- Если анти-АФК выключен, останавливаем движение
            if isMoving then
                stopMovement()
                isMoving = false
            end
        end
    end
end

-- Команда /afk
local function afkCommand(params)
    afkEnabled = not afkEnabled
    config.enabled = afkEnabled
    saveConfig()
    
    local status = afkEnabled and u8('включен') or u8('выключен')
    sampAddChatMessage(string.format(u8('Анти-АФК %s'), status), 0x00FF00FF)
    
    if not afkEnabled then
        stopMovement()
        isMoving = false
    end
end

-- Команда для открытия меню
local function menuCommand(params)
    window.v = not window.v
end

function main()
    -- Инициализация генератора случайных чисел
    math.randomseed(os.time())
    
    -- Проверка загрузки библиотек
    if not isSampfuncsLoaded() or not isSampLoaded() then
        return
    end
    
    -- Ожидание загрузки SAMP
    while not isSampAvailable() do
        wait(0)
    end
    
    -- Загрузка конфигурации
    loadConfig()
    
    -- Инициализация ImGui
    initImGui()
    
    -- Регистрация команд
    sampRegisterChatCommand('afk', afkCommand)
    sampRegisterChatCommand('afkmenu', menuCommand)
    
    -- Запуск основного цикла анти-АФК
    lua_thread.create(afkLoop)
    
    -- Основной цикл отрисовки ImGui и проверки клавиатуры
    while true do
        wait(0)
        
        -- Проверка нажатия F7 для открытия меню
        if wasKeyPressed(0x76) then -- VK_F7
            window.v = not window.v
        end
        
        renderMenu()
    end
end
