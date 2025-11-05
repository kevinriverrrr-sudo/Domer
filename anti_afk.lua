script_author('Cosmo & ported by t.me/monetbinder (@osp_x)')
script_description('ShitCode Prodakshen')
local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

local ffi = require 'ffi'

local version = '1.0.0'

local config = {
    enabled = false,
    interval = 5000, -- интервал в миллисекундах
    useCameraRotation = true,
    useAnimation = true,
    useMovement = false,
    randomDelay = true,
    minDelay = 3000,
    maxDelay = 8000
}

local menuOpen = false
local configPath = getWorkingDirectory() .. '/configs/anti_afk.ini'

-- ImGui окно
local window = imgui.new.bool(false)
local enabled = imgui.new.bool(config.enabled)
local interval = imgui.new.int(config.interval)
local useCameraRotation = imgui.new.bool(config.useCameraRotation)
local useAnimation = imgui.new.bool(config.useAnimation)
local useMovement = imgui.new.bool(config.useMovement)
local randomDelay = imgui.new.bool(config.randomDelay)
local minDelay = imgui.new.int(config.minDelay)
local maxDelay = imgui.new.int(config.maxDelay)

local lastActionTime = 0
local nextActionTime = 0

-- Загрузка конфигурации
function loadConfig()
    if doesFileExist(configPath) then
        local cfg = inicfg.load(nil, configPath)
        if cfg and cfg.anti_afk then
            config.enabled = cfg.anti_afk.enabled or config.enabled
            config.interval = cfg.anti_afk.interval or config.interval
            config.useCameraRotation = cfg.anti_afk.useCameraRotation ~= nil and cfg.anti_afk.useCameraRotation or config.useCameraRotation
            config.useAnimation = cfg.anti_afk.useAnimation ~= nil and cfg.anti_afk.useAnimation or config.useAnimation
            config.useMovement = cfg.anti_afk.useMovement ~= nil and cfg.anti_afk.useMovement or config.useMovement
            config.randomDelay = cfg.anti_afk.randomDelay ~= nil and cfg.anti_afk.randomDelay or config.randomDelay
            config.minDelay = cfg.anti_afk.minDelay or config.minDelay
            config.maxDelay = cfg.anti_afk.maxDelay or config.maxDelay
            
            -- Обновляем ImGui переменные
            enabled.v = config.enabled
            interval.v = config.interval
            useCameraRotation.v = config.useCameraRotation
            useAnimation.v = config.useAnimation
            useMovement.v = config.useMovement
            randomDelay.v = config.randomDelay
            minDelay.v = config.minDelay
            maxDelay.v = config.maxDelay
        end
    end
end

-- Сохранение конфигурации
function saveConfig()
    local cfg = {
        anti_afk = {
            enabled = config.enabled,
            interval = config.interval,
            useCameraRotation = config.useCameraRotation,
            useAnimation = config.useAnimation,
            useMovement = config.useMovement,
            randomDelay = config.randomDelay,
            minDelay = config.minDelay,
            maxDelay = config.maxDelay
        }
    }
    inicfg.save(cfg, configPath)
end

-- Инициализация при загрузке скрипта
function main()
    if not isSampfuncsLoaded() or not isSampLoaded() then return end
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand('afk', function()
        menuOpen = not menuOpen
        window.v = menuOpen
    end)
    
    loadConfig()
    
    lua_thread.create(function()
        while true do
            wait(0)
            
            if config.enabled and isSampAvailable() then
                local currentTime = os.clock() * 1000
                
                if currentTime >= nextActionTime then
                    -- Поворот камеры (незаметное движение мыши)
                    if config.useCameraRotation then
                        local angle = math.random(0, 360)
                        local mouseX = math.cos(math.rad(angle)) * 0.5
                        local mouseY = math.sin(math.rad(angle)) * 0.5
                        setCameraBehindPlayer()
                        -- Симуляция движения мыши через изменение угла камеры
                        local x, y, z = getCharCoordinates(PLAYER_PED)
                        local heading = getCharHeading(PLAYER_PED)
                        setCharHeading(PLAYER_PED, (heading + mouseX) % 360)
                    end
                    
                    -- Анимация через команду /me
                    if config.useAnimation then
                        local messages = {
                            '*проверяет часы*',
                            '*смотрит по сторонам*',
                            '*поправляет одежду*',
                            '*почесывает голову*'
                        }
                        local msg = messages[math.random(1, #messages)]
                        sampSendChat('/me ' .. msg)
                    end
                    
                    -- Небольшое движение (минимальное смещение позиции)
                    if config.useMovement then
                        local x, y, z = getCharCoordinates(PLAYER_PED)
                        local offsetX = (math.random() - 0.5) * 0.001
                        local offsetY = (math.random() - 0.5) * 0.001
                        setCharCoordinates(PLAYER_PED, x + offsetX, y + offsetY, z)
                        wait(5)
                        setCharCoordinates(PLAYER_PED, x, y, z)
                    end
                    
                    -- Вычисляем следующее время действия
                    if config.randomDelay then
                        nextActionTime = currentTime + math.random(config.minDelay, config.maxDelay)
                    else
                        nextActionTime = currentTime + config.interval
                    end
                    
                    lastActionTime = currentTime
                end
            end
        end
    end)
    
    -- Регистрация callback для ImGui
    imgui.OnFrame(function()
        if not window.v then return end
        
        imgui.SetNextWindowSize(imgui.ImVec2(400, 450), imgui.Cond.FirstUseEver)
        imgui.Begin(u8('Anti-AFK v' .. version), window, imgui.WindowFlags.None)
        
        -- Включение/выключение
        if imgui.Checkbox(u8('Включить Anti-AFK'), enabled) then
            config.enabled = enabled.v
            saveConfig()
            if config.enabled then
                nextActionTime = os.clock() * 1000
            end
        end
        
        imgui.Separator()
        
        -- Интервал
        imgui.Text(u8('Интервал (мс):'))
        if imgui.InputInt(u8('##interval'), interval) then
            if interval.v < 1000 then interval.v = 1000 end
            if interval.v > 60000 then interval.v = 60000 end
            config.interval = interval.v
            saveConfig()
        end
        
        imgui.Separator()
        
        -- Случайная задержка
        if imgui.Checkbox(u8('Случайная задержка'), randomDelay) then
            config.randomDelay = randomDelay.v
            saveConfig()
        end
        
        if config.randomDelay then
            imgui.Text(u8('Минимальная задержка (мс):'))
            if imgui.InputInt(u8('##mindelay'), minDelay) then
                if minDelay.v < 1000 then minDelay.v = 1000 end
                if minDelay.v > config.maxDelay then minDelay.v = config.maxDelay end
                config.minDelay = minDelay.v
                saveConfig()
            end
            
            imgui.Text(u8('Максимальная задержка (мс):'))
            if imgui.InputInt(u8('##maxdelay'), maxDelay) then
                if maxDelay.v < config.minDelay then maxDelay.v = config.minDelay end
                if maxDelay.v > 60000 then maxDelay.v = 60000 end
                config.maxDelay = maxDelay.v
                saveConfig()
            end
        end
        
        imgui.Separator()
        
        -- Поворот камеры
        if imgui.Checkbox(u8('Поворот камеры'), useCameraRotation) then
            config.useCameraRotation = useCameraRotation.v
            saveConfig()
        end
        
        -- Анимация
        if imgui.Checkbox(u8('Использовать анимацию (/me)'), useAnimation) then
            config.useAnimation = useAnimation.v
            saveConfig()
        end
        
        -- Движение
        if imgui.Checkbox(u8('Использовать движение'), useMovement) then
            config.useMovement = useMovement.v
            saveConfig()
        end
        
        imgui.Separator()
        
        -- Статус
        if config.enabled then
            local timeUntilNext = math.max(0, math.floor((nextActionTime - os.clock() * 1000) / 1000))
            imgui.TextColored(imgui.ImVec4(0, 1, 0, 1), u8('Статус: Активен'))
            imgui.Text(u8('Следующее действие через: ' .. timeUntilNext .. ' сек'))
        else
            imgui.TextColored(imgui.ImVec4(1, 0, 0, 1), u8('Статус: Выключен'))
        end
        
        imgui.Separator()
        
        -- Кнопка закрытия
        if imgui.Button(u8('Закрыть'), imgui.ImVec2(-1, 0)) then
            window.v = false
            menuOpen = false
        end
        
        imgui.End()
    end)
end
