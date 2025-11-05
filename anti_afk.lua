script_author('Cosmo & ported by t.me/monetbinder (@osp_x)')
script_description('ShitCode Prodakshen')
local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

local config = {
    enabled = true,
    timeout = 120000, -- время в мс до активации (по умолчанию 2 минуты)
    action_type = 1, -- 1 - движение, 2 - прыжок, 3 - анимация
    move_distance = 1.0, -- расстояние для движения
    show_notification = true,
    keybind = 0 -- 0 = нет клавиши, используйте VK коды
}

local config_path = getWorkingDirectory() .. '\\config\\anti_afk.ini'

local function loadConfig()
    if doesFileExist(config_path) then
        local ini = inicfg.load(config_path)
        if ini and ini.main then
            config.enabled = ini.main.enabled or config.enabled
            config.timeout = ini.main.timeout or config.timeout
            config.action_type = ini.main.action_type or config.action_type
            config.move_distance = ini.main.move_distance or config.move_distance
            config.show_notification = ini.main.show_notification ~= nil and ini.main.show_notification or config.show_notification
            config.keybind = ini.main.keybind or config.keybind
        end
    end
end

local function saveConfig()
    local ini = inicfg.new({
        main = config
    })
    inicfg.save(ini, config_path)
end

local last_activity = 0
local is_afk_active = false

local function getCurrentTime()
    return os.clock() * 1000
end

local function updateActivity()
    last_activity = getCurrentTime()
    is_afk_active = false
end

local function performAntiAfkAction()
    if is_afk_active then return end
    
    is_afk_active = true
    
    if config.action_type == 1 then -- Движение
        local x, y, z = getCharCoordinates(PLAYER_PED)
        local angle = getCharHeading(PLAYER_PED)
        local rad = math.rad(angle)
        local new_x = x + math.sin(rad) * config.move_distance
        local new_y = y + math.cos(rad) * config.move_distance
        
        setCharCoordinates(PLAYER_PED, new_x, new_y, z)
        
        if config.show_notification then
            sampAddChatMessage(u8:decode('[Anti-AFK] Выполнено движение'), 0x00FF00)
        end
    elseif config.action_type == 2 then -- Прыжок
        taskJumpChar(PLAYER_PED, false)
        
        if config.show_notification then
            sampAddChatMessage(u8:decode('[Anti-AFK] Выполнен прыжок'), 0x00FF00)
        end
    elseif config.action_type == 3 then -- Анимация
        if not isCharPlayingAnim(PLAYER_PED, 'PED', 'IDLE_CHAT') then
            taskPlayAnimSecondary(PLAYER_PED, 'PED', 'IDLE_CHAT', 4.0, false, false, false, 0, 0)
            lua_thread.create(function()
                wait(2000)
                clearCharTasksImmediately(PLAYER_PED)
            end)
        end
        
        if config.show_notification then
            sampAddChatMessage(u8:decode('[Anti-AFK] Выполнена анимация'), 0x00FF00)
        end
    end
    
    updateActivity()
end

-- Отслеживание активности игрока
function se.onSendChat(message)
    updateActivity()
end

function se.onSendCommand(command)
    updateActivity()
end

function se.onSendKeyUp(key)
    updateActivity()
end

function se.onSendClick()
    updateActivity()
end

function se.onServerMessage(color, text)
    updateActivity()
end

function main()
    loadConfig()
    last_activity = getCurrentTime()
    
    sampRegisterChatCommand('afk', function()
        config.enabled = not config.enabled
        saveConfig()
        local status = config.enabled and u8:decode('включен') or u8:decode('выключен')
        sampAddChatMessage(u8:decode('[Anti-AFK] ' .. status), 0x00FF00)
    end)
    
    sampRegisterChatCommand('afkconfig', function()
        sampAddChatMessage(u8:decode('[Anti-AFK] Настройки:'), 0x00FF00)
        sampAddChatMessage(u8:decode('Включен: ' .. tostring(config.enabled)), 0xFFFFFF)
        sampAddChatMessage(u8:decode('Таймаут: ' .. config.timeout .. ' мс'), 0xFFFFFF)
        sampAddChatMessage(u8:decode('Тип действия: ' .. config.action_type .. ' (1-движение, 2-прыжок, 3-анимация)'), 0xFFFFFF)
        sampAddChatMessage(u8:decode('Расстояние движения: ' .. config.move_distance), 0xFFFFFF)
        sampAddChatMessage(u8:decode('Настройки в файле: ' .. config_path), 0xFFFFFF)
    end)
    
    while true do
        wait(1000)
        
        if config.enabled then
            local current_time = getCurrentTime()
            local time_since_activity = current_time - last_activity
            
            if time_since_activity >= config.timeout then
                performAntiAfkAction()
            end
        end
    end
end
