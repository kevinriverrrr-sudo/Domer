-- SAMP MoonLoader Cheat Script
-- Features: Auto +C (Aimbot), Aim Assist, WallHack, Rvanka (No Recoil), Fly

local imgui = require 'imgui'
local encoding = require 'encoding'
encoding.default = 'CP1251'
local u8 = encoding.UTF8

-- Настройки
local config = {
    enabled = true,
    autoAim = false,
    aimAssist = false,
    wallHack = false,
    noRecoil = false,
    fly = false,
    aimKey = 0x43, -- C key
    flySpeed = 0.5,
    aimDistance = 50.0,
    aimFOV = 90.0,
    showMenu = false
}

-- Состояние
local state = {
    targetPlayer = nil,
    flyEnabled = false,
    flyZ = 0.0,
    lastShotTime = 0
}

-- Функция для получения игроков
function getPlayers()
    if not sampIsLocalPlayerSpawned() then return {} end
    
    local players = {}
    local maxPlayers = sampGetPlayerPoolSize()
    local myPed = PLAYER_PED
    local myPos = {getCharCoordinates(myPed)}
    
    for i = 0, maxPlayers do
        if sampIsPlayerConnected(i) and i ~= sampGetLocalPlayerId() then
            if sampIsPlayerSpawned(i) then
                local ped = sampGetCharHandleBySampPlayerId(i)
                if ped and ped ~= 0 then
                    local charPos = {getCharCoordinates(ped)}
                    local distance = getDistanceBetweenCoords3d(myPos[1], myPos[2], myPos[3], charPos[1], charPos[2], charPos[3])
                    table.insert(players, {
                        id = i,
                        ped = ped,
                        pos = charPos,
                        distance = distance
                    })
                end
            end
        end
    end
    
    return players
end

-- Вычисление угла между векторами
function getAngleBetween(coords1, coords2, camRot)
    local dx = coords2[1] - coords1[1]
    local dy = coords2[2] - coords1[2]
    local dz = coords2[3] - coords1[3]
    
    local distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance < 0.1 then return 180 end
    
    local dirX = dx / distance
    local dirY = dy / distance
    local dirZ = dz / distance
    
    local camPitch = math.rad(camRot[1])
    local camYaw = math.rad(camRot[2])
    
    local forwardX = math.cos(camPitch) * math.cos(camYaw)
    local forwardY = math.cos(camPitch) * math.sin(camYaw)
    local forwardZ = math.sin(camPitch)
    
    local dot = dirX * forwardX + dirY * forwardY + dirZ * forwardZ
    local angle = math.acos(math.max(-1, math.min(1, dot)))
    
    return math.deg(angle)
end

-- Поиск ближайшего игрока в FOV
function findNearestPlayer()
    if not sampIsLocalPlayerSpawned() then return nil end
    
    local players = getPlayers()
    if #players == 0 then return nil end
    
    local myPed = PLAYER_PED
    local myPos = {getCharCoordinates(myPed)}
    local cameraPos = {getGameCamPos()}
    local cameraRot = {getGameCamRot()}
    
    local bestPlayer = nil
    local bestDistance = config.aimDistance
    local bestAngle = config.aimFOV
    
    for _, player in ipairs(players) do
        if player.distance <= config.aimDistance then
            local angle = getAngleBetween(cameraPos, player.pos, cameraRot)
            
            if angle <= bestAngle then
                bestAngle = angle
                bestDistance = player.distance
                bestPlayer = player
            end
        end
    end
    
    return bestPlayer
end

-- Авто-аим (Aimbot)
function autoAim()
    if not config.autoAim then return end
    if not sampIsLocalPlayerSpawned() then return end
    
    local target = findNearestPlayer()
    if not target then return end
    
    local myPed = PLAYER_PED
    local targetPos = target.pos
    local myPos = {getCharCoordinates(myPed)}
    
    -- Вычисляем угол для аима
    local dx = targetPos[1] - myPos[1]
    local dy = targetPos[2] - myPos[2]
    local dz = (targetPos[3] + 0.5) - (myPos[3] + 0.5) -- Немного выше для хедшота
    
    local distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance < 0.1 then return end
    
    local pitch = math.asin(dz / distance)
    local yaw = math.atan2(dy, dx)
    
    -- Применяем аим через педа
    pointCharAtCoord(myPed, targetPos[1], targetPos[2], targetPos[3] + 0.5)
    
    -- Также корректируем камеру
    local newPitch = math.deg(pitch)
    local newYaw = math.deg(yaw)
    setGameCamRot(newPitch, newYaw, 0.0, 2)
end

-- Aim Assist
function aimAssist()
    if not config.aimAssist then return end
    if not sampIsLocalPlayerSpawned() then return end
    
    local target = findNearestPlayer()
    if not target then return end
    
    local myPed = PLAYER_PED
    local targetPos = target.pos
    local myPos = {getCharCoordinates(myPed)}
    
    local dx = targetPos[1] - myPos[1]
    local dy = targetPos[2] - myPos[2]
    local dz = (targetPos[3] + 0.5) - (myPos[3] + 0.5)
    
    local distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance < 0.1 then return end
    
    local pitch = math.asin(dz / distance)
    local yaw = math.atan2(dy, dx)
    
    -- Мягкий аим (20% силы)
    local currentRot = {getGameCamRot()}
    local newPitch = currentRot[1] + (math.deg(pitch) - currentRot[1]) * 0.2
    local newYaw = currentRot[2] + (math.deg(yaw) - currentRot[2]) * 0.2
    
    setGameCamRot(newPitch, newYaw, 0.0, 2)
end

-- WallHack (ESP) - рисование через samp.* функции
function drawWallHack()
    if not config.wallHack then return end
    if not sampIsLocalPlayerSpawned() then return end
    
    local players = getPlayers()
    if #players == 0 then return end
    
    local myPed = PLAYER_PED
    local myPos = {getCharCoordinates(myPed)}
    
    for _, player in ipairs(players) do
        if player.distance <= 100.0 then
            local targetPos = player.pos
            
            -- Конвертируем 3D координаты в экранные
            local screenX, screenY = convert3DCoordsToScreen(targetPos[1], targetPos[2], targetPos[3] + 1.0)
            
            if screenX and screenY and screenX > 0 and screenY > 0 then
                -- Рисуем линию от игрока к цели
                local myScreenX, myScreenY = convert3DCoordsToScreen(myPos[1], myPos[2], myPos[3] + 0.5)
                if myScreenX and myScreenY then
                    drawLine(myScreenX, myScreenY, screenX, screenY, 255, 0, 0, 255)
                end
                
                -- Рисуем имя игрока
                local playerName = sampGetPlayerNickname(player.id)
                if playerName then
                    drawText(playerName, screenX, screenY - 20, 255, 255, 255, 255)
                end
                
                -- Рисуем дистанцию
                drawText(string.format("%.1fm", player.distance), screenX, screenY - 5, 255, 255, 0, 255)
                
                -- Рисуем бокс
                local boxSize = 20.0 / player.distance * 10
                drawBox(screenX - boxSize/2, screenY - boxSize/2, boxSize, boxSize, 0, 255, 0, 150)
            end
        end
    end
end

-- Rvanka (No Recoil) - убираем отдачу
function noRecoil()
    if not config.noRecoil then return end
    if not sampIsLocalPlayerSpawned() then return end
    
    local myPed = PLAYER_PED
    if not isCharInAnyCar(myPed) then
        local weapon = getCurrentCharWeapon(myPed)
        if weapon ~= 0 then
            -- Сохраняем позицию камеры до выстрела
            if isCharShooting(myPed) then
                local camRot = {getGameCamRot()}
                state.lastShotTime = os.clock()
                
                -- Сбрасываем отдачу через небольшой интервал
                wait(5)
                setGameCamRot(camRot[1], camRot[2], camRot[3], 2)
            end
        end
    end
end

-- Fly Hack
function flyHack()
    if not config.fly then return end
    
    local myPed = PLAYER_PED
    if not sampIsLocalPlayerSpawned() then return end
    
    local pos = {getCharCoordinates(myPed)}
    
    if not state.flyEnabled then
        state.flyZ = pos[3]
        state.flyEnabled = true
    end
    
    -- Управление высотой
    if isKeyPressed(0x57) and isKeyPressed(0x10) then -- W + Shift (вверх)
        state.flyZ = state.flyZ + config.flySpeed
    elseif isKeyPressed(0x53) and isKeyPressed(0x10) then -- S + Shift (вниз)
        state.flyZ = state.flyZ - config.flySpeed
    end
    
    -- Получаем направление камеры
    local camRot = {getGameCamRot()}
    local pitch = math.rad(camRot[1])
    local yaw = math.rad(camRot[2])
    
    local forwardX = math.cos(pitch) * math.cos(yaw)
    local forwardY = math.cos(pitch) * math.sin(yaw)
    local forwardZ = math.sin(pitch)
    
    local rightX = math.cos(yaw + math.pi/2)
    local rightY = math.sin(yaw + math.pi/2)
    
    local moveX, moveY, moveZ = 0, 0, 0
    
    -- Движение вперед/назад
    if isKeyPressed(0x57) then -- W
        moveX = moveX + forwardX * config.flySpeed
        moveY = moveY + forwardY * config.flySpeed
    end
    if isKeyPressed(0x53) then -- S
        moveX = moveX - forwardX * config.flySpeed
        moveY = moveY - forwardY * config.flySpeed
    end
    
    -- Движение влево/вправо
    if isKeyPressed(0x41) then -- A
        moveX = moveX - rightX * config.flySpeed
        moveY = moveY - rightY * config.flySpeed
    end
    if isKeyPressed(0x44) then -- D
        moveX = moveX + rightX * config.flySpeed
        moveY = moveY + rightY * config.flySpeed
    end
    
    -- Применяем движение
    if moveX ~= 0 or moveY ~= 0 or state.flyZ ~= pos[3] then
        setCharCoordinates(myPed, pos[1] + moveX, pos[2] + moveY, state.flyZ)
        -- Убираем гравитацию и скорость
        setCharVelocity(myPed, 0.0, 0.0, 0.0)
    end
end

-- Вспомогательные функции для рисования
function drawLine(x1, y1, x2, y2, r, g, b, a)
    if not x1 or not y1 or not x2 or not y2 then return end
    drawLineOnScreen(x1, y1, x2, y2, r, g, b, a)
end

function drawText(text, x, y, r, g, b, a)
    if not text or not x or not y then return end
    drawTextOnScreen(text, x, y, 0.4, r, g, b, a)
end

function drawBox(x, y, w, h, r, g, b, a)
    if not x or not y then return end
    drawBoxOnScreen(x, y, w, h, r, g, b, a)
end

-- Главный цикл
function main()
    if not sampIsSampLoaded() then
        wait(1000)
        return
    end
    
    while not sampIsLocalPlayerSpawned() do
        wait(100)
    end
    
    sampAddChatMessage(u8'SAMP Cheat загружен! Нажмите INSERT для меню', 0x00FF00)
    
    while true do
        wait(0)
        
        -- Меню по Insert
        if wasKeyPressed(0x2D) then -- INSERT
            config.showMenu = not config.showMenu
        end
        
        if config.enabled then
            -- Проверка клавиши C для авто-аима
            if isKeyPressed(config.aimKey) then
                if config.autoAim then
                    autoAim()
                end
            end
            
            -- Aim Assist
            if config.aimAssist then
                aimAssist()
            end
            
            -- WallHack
            if config.wallHack then
                drawWallHack()
            end
            
            -- No Recoil
            if config.noRecoil then
                noRecoil()
            end
            
            -- Fly
            if config.fly then
                flyHack()
            end
        end
    end
end

-- GUI меню
function imgui.OnDrawFrame()
    if not config.showMenu then return end
    
    imgui.SetNextWindowPos(imgui.ImVec2(50, 50), imgui.Cond.FirstUseEver)
    imgui.SetNextWindowSize(imgui.ImVec2(300, 450), imgui.Cond.FirstUseEver)
    
    imgui.Begin(u8' SAMP Cheat Menu', config.showMenu)
    
    if imgui.Checkbox(u8'Включить', config.enabled) then
        config.enabled = not config.enabled
    end
    
    imgui.Separator()
    
    if imgui.Checkbox(u8'Auto Aim (+C)', config.autoAim) then
        config.autoAim = not config.autoAim
    end
    
    if imgui.Checkbox(u8'Aim Assist', config.aimAssist) then
        config.aimAssist = not config.aimAssist
    end
    
    if imgui.Checkbox(u8'WallHack (ESP)', config.wallHack) then
        config.wallHack = not config.wallHack
    end
    
    if imgui.Checkbox(u8'No Recoil (Rvanka)', config.noRecoil) then
        config.noRecoil = not config.noRecoil
    end
    
    if imgui.Checkbox(u8'Fly', config.fly) then
        config.fly = not config.fly
        if not config.fly then
            state.flyEnabled = false
        end
    end
    
    imgui.Separator()
    
    imgui.Text(u8'Настройки Fly:')
    local changed, speed = imgui.SliderFloat(u8'Скорость полета', config.flySpeed, 0.1, 5.0)
    if changed then
        config.flySpeed = speed
    end
    
    imgui.Separator()
    
    imgui.Text(u8'Настройки Aim:')
    local changed1, dist = imgui.SliderFloat(u8'Дистанция', config.aimDistance, 10.0, 200.0)
    if changed1 then
        config.aimDistance = dist
    end
    
    local changed2, fov = imgui.SliderFloat(u8'FOV', config.aimFOV, 10.0, 180.0)
    if changed2 then
        config.aimFOV = fov
    end
    
    imgui.Separator()
    imgui.Text(u8'Управление:')
    imgui.Text(u8'INSERT - Меню')
    imgui.Text(u8'C - Auto Aim')
    imgui.Text(u8'WASD - Fly')
    imgui.Text(u8'W/S + Shift - Вверх/Вниз')
    
    imgui.End()
end

-- Запуск
main()
