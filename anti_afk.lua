--[[
    Anti-AFK Script for SAMP (MonetLoader)
    Активация: /afk
]]

local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

local afkEnabled = false
local afkThread = nil

-- Коды клавиш игры (из опкодов)
local KEY_UP = 0
local KEY_DOWN = 1
local KEY_LEFT = 2
local KEY_RIGHT = 3
local KEY_SPRINT = 4
local KEY_JUMP = 5
local KEY_ENTER = 6
local KEY_AIM = 7

-- Функция для выполнения анти-АФК действий
local function performAntiAFK()
    while afkEnabled do
        if sampIsLocalPlayerSpawned() then
            -- Получаем указатель на персонажа игрока
            local playerPed = getCharPointer(PLAYER_PED)
            
            if playerPed ~= 0 then
                -- Чередуем разные действия для имитации активности
                local action = math.random(1, 6)
                
                if action == 1 then
                    -- Короткое движение вперед
                    setGameKeyState(KEY_UP, 1)
                    wait(math.random(150, 300))
                    setGameKeyState(KEY_UP, 0)
                    
                elseif action == 2 then
                    -- Короткое движение назад
                    setGameKeyState(KEY_DOWN, 1)
                    wait(math.random(150, 300))
                    setGameKeyState(KEY_DOWN, 0)
                    
                elseif action == 3 then
                    -- Поворот влево
                    setGameKeyState(KEY_LEFT, 1)
                    wait(math.random(200, 400))
                    setGameKeyState(KEY_LEFT, 0)
                    
                elseif action == 4 then
                    -- Поворот вправо
                    setGameKeyState(KEY_RIGHT, 1)
                    wait(math.random(200, 400))
                    setGameKeyState(KEY_RIGHT, 0)
                    
                elseif action == 5 then
                    -- Комбинация: движение вперед + спринт
                    setGameKeyState(KEY_UP, 1)
                    setGameKeyState(KEY_SPRINT, 1)
                    wait(math.random(200, 400))
                    setGameKeyState(KEY_UP, 0)
                    setGameKeyState(KEY_SPRINT, 0)
                    
                elseif action == 6 then
                    -- Поворот влево + движение
                    setGameKeyState(KEY_LEFT, 1)
                    setGameKeyState(KEY_UP, 1)
                    wait(math.random(200, 350))
                    setGameKeyState(KEY_LEFT, 0)
                    setGameKeyState(KEY_UP, 0)
                end
            end
        end
        
        -- Ждем случайное время от 4 до 10 секунд перед следующим действием
        wait(math.random(4000, 10000))
    end
end

-- Обработчик команды /afk
function cmd_afk()
    if not sampIsLocalPlayerSpawned() then
        sampAddChatMessage(u8"{FF0000}[Anti-AFK] {FFFFFF}Вы не заспавнены!", 0xFFFFFFFF)
        return
    end
    
    afkEnabled = not afkEnabled
    
    if afkEnabled then
        sampAddChatMessage(u8"{00FF00}[Anti-AFK] {FFFFFF}Анти-АФК включен", 0xFFFFFFFF)
        
        -- Запускаем поток анти-АФК
        afkThread = lua_thread.create(performAntiAFK)
    else
        sampAddChatMessage(u8"{FF0000}[Anti-AFK] {FFFFFF}Анти-АФК выключен", 0xFFFFFFFF)
        
        -- Сбрасываем все клавиши
        setGameKeyState(KEY_UP, 0)
        setGameKeyState(KEY_DOWN, 0)
        setGameKeyState(KEY_LEFT, 0)
        setGameKeyState(KEY_RIGHT, 0)
        setGameKeyState(KEY_SPRINT, 0)
        
        -- Поток завершится сам, когда afkEnabled станет false
    end
end

-- Регистрация команды при загрузке скрипта
function main()
    -- Проверяем, что SAMP загружен
    if not isSampLoaded() then
        printString("Anti-AFK: SAMP не загружен!", 1000, 1)
        return
    end
    
    -- Ждем инициализации SAMP
    while not sampIsLocalPlayerSpawned() do
        wait(100)
    end
    
    sampRegisterChatCommand("afk", cmd_afk)
    sampAddChatMessage(u8"{00FF00}[Anti-AFK] {FFFFFF}Скрипт загружен. Используйте /afk для включения/выключения", 0xFFFFFFFF)
end

-- Очистка при выгрузке скрипта
function onScriptTerminate()
    if afkEnabled then
        afkEnabled = false
        -- Сбрасываем все клавиши на случай, если они были нажаты
        setGameKeyState(KEY_UP, 0)
        setGameKeyState(KEY_DOWN, 0)
        setGameKeyState(KEY_LEFT, 0)
        setGameKeyState(KEY_RIGHT, 0)
        setGameKeyState(KEY_SPRINT, 0)
    end
    
    if sampIsChatCommandDefined("afk") then
        sampUnregisterChatCommand("afk")
    end
end
