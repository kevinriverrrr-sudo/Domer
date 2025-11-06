--[[
    AimBot для SAMP (MonetLoader)
    Автор: AI Assistant
    Версия: 1.0
]]

local imgui = require 'mimgui'
local encoding = require 'encoding'
encoding.default = "CP1251"
local u8 = encoding.UTF8

local jsoncfg = require 'jsoncfg'
local widgets = require 'widgets'
local ffi = require 'ffi'
local memory = require 'memory'
local samp = require 'sampfuncs'
local sampev = require 'samp.events'
local sa_renderfix = require 'sa_renderfix'

-- Конфигурация
local config = jsoncfg.new('AimBot.json', {
    enabled = false,
    autoAim = true,
    smoothAim = true,
    smoothSpeed = 0.15,
    maxDistance = 50.0,
    fov = 60.0,
    targetBone = 6, -- 6 = голова (BONE_HEAD), 3 = тело (BONE_SPINE1)
    aimKey = 0x02, -- Правая кнопка мыши
    showMenu = true,
    showESP = true,
    showFOV = true,
    teamFilter = false,
    ignoreFriends = true,
    prediction = true,
    aimHeight = 0.0,
    lockTarget = false,
    autoShoot = false,
    shootDelay = 100
})

-- Состояние меню
local menuState = imgui.ImBool(false)
local espState = imgui.ImBool(config.showESP)
local fovState = imgui.ImBool(config.showFOV)

-- Переменные
local currentTarget = nil
local targetLocked = false
local lastShootTime = 0
local aimbotEnabled = imgui.ImBool(config.enabled)
local autoAimEnabled = imgui.ImBool(config.autoAim)
local smoothAimEnabled = imgui.ImBool(config.smoothAim)
local teamFilterEnabled = imgui.ImBool(config.teamFilter)
local ignoreFriendsEnabled = imgui.ImBool(config.ignoreFriends)
local predictionEnabled = imgui.ImBool(config.prediction)
local lockTargetEnabled = imgui.ImBool(config.lockTarget)
local autoShootEnabled = imgui.ImBool(config.autoShoot)

-- Слайдеры
local smoothSpeedSlider = imgui.ImFloat(config.smoothSpeed)
local maxDistanceSlider = imgui.ImFloat(config.maxDistance)
local fovSlider = imgui.ImFloat(config.fov)
local aimHeightSlider = imgui.ImFloat(config.aimHeight)
local shootDelaySlider = imgui.ImInt(config.shootDelay)
local targetBoneCombo = imgui.ImInt(0) -- 0 = Голова по умолчанию

-- Табы меню
local currentTab = imgui.ImInt(0)
local tabNames = {u8"Основные", u8"Настройки", u8"Визуал", u8"О программе"}

-- Цвета
local colors = {
    primary = imgui.ImVec4(0.2, 0.6, 1.0, 1.0),
    success = imgui.ImVec4(0.2, 0.8, 0.2, 1.0),
    danger = imgui.ImVec4(1.0, 0.2, 0.2, 1.0),
    warning = imgui.ImVec4(1.0, 0.8, 0.0, 1.0),
    text = imgui.ImVec4(1.0, 1.0, 1.0, 1.0),
    bg = imgui.ImVec4(0.1, 0.1, 0.15, 0.95)
}

-- Функции
function getDistance3D(x1, y1, z1, x2, y2, z2)
    return math.sqrt((x2 - x1)^2 + (y2 - y1)^2 + (z2 - z1)^2)
end

function getDistance2D(x1, y1, x2, y2)
    return math.sqrt((x2 - x1)^2 + (y2 - y1)^2)
end

function getAngleToPoint(fromX, fromY, toX, toY)
    local dx = toX - fromX
    local dy = toY - fromY
    local angle = math.atan2(dy, dx) * 180.0 / math.pi
    return angle
end

function getClosestPlayer()
    if not sampIsLocalPlayerSpawned() then return nil end
    
    local myX, myY, myZ = getCharCoordinates(PLAYER_PED)
    local myId = sampGetMyId()
    local closestPlayer = nil
    local closestDistance = config.maxDistance
    
    for i = 0, 1000 do
        if sampIsPlayerConnected(i) and i ~= myId and sampIsPlayerSpawned(i) then
            local streamed, ped = sampGetCharHandleBySampPlayerId(i)
            if streamed and ped and ped ~= 0 then
                local playerX, playerY, playerZ = getCharCoordinates(ped)
                local distance = getDistance3D(myX, myY, myZ, playerX, playerY, playerZ)
                
                if distance <= config.maxDistance and distance < closestDistance then
                    -- Проверка команды
                    if config.teamFilter then
                        local myTeam = sampGetPlayerTeamId(myId)
                        local targetTeam = sampGetPlayerTeamId(i)
                        if myTeam == targetTeam then
                            goto continue
                        end
                    end
                    
                    -- Проверка друзей
                    if config.ignoreFriends then
                        if sampIsPlayerFriend(i) then
                            goto continue
                        end
                    end
                    
                    closestPlayer = i
                    closestDistance = distance
                end
            end
            ::continue::
        end
    end
    
    return closestPlayer, closestDistance
end

function getBonePosition(playerId, boneId)
    local streamed, ped = sampGetCharHandleBySampPlayerId(playerId)
    if not streamed or not ped or ped == 0 then return nil end
    
    local bonePos = ffi.new('float[3]')
    if getBonePosition(ped, boneId, bonePos) then
        return bonePos[0], bonePos[1], bonePos[2]
    end
    
    -- Fallback на координаты персонажа
    return getCharCoordinates(ped)
end

function worldToScreen(x, y, z)
    local screenX = ffi.new('float[1]')
    local screenY = ffi.new('float[1]')
    local screenZ = ffi.new('float[1]')
    
    if convert3DCoordsToScreen(x, y, z, screenX, screenY, screenZ) then
        local resX, resY = getScreenResolution()
        return screenX[0] * resX, screenY[0] * resY, screenZ[0]
    end
    return nil, nil, nil
end

-- Альтернативная функция для получения координат экрана
function worldToScreen2(x, y, z)
    local resX, resY = getScreenResolution()
    local screenX, screenY = convertWorldScreenCoord(x, y, z)
    if screenX and screenY then
        return screenX * resX, screenY * resY, 0
    end
    return nil, nil, nil
end

function aimAtTarget(playerId)
    if not playerId or not sampIsPlayerSpawned(playerId) then return false end
    
    local myX, myY, myZ = getCharCoordinates(PLAYER_PED)
    local boneId = config.targetBone
    
    local targetX, targetY, targetZ = getBonePosition(playerId, boneId)
    if not targetX then
        -- Fallback на координаты игрока
        local streamed, ped = sampGetCharHandleBySampPlayerId(playerId)
        if streamed and ped then
            targetX, targetY, targetZ = getCharCoordinates(ped)
        else
            return false
        end
    end
    
    targetZ = targetZ + config.aimHeight
    
    -- Предсказание движения
    if config.prediction then
        local streamed, ped = sampGetCharHandleBySampPlayerId(playerId)
        if streamed and ped then
            local vx, vy, vz = getCharVelocity(ped)
            local distance = getDistance3D(myX, myY, myZ, targetX, targetY, targetZ)
            local timeToTarget = distance / 1000.0 -- Примерное время полета пули
            
            targetX = targetX + vx * timeToTarget
            targetY = targetY + vy * timeToTarget
            targetZ = targetZ + vz * timeToTarget
        end
    end
    
    -- Вычисление углов
    local dx = targetX - myX
    local dy = targetY - myY
    local dz = targetZ - myZ
    
    local distance2D = math.sqrt(dx * dx + dy * dy)
    local angleZ = math.atan2(dz, distance2D) * 180.0 / math.pi
    local angleXY = math.atan2(dy, dx) * 180.0 / math.pi
    
    -- Плавное наведение
    if config.smoothAim then
        local currentHeading = getCharHeading(PLAYER_PED)
        local smooth = config.smoothSpeed
        
        -- Нормализация углов
        local angleDiff = angleXY - currentHeading
        while angleDiff > 180 do angleDiff = angleDiff - 360 end
        while angleDiff < -180 do angleDiff = angleDiff + 360 end
        
        angleXY = currentHeading + angleDiff * smooth
    end
    
    -- Установка угла поворота
    setCharHeading(PLAYER_PED, angleXY)
    
    -- Установка угла камеры (вертикальный)
    -- Используем простой способ через установку направления взгляда
    local camX = myX + math.cos(math.rad(angleXY)) * math.cos(math.rad(angleZ)) * 10
    local camY = myY + math.sin(math.rad(angleXY)) * math.cos(math.rad(angleZ)) * 10
    local camZ = myZ + math.sin(math.rad(angleZ)) * 10
    
    pointCameraAtCoord(camX, camY, camZ)
    
    return true
end

function isInFOV(playerId)
    if not config.showFOV then return true end
    
    local streamed, ped = sampGetCharHandleBySampPlayerId(playerId)
    if not streamed or not ped then return false end
    
    local targetX, targetY, targetZ = getCharCoordinates(ped)
    local screenX, screenY = worldToScreen(targetX, targetY, targetZ)
    if not screenX then 
        -- Попробуем альтернативный метод
        screenX, screenY = worldToScreen2(targetX, targetY, targetZ)
        if not screenX then return false end
    end
    
    local resX, resY = getScreenResolution()
    local centerX, centerY = resX / 2, resY / 2
    
    local distance = getDistance2D(centerX, centerY, screenX, screenY)
    local fovRadius = (resY / 2) * (config.fov / 90.0)
    
    return distance <= fovRadius
end

function drawESP()
    if not config.showESP then return end
    
    local myId = sampGetMyId()
    local myX, myY, myZ = getCharCoordinates(PLAYER_PED)
    
    for i = 0, 1000 do
        if sampIsPlayerConnected(i) and i ~= myId and sampIsPlayerSpawned(i) then
            local streamed, ped = sampGetCharHandleBySampPlayerId(i)
            if streamed and ped then
                local playerX, playerY, playerZ = getCharCoordinates(ped)
                local distance = getDistance3D(myX, myY, myZ, playerX, playerY, playerZ)
                
                if distance <= config.maxDistance then
                    local screenX, screenY = worldToScreen(playerX, playerY, playerZ)
                    if not screenX then
                        screenX, screenY = worldToScreen2(playerX, playerY, playerZ)
                    end
                    
                    if screenX then
                        local resX, resY = getScreenResolution()
                        local color = i == currentTarget and colors.danger or colors.primary
                        
                        -- Линия к игроку
                        drawLine(screenX, screenY, resX / 2, resY / 2, 
                                math.floor(color.x * 255), math.floor(color.y * 255), 
                                math.floor(color.z * 255), 200)
                        
                        -- Имя игрока
                        local playerName = sampGetPlayerNickname(i)
                        if playerName then
                            drawText(playerName, screenX, screenY - 20, 
                                    math.floor(colors.text.x * 255), 
                                    math.floor(colors.text.y * 255), 
                                    math.floor(colors.text.z * 255), 255)
                        end
                        
                        -- Дистанция
                        local distText = string.format("%.1fm", distance)
                        drawText(distText, screenX, screenY - 5, 
                                math.floor(colors.text.x * 255), 
                                math.floor(colors.text.y * 255), 
                                math.floor(colors.text.z * 255), 255)
                    end
                end
            end
        end
    end
end

function drawFOVCircle()
    if not config.showFOV then return end
    
    local resX, resY = getScreenResolution()
    local centerX, centerY = resX / 2, resY / 2
    local radius = (resY / 2) * (config.fov / 90.0)
    
    local r = math.floor(colors.warning.x * 255)
    local g = math.floor(colors.warning.y * 255)
    local b = math.floor(colors.warning.z * 255)
    
    -- Рисуем круг FOV
    for i = 0, 360, 2 do
        local angle1 = i * math.pi / 180
        local angle2 = (i + 2) * math.pi / 180
        local x1 = centerX + radius * math.cos(angle1)
        local y1 = centerY + radius * math.sin(angle1)
        local x2 = centerX + radius * math.cos(angle2)
        local y2 = centerY + radius * math.sin(angle2)
        
        drawLine(x1, y1, x2, y2, r, g, b, 150)
    end
end

-- Основной цикл
function main()
    while not isSampAvailable() do wait(100) end
    
    sampRegisterChatCommand('aimbot', function()
        menuState.v = not menuState.v
        imgui.Process = menuState.v
    end)
    
    sampRegisterChatCommand('aim', function()
        config.enabled = not config.enabled
        aimbotEnabled.v = config.enabled
        jsoncfg.save(config)
        sampAddChatMessage(
            string.format("{32CD32}[AimBot] {FFFFFF}AimBot %s", config.enabled and "включен" or "выключен"),
            -1
        )
    end)
    
    while true do
        wait(0)
        
        -- Обновление конфига
        config.enabled = aimbotEnabled.v
        config.autoAim = autoAimEnabled.v
        config.smoothAim = smoothAimEnabled.v
        config.teamFilter = teamFilterEnabled.v
        config.ignoreFriends = ignoreFriendsEnabled.v
        config.prediction = predictionEnabled.v
        config.lockTarget = lockTargetEnabled.v
        config.autoShoot = autoShootEnabled.v
        config.smoothSpeed = smoothSpeedSlider.v
        config.maxDistance = maxDistanceSlider.v
        config.fov = fovSlider.v
        config.aimHeight = aimHeightSlider.v
        config.shootDelay = shootDelaySlider.v
        config.targetBone = targetBoneCombo.v
        config.showESP = espState.v
        config.showFOV = fovState.v
        
        -- Рисуем ESP и FOV
        if config.showESP or config.showFOV then
            drawESP()
            drawFOVCircle()
        end
        
        -- AimBot логика
        if config.enabled and sampIsLocalPlayerSpawned() then
            if config.autoAim or isKeyDown(config.aimKey) then
                local target, distance = getClosestPlayer()
                
                if target and isInFOV(target) then
                    if not targetLocked or not config.lockTarget then
                        currentTarget = target
                        targetLocked = true
                    end
                    
                    if currentTarget and sampIsPlayerSpawned(currentTarget) then
                        if aimAtTarget(currentTarget) then
                            -- Автострель
                            if config.autoShoot then
                                local currentTime = os.clock() * 1000
                                if currentTime - lastShootTime >= config.shootDelay then
                                    setGameKeyState(0, 128) -- ЛКМ (fire)
                                    wait(10)
                                    setGameKeyState(0, 0)
                                    lastShootTime = currentTime
                                end
                            end
                        end
                    end
                else
                    if not config.lockTarget then
                        currentTarget = nil
                        targetLocked = false
                    end
                end
            else
                if not config.lockTarget then
                    currentTarget = nil
                    targetLocked = false
                end
            end
        else
            currentTarget = nil
            targetLocked = false
        end
        
        -- Сохранение конфига при изменении
        if menuState.v then
            jsoncfg.save(config)
        end
    end
end

-- Меню
function imgui.OnDrawFrame()
    if not menuState.v then
        imgui.Process = false
        return
    end
    
    imgui.Process = true
    
    local resX, resY = getScreenResolution()
    imgui.SetNextWindowPos(imgui.ImVec2(resX / 2, resY / 2), imgui.Cond.FirstUseEver, imgui.ImVec2(0.5, 0.5))
    imgui.SetNextWindowSize(imgui.ImVec2(500, 600), imgui.Cond.FirstUseEver)
    
    imgui.PushStyleColor(imgui.Col.WindowBg, colors.bg)
    imgui.PushStyleColor(imgui.Col.TitleBg, colors.primary)
    imgui.PushStyleColor(imgui.Col.TitleBgActive, colors.primary)
    imgui.PushStyleColor(imgui.Col.Button, imgui.ImVec4(0.2, 0.5, 0.9, 1.0))
    imgui.PushStyleColor(imgui.Col.ButtonHovered, imgui.ImVec4(0.3, 0.6, 1.0, 1.0))
    imgui.PushStyleColor(imgui.Col.ButtonActive, imgui.ImVec4(0.1, 0.4, 0.8, 1.0))
    imgui.PushStyleColor(imgui.Col.FrameBg, imgui.ImVec4(0.2, 0.2, 0.25, 1.0))
    imgui.PushStyleColor(imgui.Col.FrameBgHovered, imgui.ImVec4(0.25, 0.25, 0.3, 1.0))
    imgui.PushStyleColor(imgui.Col.FrameBgActive, imgui.ImVec4(0.3, 0.3, 0.35, 1.0))
    imgui.PushStyleColor(imgui.Col.CheckMark, colors.success)
    imgui.PushStyleColor(imgui.Col.SliderGrab, colors.primary)
    imgui.PushStyleColor(imgui.Col.SliderGrabActive, colors.primary)
    
    imgui.Begin(u8'AimBot Menu', menuState, imgui.WindowFlags.NoCollapse)
    
    -- Табы
    imgui.BeginTabBar('Tabs')
    
    -- Вкладка "Основные"
    if imgui.BeginTabItem(u8'Основные') then
        currentTab.v = 0
        
        imgui.Spacing()
        imgui.TextColored(colors.primary, u8'? Основные настройки')
        imgui.Separator()
        imgui.Spacing()
        
        if imgui.Checkbox(u8'Включить AimBot', aimbotEnabled) then
            config.enabled = aimbotEnabled.v
            jsoncfg.save(config)
        end
        
        imgui.SameLine()
        local statusColor = aimbotEnabled.v and colors.success or colors.danger
        imgui.TextColored(statusColor, aimbotEnabled.v and u8'[ВКЛ]' or u8'[ВЫКЛ]')
        
        imgui.Spacing()
        
        if imgui.Checkbox(u8'Автоматическое наведение', autoAimEnabled) then
            config.autoAim = autoAimEnabled.v
            jsoncfg.save(config)
        end
        
        if imgui.Checkbox(u8'Плавное наведение', smoothAimEnabled) then
            config.smoothAim = smoothAimEnabled.v
            jsoncfg.save(config)
        end
        
        if imgui.Checkbox(u8'Закрепить цель', lockTargetEnabled) then
            config.lockTarget = lockTargetEnabled.v
            jsoncfg.save(config)
        end
        
        if imgui.Checkbox(u8'Автострель', autoShootEnabled) then
            config.autoShoot = autoShootEnabled.v
            jsoncfg.save(config)
        end
        
        imgui.Spacing()
        imgui.Separator()
        imgui.Spacing()
        
        imgui.TextColored(colors.primary, u8'?? Фильтры целей')
        imgui.Separator()
        imgui.Spacing()
        
        if imgui.Checkbox(u8'Фильтр по команде', teamFilterEnabled) then
            config.teamFilter = teamFilterEnabled.v
            jsoncfg.save(config)
        end
        
        if imgui.Checkbox(u8'Игнорировать друзей', ignoreFriendsEnabled) then
            config.ignoreFriends = ignoreFriendsEnabled.v
            jsoncfg.save(config)
        end
        
        imgui.Spacing()
        
        if currentTarget then
            imgui.TextColored(colors.success, u8'Текущая цель: ' .. sampGetPlayerNickname(currentTarget))
        else
            imgui.TextColored(colors.warning, u8'Цель не найдена')
        end
        
        imgui.EndTabItem()
    end
    
    -- Вкладка "Настройки"
    if imgui.BeginTabItem(u8'Настройки') then
        currentTab.v = 1
        
        imgui.Spacing()
        imgui.TextColored(colors.primary, u8'? Параметры наведения')
        imgui.Separator()
        imgui.Spacing()
        
        imgui.Text(u8'Скорость плавности:')
        if imgui.SliderFloat(u8'##smooth', smoothSpeedSlider, 0.01, 1.0, '%.2f') then
            config.smoothSpeed = smoothSpeedSlider.v
            jsoncfg.save(config)
        end
        
        imgui.Text(u8'Максимальная дистанция:')
        if imgui.SliderFloat(u8'##distance', maxDistanceSlider, 5.0, 200.0, '%.1f м') then
            config.maxDistance = maxDistanceSlider.v
            jsoncfg.save(config)
        end
        
        imgui.Text(u8'Угол обзора (FOV):')
        if imgui.SliderFloat(u8'##fov', fovSlider, 10.0, 180.0, '%.1f°') then
            config.fov = fovSlider.v
            jsoncfg.save(config)
        end
        
        imgui.Text(u8'Высота прицела:')
        if imgui.SliderFloat(u8'##height', aimHeightSlider, -1.0, 1.0, '%.2f м') then
            config.aimHeight = aimHeightSlider.v
            jsoncfg.save(config)
        end
        
        imgui.Spacing()
        imgui.Separator()
        imgui.Spacing()
        
        imgui.TextColored(colors.primary, u8'?? Настройки цели')
        imgui.Separator()
        imgui.Spacing()
        
        imgui.Text(u8'Кость для прицела:')
        local bones = {u8'Голова (6)', u8'Шея (5)', u8'Тело (3)', u8'Грудь (4)', u8'Живот (2)'}
        local boneIds = {6, 5, 3, 4, 2}
        
        -- Находим текущий индекс кости
        local currentBoneIndex = 0
        for i, boneId in ipairs(boneIds) do
            if boneId == config.targetBone then
                currentBoneIndex = i - 1
                break
            end
        end
        targetBoneCombo.v = currentBoneIndex
        
        if imgui.Combo(u8'##bone', targetBoneCombo, bones, #bones) then
            config.targetBone = boneIds[targetBoneCombo.v + 1] or 6
            jsoncfg.save(config)
        end
        
        if imgui.Checkbox(u8'Предсказание движения', predictionEnabled) then
            config.prediction = predictionEnabled.v
            jsoncfg.save(config)
        end
        
        imgui.Spacing()
        imgui.Separator()
        imgui.Spacing()
        
        imgui.TextColored(colors.primary, u8'?? Настройки стрельбы')
        imgui.Separator()
        imgui.Spacing()
        
        imgui.Text(u8'Задержка стрельбы:')
        if imgui.SliderInt(u8'##shootdelay', shootDelaySlider, 50, 500, '%d мс') then
            config.shootDelay = shootDelaySlider.v
            jsoncfg.save(config)
        end
        
        imgui.EndTabItem()
    end
    
    -- Вкладка "Визуал"
    if imgui.BeginTabItem(u8'Визуал') then
        currentTab.v = 2
        
        imgui.Spacing()
        imgui.TextColored(colors.primary, u8'?? Визуальные эффекты')
        imgui.Separator()
        imgui.Spacing()
        
        if imgui.Checkbox(u8'Показать ESP', espState) then
            config.showESP = espState.v
            jsoncfg.save(config)
        end
        
        if imgui.Checkbox(u8'Показать FOV круг', fovState) then
            config.showFOV = fovState.v
            jsoncfg.save(config)
        end
        
        imgui.Spacing()
        imgui.Separator()
        imgui.Spacing()
        
        imgui.TextColored(colors.warning, u8'ESP показывает линии к игрокам')
        imgui.TextColored(colors.warning, u8'FOV показывает область поиска целей')
        
        imgui.EndTabItem()
    end
    
    -- Вкладка "О программе"
    if imgui.BeginTabItem(u8'О программе') then
        currentTab.v = 3
        
        imgui.Spacing()
        imgui.TextColored(colors.primary, u8'AimBot для SAMP')
        imgui.Separator()
        imgui.Spacing()
        
        imgui.Text(u8'Версия: 1.0')
        imgui.Text(u8'Платформа: MonetLoader')
        imgui.Spacing()
        
        imgui.TextColored(colors.success, u8'Команды:')
        imgui.BulletText(u8'/aimbot - Открыть меню')
        imgui.BulletText(u8'/aim - Включить/выключить AimBot')
        
        imgui.Spacing()
        imgui.Separator()
        imgui.Spacing()
        
        imgui.TextColored(colors.warning, u8'? Используйте на свой страх и риск!')
        
        imgui.EndTabItem()
    end
    
    imgui.EndTabBar()
    
    imgui.Spacing()
    imgui.Separator()
    
    if imgui.Button(u8'Закрыть', imgui.ImVec2(-1, 0)) then
        menuState.v = false
        imgui.Process = false
    end
    
    imgui.End()
    imgui.PopStyleColor(13)
end
