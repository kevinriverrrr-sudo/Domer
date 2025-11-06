local imgui = require('mimgui')
local vector = require('vector3d')
local faicons = require('fAwesome6')
local sampev = require('lib.samp.events')
local encoding = require('encoding')
encoding.default = 'CP1251'
u8 = encoding.UTF8

require("moonloader")
local inicfg = require 'inicfg'
local settings = inicfg.load({
    orvn = {
        speed = 1,
        dist = 25,
        active = false,
        coord = false,
        ignorecar = false,
        slapper = false,
        rotate = false,
        minusZ = 0,
        rAnim = false,
        rQuant = false,
        invisDist = 49,
        invisZPos = 1000
    },
    vrvn = {
        active = false,
        speed = 0.2,
        coord = false,
        ncoord = false,
        dist = 25,
        slapper = false,
        minusZ = 0,
        rQuant = false,
        rotate = false,
        invisPacket = 50,
        meteor = false,
        bypasscol = false,
        rpos = false
    },
    urvn = {
        rvanka = false,
        slapper = false,
        meteor = false,
        rotate = false,
        rollAndDirect = false,
        destroy = false,
        minusZ = 0,
        dist = 60,
    },
    settings = {
        drawCircle = true,
        drawLine = true,
        moveCircle = true,
        checker = true
    }
}, 'MRvanka.ini')
inicfg.save(settings, 'MRvanka.ini')

function save()
    inicfg.save(settings, 'MRvanka.ini')
end

local new = imgui.new
local packet, change = 0, false
local surfState = false

local MRvanka = {
    boost = false,
    orvn = {
        state = false,
        packet = 0,
        nop = false,
        speed = new.float(settings.orvn.speed),
        active = new.bool(settings.orvn.active),
        dist = new.float(settings.orvn.dist),
        coord = new.bool(settings.orvn.coord),
        ignorecar = new.bool(settings.orvn.ignorecar),
        packets = 0,
        slapper = new.bool(settings.orvn.slapper),
        rotate = new.bool(settings.orvn.rotate),
        minusZ = new.float(settings.orvn.minusZ),
        invisZ = new.bool(false),
        invisSurf = new.bool(false),
        rAnim = new.bool(settings.orvn.rAnim),
        rQuant = new.bool(settings.orvn.rQuant),
        invisDist = new.int(settings.orvn.invisDist),
        invisZState = false,
        invisSurfState = false,
        cid = -1,
        invisZPos = new.int(settings.orvn.invisZPos)
    },
    vrvn = {
        state = false,
        slapstate = false,
        meteorstate = false,
        active = new.bool(settings.vrvn.active),
        dist = new.float(settings.vrvn.dist),
        nop = false,
        coord = new.bool(settings.vrvn.coord),
        slapper = new.bool(settings.vrvn.slapper),
        meteor = new.bool(settings.vrvn.meteor),
        bypasscol = new.bool(settings.vrvn.bypasscol),
        minusZ = new.float(settings.vrvn.minusZ),
        invisZ = new.bool(false),
        invisSpawn = new.bool(false),
        rpos = new.bool(settings.vrvn.rpos),
        rQuant = new.bool(settings.vrvn.rQuant),
        rotate = new.bool(settings.vrvn.rotate),
        invisPacket = new.int(settings.vrvn.invisPacket),
        invisZState = false,
        invisSpawnState = false,
        invisPackets = 0,
        mxy = 0,
        mz = 0
    },
    urvn = {
        rvanka = new.bool(settings.urvn.rvanka),
        slapper = new.bool(settings.urvn.slapper),
        meteor = new.bool(settings.urvn.meteor),
        rotate = new.bool(settings.urvn.rotate),
        rollAndDirect = new.bool(settings.urvn.rollAndDirect),
        destroy = new.bool(settings.urvn.destroy),
        minusZ = new.float(settings.urvn.minusZ),
        dist = new.int(settings.urvn.dist),
        rvankaState = false,
        slapperState = false,
        meteorState = false,
        destroyState = false
    },
    other = {
        zgrug = 0.8,
        id = {},
        kicked = 0
    },
    settings = {
        drawCircle = new.bool(settings.settings.drawCircle),
        drawLine = new.bool(settings.settings.drawLine),
        moveCircle = new.bool(settings.settings.moveCircle),
        checker = new.bool(settings.settings.checker)
    },
    coord = {
        x = 0,
        y = 0,
        z = 0
    }
}

local renderWindow = imgui.new.bool(false)
local tab = 1
local menuAlpha = 0
local menuStartTime = 0
local menuActive = false

function msg(...) return sampAddChatMessage(string.format('{14d1db}[MRvanka]:{FFFFFF} %s', string.format(...)), -1) end

local menu = imgui.OnFrame(function() return renderWindow[0] end, function(player)
    local xw, yw = getScreenResolution()
    imgui.SetNextWindowPos(imgui.ImVec2(xw / 2, yw / 2), imgui.Cond.Always, imgui.ImVec2(0.5, 0.5))
    imgui.SetNextWindowSize(imgui.ImVec2(690, 380), imgui.Cond.Always)

    local timePassed = os.clock() - menuStartTime
    local fadeDuration = 0.2
    if menuActive then
        menuAlpha = math.min(timePassed / fadeDuration, 1)
    else
        menuAlpha = math.max(1 - (timePassed / fadeDuration), 0)
        if menuAlpha <= 0 then renderWindow[0] = false end
    end
    local gradientTop = imgui.ImVec4(0, 0, 0.2, 0.5 * menuAlpha)
    local gradientCenter = imgui.ImVec4(0, 0, 0, 0.5 * menuAlpha)
    local bg = imgui.GetBackgroundDrawList()
    bg:AddRectFilledMultiColor(imgui.ImVec2(0, 0), imgui.ImVec2(xw / 2, yw / 2),
        imgui.ColorConvertFloat4ToU32(gradientTop), imgui.ColorConvertFloat4ToU32(gradientTop),
        imgui.ColorConvertFloat4ToU32(gradientCenter), imgui.ColorConvertFloat4ToU32(gradientTop))
    bg:AddRectFilledMultiColor(imgui.ImVec2(xw / 2, 0), imgui.ImVec2(xw, yw / 2),
        imgui.ColorConvertFloat4ToU32(gradientTop), imgui.ColorConvertFloat4ToU32(gradientTop),
        imgui.ColorConvertFloat4ToU32(gradientTop), imgui.ColorConvertFloat4ToU32(gradientCenter))
    bg:AddRectFilledMultiColor(imgui.ImVec2(0, yw / 2), imgui.ImVec2(xw / 2, yw),
        imgui.ColorConvertFloat4ToU32(gradientTop), imgui.ColorConvertFloat4ToU32(gradientCenter),
        imgui.ColorConvertFloat4ToU32(gradientTop), imgui.ColorConvertFloat4ToU32(gradientTop))
    bg:AddRectFilledMultiColor(imgui.ImVec2(xw / 2, yw / 2), imgui.ImVec2(xw, yw),
        imgui.ColorConvertFloat4ToU32(gradientCenter), imgui.ColorConvertFloat4ToU32(gradientTop),
        imgui.ColorConvertFloat4ToU32(gradientTop), imgui.ColorConvertFloat4ToU32(gradientTop))
    bg:AddRectFilled(imgui.ImVec2(0, 0), imgui.ImVec2(xw, yw), imgui.ColorConvertFloat4ToU32(imgui.ImVec4(0, 0, 0, 0.7)), 0)

    imgui.PushStyleVarFloat(imgui.StyleVar.Alpha, menuAlpha)

    local names = {
        "OnFoot "..faicons("PERSON_WALKING"),
        "InCar "..faicons("car"),
        --"Unoccupied "..faicons("car"),
        "Invisible "..faicons("EYE_LOW_VISION"),
        "Settings "..faicons("gear"),
    }

    imgui.Begin("##multirvn", renderWindow, imgui.WindowFlags.NoTitleBar + imgui.WindowFlags.NoResize + imgui.WindowFlags.NoScrollbar)
    imgui.SetCursorPos(imgui.ImVec2((690/2.52), -45))
    local clrNormal = imgui.GetColorU32(imgui.Col.Button)
    local clrHover  = imgui.GetColorU32(imgui.Col.ButtonHovered)
    local clrActive = imgui.GetColorU32(imgui.Col.ButtonActive)

    imgui.SetCursorPos(imgui.ImVec2((690-40), 7))
    if imgui.RoundedRectButton(faicons("XMARK"), 25, 25, 8, clrNormal, clrHover, clrActive) then
        menuStartTime = os.clock()
        menuAlpha = 1
        menuActive = false
    end
    imgui.Separator()
    imgui.SetCursorPosY(47)

    if imgui.BeginChild("##buttontabs", imgui.ImVec2(130, 320), true) then
        imgui.SetCursorPos(imgui.ImVec2(8, 35))
        for k, v in ipairs(names) do
            if imgui.Button(v, imgui.ImVec2(115, 55)) then
                tab = k
            end
            imgui.SetCursorPosX(8)
        end
        imgui.EndChild()
    end
    imgui.SameLine()
    if imgui.BeginChild("##tepertabs", imgui.ImVec2(532, 320), true) then
        if tab == 1 then
            imgui.SetCursorPos(imgui.ImVec2(200, 40))
            if imgui.ToggleButton(' Rvanka | Kicker##xyi', MRvanka.orvn.active) then 
                settings.orvn.active = MRvanka.orvn.active[0]
                save()
            end
            imgui.Spacing()
            if MRvanka.orvn.active[0] then
                imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Менять повороты рванки', MRvanka.orvn.rotate) then
                    settings.orvn.rotate = MRvanka.orvn.rotate[0]
                    save()
                end
                imgui.SameLine(280)
                if imgui.Checkbox(u8'Random Animation', MRvanka.orvn.rAnim) then
                    settings.orvn.rAnim = MRvanka.orvn.rAnim[0]
                    save()
                end
                --[[imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Плавный телепорт к жертве', MRvanka.orvn.coord) then
                    if not MRvanka.orvn.coord[0] then
                        if MRvanka.orvn.dist[0] > 25 then
                            MRvanka.orvn.dist[0] = 25
                            settings.orvn.dist = MRvanka.orvn.dist[0]
                            save()
                        end
                    end
                    settings.orvn.coord = MRvanka.orvn.coord[0]
                    save()
                end]]
                imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Игнорировать машину', MRvanka.orvn.ignorecar) then
                    settings.orvn.ignorecar = MRvanka.orvn.ignorecar[0]
                    save()
                end
                imgui.SameLine(280)
                if imgui.Checkbox(u8'Random Quanternion', MRvanka.orvn.rQuant) then
                    settings.orvn.rQuant = MRvanka.orvn.rQuant[0]
                    save()
                end
            end
            imgui.Spacing()
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Скорость по высоте', MRvanka.orvn.speed, false, 0.5, 1, '%0.1f') then
                settings.orvn.speed = MRvanka.orvn.speed[0]
                save()
            end
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Дистанция к жертве', MRvanka.orvn.dist, false, 5, MRvanka.orvn.coord[0] and 200 or 25, '%0.0f') then
                settings.orvn.dist = MRvanka.orvn.dist[0]
                save()
            end
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Отнимать высоту', MRvanka.orvn.minusZ, false, 0, 1, '%0.2f') then
                settings.orvn.minusZ = MRvanka.orvn.minusZ[0]
                save()
            end
        elseif tab == 2 then
            imgui.SetCursorPos(imgui.ImVec2(120, 40))
            if imgui.ToggleButton(u8'Rvanka##penis', MRvanka.vrvn.active) then 
                settings.vrvn.active = MRvanka.vrvn.active[0]
                save()
            end
            imgui.SameLine()
            imgui.SetCursorPosY(40)
            if imgui.ToggleButton(u8'Slapper##penis', MRvanka.vrvn.slapper) then 
                settings.vrvn.slapper = MRvanka.vrvn.slapper[0]
                save()
            end
            imgui.SameLine()
            imgui.SetCursorPosY(40)
            if imgui.ToggleButton(u8'Meteor##penis', MRvanka.vrvn.meteor) then 
                settings.vrvn.meteor = MRvanka.vrvn.meteor[0]
                save()
            end
            imgui.Spacing()
            if MRvanka.vrvn.active[0] then
                imgui.SetCursorPosX(90)
                imgui.Checkbox(u8'Обход коллизии (surf)', MRvanka.vrvn.bypasscol)
                imgui.SameLine(280)
                imgui.Checkbox(u8"Random Position", MRvanka.vrvn.rpos)
                imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Менять повороты рванки##2', MRvanka.vrvn.rotate) then
                    settings.vrvn.rotate = MRvanka.vrvn.rotate[0]
                    save()
                end
                imgui.SameLine(280)
                if imgui.Checkbox(u8'Random Quanternion', MRvanka.vrvn.rQuant) then
                    settings.vrvn.rQuant = MRvanka.vrvn.rQuant[0]
                    save()
                end
                imgui.SetCursorPosX(90)
                --[[imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Плавный телепорт к жертве##2', MRvanka.vrvn.coord) then
                    if not MRvanka.vrvn.coord[0] then
                        if MRvanka.vrvn.dist[0] > 25 then
                            MRvanka.vrvn.dist[0] = 25
                            settings.vrvn.dist = MRvanka.vrvn.dist[0]
                            save()
                        end
                    end
                    settings.vrvn.coord = MRvanka.vrvn.coord[0]
                    save()
                end]]
            end
            if (MRvanka.vrvn.slapper[0] or MRvanka.vrvn.meteor[0]) and not MRvanka.vrvn.active[0] then
                imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Random Quanternion', MRvanka.vrvn.rQuant) then
                    settings.vrvn.rQuant = MRvanka.vrvn.rQuant[0]
                    save()
                end
                imgui.SameLine(280)
                imgui.Checkbox(u8"Random Position", MRvanka.vrvn.rpos)
            end
            --[[if MRvanka.vrvn.slapper[0] and not MRvanka.vrvn.active[0] then
                imgui.SetCursorPosX(90)
                if imgui.Checkbox(u8'Плавный телепорт к жертве##2', MRvanka.vrvn.coord) then
                    if not MRvanka.vrvn.coord[0] then
                        if MRvanka.vrvn.dist[0] > 25 then
                            MRvanka.vrvn.dist[0] = 25
                            settings.vrvn.dist = MRvanka.vrvn.dist[0]
                            save()
                        end
                    end
                    settings.vrvn.coord = MRvanka.vrvn.coord[0]
                    save()
                end
            end]]
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Отнимать высоту##2', MRvanka.vrvn.minusZ, false, 0, 1, '%0.2f') then
                settings.vrvn.minusZ = MRvanka.vrvn.minusZ[0]
                save()
            end
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Дистанция##2', MRvanka.vrvn.dist, false, 5, MRvanka.vrvn.coord[0] and 200 or 25, '%0.2f') then
                settings.vrvn.dist = MRvanka.vrvn.dist[0]
                save()
            end
        -- elseif tab == 3 then
        --     imgui.SetCursorPos(imgui.ImVec2(120, 40))
        --     if imgui.ToggleButton(u8'Rvanka##unoc', MRvanka.urvn.rvanka) then 
        --         settings.urvn.rvanka = MRvanka.urvn.rvanka[0]
        --         save()
        --     end
        --     imgui.SameLine()
        --     imgui.SetCursorPosY(40)
        --     if imgui.ToggleButton(u8'Slapper##unoc', MRvanka.urvn.slapper) then 
        --         settings.urvn.slapper = MRvanka.urvn.slapper[0]
        --         save()
        --     end
        --     imgui.SameLine()
        --     imgui.SetCursorPosY(40)
        --     if imgui.ToggleButton(u8'Meteor##unoc', MRvanka.urvn.meteor) then 
        --         settings.urvn.meteor = MRvanka.urvn.meteor[0]
        --         save()
        --     end
        --     imgui.Spacing()
        --     if MRvanka.urvn.rvanka[0] then
        --         imgui.SetCursorPosX(90)
        --         if imgui.Checkbox(u8'Менять повороты рванки', MRvanka.urvn.rotate) then
        --             settings.urvn.rotate = MRvanka.urvn.rotate[0]
        --             save()
        --         end
        --         imgui.SameLine(280)
        --         if imgui.Checkbox(u8'Random roll/direction', MRvanka.urvn.rollAndDirect) then
        --             settings.urvn.rollAndDirect = MRvanka.urvn.rollAndDirect[0]
        --             save()
        --         end
        --         imgui.SetCursorPosX(90)
        --         if imgui.Checkbox(u8'Спавнить авто', MRvanka.urvn.destroy) then
        --             settings.urvn.destroy = MRvanka.urvn.destroy[0]
        --             save()
        --         end
        --     else
        --         if MRvanka.urvn.meteor[0] or MRvanka.urvn.slapper[0] then
        --             imgui.SetCursorPosX(90)
        --             if imgui.Checkbox(u8'Random roll/direction', MRvanka.urvn.rollAndDirect) then
        --                 settings.urvn.rollAndDirect = MRvanka.urvn.rollAndDirect[0]
        --                 save()
        --             end
        --             imgui.SameLine(280)
        --             if imgui.Checkbox(u8'Спавнить авто', MRvanka.urvn.destroy) then
        --                 settings.urvn.destroy = MRvanka.urvn.destroy[0]
        --                 save()
        --             end
        --         end
        --     end
        --     imgui.Spacing()
        --     imgui.SetCursorPosX(130)
        --     if imgui.CustomSlider(u8'Дистанция к жертве', MRvanka.urvn.dist, true, 5, 59) then
        --         settings.urvn.dist = MRvanka.urvn.dist[0]
        --         save()
        --     end
        --     imgui.SetCursorPosX(130)
        --     if imgui.CustomSlider(u8'Отнимать высоту', MRvanka.urvn.minusZ, false, 0, 1, '%0.2f') then
        --         settings.urvn.minusZ = MRvanka.urvn.minusZ[0]
        --         save()
        --     end
        elseif tab == 3 then
            imgui.SetCursorPos(imgui.ImVec2(80, 40))
            if imgui.Checkbox("OnFoot Invisible (pos z)  ", MRvanka.orvn.invisZ) then
                if isCharInAnyCar(PLAYER_PED) then MRvanka.orvn.invisZ[0] = false end
                local pos = {getCharCoordinates(PLAYER_PED)}
                if MRvanka.orvn.invisZ[0] then
                    if MRvanka.orvn.invisZPos[0] <= -100 then
                        for i = pos[3], MRvanka.orvn.invisZPos[0], -25 do
                            onfoot({pos[1], pos[2], i}, {0, 0, -1}, nil)
                        end
                    else
                        for i = pos[3], -125, -25 do
                            onfoot({pos[1], pos[2], i}, {0, 0, -1}, nil)
                            --msg(i)
                        end
                    end
                else
                    if MRvanka.orvn.invisZPos[0] > -90 then
                        for i = MRvanka.orvn.invisZPos[0], pos[3], -25 do
                            onfoot({pos[1], pos[2], i}, {0, 0, -1}, nil)
                        end
                    end
                end
                MRvanka.orvn.invisZState = MRvanka.orvn.invisZ[0]
            end
            imgui.SameLine()
            imgui.Checkbox("OnFoot Invisible (surfing)  ", MRvanka.orvn.invisSurf)
            imgui.SetCursorPosX(80)
            if imgui.Checkbox("InCar Invisible    (pos z)  ", MRvanka.vrvn.invisZ) then
                if isCharOnFoot(PLAYER_PED) then MRvanka.vrvn.invisZ[0] = false end
                local pos = {getCharCoordinates(PLAYER_PED)}
                if MRvanka.vrvn.invisZ[0] then
                    if MRvanka.orvn.invisZPos[0] <= -100 then
                        for i = pos[3], MRvanka.orvn.invisZPos[0], -25 do
                            vehicle({pos[1], pos[2], i}, -0.1)
                        end
                    else
                        for i = pos[3], -125, -25 do
                            vehicle({pos[1], pos[2], i}, -0.1)
                        end
                    end
                else
                    if MRvanka.orvn.invisZPos[0] > -90 then
                        for i = MRvanka.orvn.invisZPos[0], pos[3], -25 do
                            vehicle({pos[1], pos[2], i}, MRvanka.vrvn.state and -3.45 or MRvanka.vrvn.slapstate and -3.45 or MRvanka.vrvn.meteorstate and -3.45 or -0.1)
                        end
                    end
                end
                MRvanka.vrvn.invisZState = MRvanka.vrvn.invisZ[0]
            end
            imgui.SameLine()
            if imgui.Checkbox("InCar Invisible (spawn car)", MRvanka.vrvn.invisSpawn) then
                if isCharOnFoot(PLAYER_PED) then MRvanka.vrvn.invisSpawn[0] = false end
            end
            imgui.Spacing()
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Дистанция до авто', MRvanka.orvn.invisDist, false, 1, 65, '%0.2f') then
                settings.vrvn.invisDist = MRvanka.orvn.invisDist[0]
                save()
            end
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Количество пакетов', MRvanka.vrvn.invisPacket, true, 1, 100) then
                settings.vrvn.invisPacket = MRvanka.vrvn.invisPacket[0]
                save()
            end
            imgui.SetCursorPosX(130)
            if imgui.CustomSlider(u8'Высота', MRvanka.orvn.invisZPos, true, -990, 1500) then
                settings.orvn.invisZPos = MRvanka.orvn.invisZPos[0]
                save()
            end
        elseif tab == 4 then
            imgui.SetCursorPos(imgui.ImVec2(120, 40))
            if imgui.Checkbox(u8'Отрисовка круга', MRvanka.settings.drawCircle) then
                settings.settings.drawCircle = MRvanka.settings.drawCircle[0]
                save()
            end
            imgui.SameLine(260)
            if imgui.Checkbox(u8'Отрисовка линии', MRvanka.settings.drawLine) then
                settings.settings.drawLine = MRvanka.settings.drawLine[0]
                save()
            end
            imgui.SetCursorPosX(120)
            if imgui.Checkbox(u8'Двигать круг', MRvanka.settings.moveCircle) then
                settings.settings.moveCircle = MRvanka.settings.moveCircle[0]
                save()
            end
            -- imgui.SameLine(260)
            -- if imgui.Checkbox(u8'Чекер смерти/кика', MRvanka.settings.checker) then
            --     settings.settings.checker = MRvanka.settings.checker[0]
            --     save()
            -- end
        end
        imgui.EndChild()
    end
    imgui.End()
end)

function main()
    while not isSampAvailable() do wait(0) end
    math.randomseed(os.time())
    sampRegisterChatCommand('rvnmf', function()
        if renderWindow[0] then
            menuStartTime = os.clock()
            menuAlpha = 1
            menuActive = false
        else
            menuStartTime = os.clock()
            menuAlpha = 0
            menuActive = not renderWindow[0]
            renderWindow[0] = true
        end
    end)
    while true do wait(0)
        if MRvanka.orvn.active[0] then
            if isKeyJustPressed(VK_Z) and keys() and isCharOnFoot(PLAYER_PED) then
                MRvanka.orvn.state = not MRvanka.orvn.state
                packet, change = 0, false
            end
            if MRvanka.orvn.state and isCharOnFoot(PLAYER_PED) then
                local id, handle = getNearPlayerId(true)
                if id and handle then
                    if MRvanka.orvn.invisZState and not MRvanka.orvn.nop then
                        local my_pos = {getCharCoordinates(PLAYER_PED)}
                        MRvanka.orvn.nop = true
                        if MRvanka.orvn.invisZPos[0] > -90 then
                            for i = MRvanka.orvn.invisZPos[0], my_pos[3], -25 do
                                onfoot({my_pos[1], my_pos[2], i}, {0, 0, -1}, nil)
                            end
                        end
                        MRvanka.orvn.invisZState = false
                        MRvanka.orvn.invisZ[0] = false
                    else
                        MRvanka.orvn.nop = true
                    end
                    table.insert(MRvanka.other.id, id)
                    local pos = {getCharCoordinates(handle)}
                    MRvanka.coord.x, MRvanka.coord.y, MRvanka.coord.z = table.unpack(pos)
                    printStringNow("Rvanka: ~r~"..sampGetPlayerNickname(id).."["..id.."]", 150)
                    lua_thread.create(function()
                        sendORvanka(pos[1], pos[2], pos[3]-MRvanka.orvn.minusZ[0], id)
                        wait(35)
                    end)
                else
                    MRvanka.orvn.nop = false
                    printStringNow("~r~ Try found a player", 150)
                end
            elseif MRvanka.orvn.state then
                MRvanka.orvn.state = false
            end
        end
        if MRvanka.vrvn.meteor[0] then
            if isKeyJustPressed(VK_M) and keys() and isCharInAnyCar(PLAYER_PED) then
                MRvanka.vrvn.meteorstate = not MRvanka.vrvn.meteorstate
                if MRvanka.vrvn.meteorstate then
                    local x, y, z = getCharCoordinates(PLAYER_PED)
                    if not (MRvanka.vrvn.state and MRvanka.vrvn.slapstate) then
                        for i = 0, 3.45, 0.06 do
                            sendVRvanka(x, y, z, 0.1, getCharHeading(PLAYER_PED), i)
                        end
                        MRvanka.vrvn.mxy = 0.1
                        MRvanka.vrvn.mz = 3.45
                    end
                end
            end
            if MRvanka.vrvn.meteorstate and isCharInAnyCar(PLAYER_PED) then
                local id, handle = getNearPlayerId(false)
                if id and handle then
                    if MRvanka.vrvn.invisZState and not MRvanka.vrvn.nop then
                        local my_pos = {getCharCoordinates(PLAYER_PED)}
                        if MRvanka.orvn.invisZPos[0] > -90 then
                            for i = MRvanka.orvn.invisZPos[0], my_pos[3], -25 do
                                vehicle({my_pos[1], my_pos[2], i}, -3.45)
                            end
                        end
                        MRvanka.vrvn.invisZState = false
                        MRvanka.vrvn.invisZ[0] = false
                    end
                    MRvanka.vrvn.nop = true
                    table.insert(MRvanka.other.id, id)
                    local pos = {getCharCoordinates(handle)}
                    printStringNow("Send meteor: ~r~"..sampGetPlayerNickname(id).."["..id.."]", 150)
                    MRvanka.vrvn.mxy = 1.3
                    MRvanka.vrvn.mz = -3.2
                    for _ = 1, 3 do
                        sendVMeteor(pos[1], pos[2], pos[3]+10, MRvanka.vrvn.mxy, MRvanka.vrvn.mz, getCharHeading(handle))
                    end
                    wait(100)
                else
                    MRvanka.vrvn.nop = false
                    printStringNow("~r~ Try found a player", 150)
                end
            elseif MRvanka.vrvn.meteorstate then
                MRvanka.vrvn.meteorstate = false
            end
        end

        if MRvanka.vrvn.active[0] then
            if isKeyJustPressed(VK_Z) and keys() and isCharInAnyCar(PLAYER_PED) then
                MRvanka.vrvn.state = not MRvanka.vrvn.state
                if MRvanka.vrvn.state then
                    local x, y, z = getCharCoordinates(PLAYER_PED)
                    if not (MRvanka.vrvn.meteorstate and MRvanka.vrvn.slapstate) then
                        for i = 0, 3.4, 0.06 do
                            sendVRvanka(x, y, z, 0.1, getCharHeading(PLAYER_PED), i)
                        end
                        MRvanka.vrvn.mxy = 0.1
                        MRvanka.vrvn.mz = 3.45
                    end
                end
            end
            if MRvanka.vrvn.state and isCharInAnyCar(PLAYER_PED) then
                local id, handle = getNearPlayerId(false)
                if id and handle then
                    if MRvanka.vrvn.invisZState and not MRvanka.vrvn.nop then
                        local my_pos = {getCharCoordinates(PLAYER_PED)}
                        if MRvanka.orvn.invisZPos[0] > -90 then
                            for i = MRvanka.orvn.invisZPos[0], my_pos[3], -25 do
                                vehicle({my_pos[1], my_pos[2], i}, -3.45)
                            end
                        end
                        MRvanka.vrvn.invisZState = false
                        MRvanka.vrvn.invisZ[0] = false
                    end
                    MRvanka.vrvn.nop = true
                    table.insert(MRvanka.other.id, id)
                    local pos = {getCharCoordinates(handle)}
                    local inCar = isCharInAnyCar(handle)
                    printStringNow("Rvanka: ~r~"..sampGetPlayerNickname(id).."["..id.."]", 150)
                    MRvanka.vrvn.mxy = inCar and 2.7 or 3.45
                    MRvanka.vrvn.mz = inCar and 2.15 or 0.1
                    sendVRvanka(pos[1], pos[2], pos[3]-MRvanka.vrvn.minusZ[0], MRvanka.vrvn.mxy, getCharHeading(handle), MRvanka.vrvn.mz)
                    wait(25)
                else
                    MRvanka.vrvn.nop = false
                    printStringNow("~r~ Try found a player", 150)
                end
            elseif MRvanka.vrvn.state then
                MRvanka.vrvn.state = false
            end
        end

        if MRvanka.vrvn.slapper[0] then
            if isKeyJustPressed(VK_R) and keys() and isCharInAnyCar(PLAYER_PED) then
                MRvanka.vrvn.slapstate = not MRvanka.vrvn.slapstate
                if MRvanka.vrvn.slapstate then
                    local x, y, z = getCharCoordinates(PLAYER_PED)
                    if not (MRvanka.vrvn.meteorstate and MRvanka.vrvn.state) then
                        for i = 0, 3.45, 0.06 do
                            sendVRvanka(x, y, z, 0.1, getCharHeading(PLAYER_PED), i)
                        end
                        MRvanka.vrvn.mxy = 0.1
                        MRvanka.vrvn.mz = 3.45
                    end
                end
            end
            if MRvanka.vrvn.slapstate and isCharInAnyCar(PLAYER_PED) then
                local id, ped = getNearPlayerId(false)
                if id ~= -1 and ped then
                    if MRvanka.vrvn.invisZState and not MRvanka.vrvn.nop then
                        local my_pos = {getCharCoordinates(PLAYER_PED)}
                        MRvanka.vrvn.nop = true
                        if MRvanka.orvn.invisZPos[0] > -90 then
                            for i = MRvanka.orvn.invisZPos[0], my_pos[3], -25 do
                                vehicle({my_pos[1], my_pos[2], i}, -3.45)
                            end
                        end
                        MRvanka.vrvn.invisZState = false
                        MRvanka.vrvn.invisZ[0] = false
                    else
                        MRvanka.vrvn.nop = true
                    end
                    table.insert(MRvanka.other.id, id)
                    local pos = {getCharCoordinates(ped)}
                    printStringNow("Slap: ~r~"..sampGetPlayerNickname(id).."["..id.."]", 150)
                    MRvanka.vrvn.mxy = 1
                    MRvanka.vrvn.mz = 3.15
                    lua_thread.create(function ()
                        for _ = 1, 3 do
                            sendVSlap(pos[1], pos[2], pos[3]-MRvanka.vrvn.minusZ[0], MRvanka.vrvn.mxy, MRvanka.vrvn.mz, id)
                        end
                        wait(25)
                    end)
                else
                    MRvanka.vrvn.nop = false
                    printStringNow("~r~Try found a player", 100)
                end
            elseif MRvanka.vrvn.slapstate then
                MRvanka.vrvn.slapstate = false
            end
        end
    end
end

local govno = false

local visual = imgui.OnFrame(function() return ((MRvanka.orvn.state or MRvanka.orvn.slapstate) and isCharOnFoot(PLAYER_PED)) or ((MRvanka.vrvn.state or MRvanka.vrvn.slapstate or MRvanka.vrvn.meteorstate) and isCharInAnyCar(PLAYER_PED)) end, function(player)
        player.HideCursor = true
        local r, g, b, a = rainbow(2.5, 255, 0)
        local rgbat = join_argb(a, r, g, b)
        local id = getNearPlayerId(isCharOnFoot(PLAYER_PED))
        if not id then return end

        local _, ped = sampGetCharHandleBySampPlayerId(id)
        if not ped then return end

        local mx, my, mz = getCharCoordinates(PLAYER_PED)
        local x, y, z = getCharCoordinates(ped)
        local wx, wy = convert3DCoordsToScreen(mx, my, mz)
        if not isCharOnScreen(ped) then return end

        local drawList = imgui.GetBackgroundDrawList()
        local prevScreen = nil
        local zgrug = MRvanka.other.zgrug
        if MRvanka.settings.drawCircle[0] then
            for rot = 0, 360, 5 do
                local rot_temp = math.rad(rot)
                local circleX = 0.8 * math.cos(rot_temp) + x
                local circleY = 0.8 * math.sin(rot_temp) + y
                local screenX, screenY = convert3DCoordsToScreen(circleX, circleY, z - zgrug)
                if screenX and screenY then
                    if prevScreen then
                        drawList:AddLine(imgui.ImVec2(prevScreen[1], prevScreen[2]), imgui.ImVec2(screenX, screenY), rgbat, 4.0)
                    end
                    prevScreen = {screenX, screenY}
                end
            end
        end
        local centerScreenX, centerScreenY = convert3DCoordsToScreen(x, y, z - zgrug)
        if centerScreenX and centerScreenY and MRvanka.settings.drawLine[0] then
            drawList:AddLine(imgui.ImVec2(wx, wy), imgui.ImVec2(centerScreenX, centerScreenY), rgbat, 2.0)
        end

        local step = 0.05
        if MRvanka.settings.moveCircle[0] then
            if govno then
                zgrug = zgrug - step
                if zgrug <= -0.8 then govno = false end
            else
                zgrug = zgrug + step
                if zgrug >= 0.8 then govno = true end
            end
        else
            zgrug = 0.8
        end
        MRvanka.other.zgrug = zgrug
    end
)

-- function sendTeleport(x, y, z, mx, my, mz)
--     local vector = require('vector3d')
--     local packet = 0
--     while getDistanceBetweenCoords3d(mx, my, mz, x, y, z) >= 10 do
--         local vector = vector(x - mx, y - my, z - mz)
--         vector:normalize()
--         mx = mx + vector.x * 3
--         my = my + vector.y * 3
--         mz = mz + vector.z * 3
--         packet = packet + 1
--         if isCharOnFoot(PLAYER_PED) then
--             onfoot({mx, my, mz}, {0.7, 0.7, 1}, nil)
--         else
--             vehicle({mx, my, mz}, {MRvanka.vrvn.mxy/1.44, MRvanka.vrvn.mxy/1.44, MRvanka.vrvn.mz})
--         end
--         if packet >= 22 then
--             if isCharOnFoot(PLAYER_PED) then
--                 onfoot({mx, my, mz}, {0.7, 0.7, 1}, nil)
--             else
--                 vehicle({mx, my, mz}, {MRvanka.vrvn.mxy/1.44, MRvanka.vrvn.mxy/1.44, MRvanka.vrvn.mz})
--             end
--             wait(500)
--             packet = 0
--         end
--     end
--     packet = 0
--     MRvanka.coord.x = mx
--     MRvanka.coord.y = my
--     MRvanka.coord.z = mz
-- end

function onfoot(pos, move, vehid)
    local data = samp_create_sync_data("player")
    data.moveSpeed = move
    data.position = pos
    data.specialAction = 3
    if vehid ~= nil then
        data.surfingVehicleId = tonumber(vehid)
        data.surfingOffsets = {0.2, 0.1, 0.4}
    end
    data.send()
end

function vehicle(pos, speed)
    local data = samp_create_sync_data('vehicle')
    data.moveSpeed.z = speed
    data.position = pos
    data.send()
end

function sendORvanka(x, y, z, id)
    local data = samp_create_sync_data('player')
    local _, ped = sampGetCharHandleBySampPlayerId(id)
    local heading = getCharHeading(ped)
    local qz = select(3, getCharQuaternion(ped))
    local sinH, cosH = math.sin(-math.rad(heading)), math.cos(-math.rad(heading))
    local rand = 0
    local badAnim = {972, 973, 974, 975}
    ::again::
    rand = math.random(1, 1812)
    --local numbers = {1564, 1567, 1570, 1573, 1576, 1579, 1582, 1585, 1591, 1593, 1595, 1597, 1600, 1603, 1606, 1607, 1609, 1612, 1615}
    if badAnim[rand] then
        goto again
    end
    local sign = change and 1 or -1
    if MRvanka.orvn.packet >= 3 then
        data.moveSpeed = {0, 0, 0}
        MRvanka.boost = not MRvanka.boost
        if MRvanka.orvn.rotate[0] then
            if packet >= 55 then
                change = not change
                packet = 0
            else
                packet = packet + 1
            end
        else
            change = false
        end
        MRvanka.orvn.packet = 0
    else
        MRvanka.orvn.packet = MRvanka.orvn.packet + 1
        local boost = MRvanka.boost and 2.69 or 2.45
        data.moveSpeed = {sinH * boost * sign, cosH * boost * sign, MRvanka.orvn.speed[0]}
    end
    data.position = {x - sinH * 2.4 * sign, y - cosH * 2.4 * sign, z}
    data.specialAction = 4
    data.surfingVehicleId = 0

    if MRvanka.orvn.rQuant[0] then
        data.quaternion = {
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            0
        }
    else
        data.quaternion[3] = qz
    end
    if MRvanka.orvn.rAnim[0] then
        data.animationId = rand
        data.animationFlags = 11111
    end
    data.send()
end

function sendVRvanka(x, y, z, move, heading, movez)
    local data = samp_create_sync_data('vehicle')
    if MRvanka.vrvn.rotate[0] then
        if packet >= 33 then
            change = not change
            packet = 0
        else
            packet = packet + 1
        end
        if change then heading = heading / 2 end
    else
        change = false
    end
    local a = heading * math.pi / 360.0

    if MRvanka.vrvn.rQuant[0] then
        data.quaternion = {
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999))
        }
    else
        local c1, c2, c3 = 1, math.cos(a), 1
        local s1, s2, s3 = 0, math.sin(a), 0
        local quat = c1 * c2 * c3 - s1 * s2 * s3
        data.quaternion[0] = quat
        data.quaternion[3] = -quat
    end

    if MRvanka.vrvn.bypasscol[0] then
        data.position = {x, y, z}
        data.moveSpeed = {move / 1.44, move / 1.44, movez}
    else
        local sinH, cosH = math.sin(-math.rad(heading)), math.cos(-math.rad(heading))
        local offset = move / 1.2
        local dx = (change and (x + sinH * offset) or (x - sinH * offset)) + (surfState and math.random(-3, 3) or 0)
        local dy = (change and (y + cosH * offset) or (y - cosH * offset)) + (surfState and math.random(-3, 3) or 0)
        data.moveSpeed = {change and -sinH * move or sinH * move, change and -cosH * move or cosH * move, movez}
        data.position = {dx, dy, z}
    end
    data.send()
end

function sendVSlap(x, y, z, move, movez, id)
    local data = samp_create_sync_data('vehicle')
    local ped = select(2, sampGetCharHandleBySampPlayerId(id))
    if id == nil then ped = PLAYER_PED end
    if MRvanka.vrvn.rQuant[0] then
        data.quaternion = {
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999))
        }
    else
        if isCharInAnyCar(ped) then
            data.quaternion[3] = -0.7
        else
            data.quaternion[3] = 0
        end
    end
    data.position = {x + (surfState and math.random(-3, 3) or 0), y + (surfState and math.random(-3, 3) or 0), z}
    data.moveSpeed = {move, move, movez}
    data.send()
end

function sendVMeteor(x, y, z, move, movez, heading)
    local data = samp_create_sync_data('vehicle')
    local sinH, cosH = math.sin(-math.rad(heading)), math.cos(-math.rad(heading))
    if MRvanka.vrvn.rQuant[0] then
        data.quaternion = {
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999)),
            tonumber("0."..math.random(0, 9999))
        }
    end
    data.position = {x - sinH * 3.5, y - cosH * 3.5, z}
    data.moveSpeed = {move * sinH, move * cosH, movez}
    data.send()
end

function sendUnocInvis(x, y, z, id)
	local data = samp_create_sync_data("unoccupied")
	local veh = select(2, sampGetCarHandleBySampVehicleId(id))
	local roll, direction = getCarRealMatrix(veh)
	data.vehicleId = id
	data.seatId = 0
	data.roll = roll
	data.direction = direction
	data.position = {x,y,z-0.5}
    data.moveSpeed = {0, 0, -0.1}
    data.turnSpeed = {0, 0.2, -0.2}
	data.vehicleHealth = 1500
	data.send()
end

function sendUnoc(pos, speed, turn, id, heading)
	local data = samp_create_sync_data("unoccupied")
	local veh = select(2, sampGetCarHandleBySampVehicleId(id))
	local roll, direction = getCarRealMatrix(veh)
    local sinH, cosH = math.sin(-math.rad(heading)), math.cos(-math.rad(heading))
    pos[3] = pos[3] - MRvanka.urvn.minusZ[0]
	data.vehicleId = id
	data.seatId = 0
	data.roll = roll
	data.direction = direction
	data.position = pos
    data.position = {pos[1] + sinH * 0.5, pos[2] + cosH * 0.5, pos[3]}
    data.moveSpeed = {speed[1] * sinH, speed[2] * cosH, speed[3]}
    data.turnSpeed = {turn[1] * sinH, turn[2] * cosH, turn[3]}
	data.vehicleHealth = getCarHealth(veh)
	data.send()
end

function getNearPlayerId(state)
    local minDist = state and MRvanka.orvn.dist[0] or MRvanka.vrvn.dist[0]
    local id, handle = -1, nil
    local x, y, z = getCharCoordinates(PLAYER_PED)
    for i = 0, sampGetMaxPlayerId(true) do
        local streamed, ped = sampGetCharHandleBySampPlayerId(i)
        if streamed and ped and not isCharDead(ped) and not sampIsPlayerPaused(i) then
            if state and MRvanka.orvn.ignorecar[0] and isCharInAnyCar(ped) then
                goto continue
            end
            local xi, yi, zi = getCharCoordinates(ped)
            local dist = getDistanceBetweenCoords3d(x, y, z, xi, yi, zi)
            if dist < minDist then
                minDist = dist
                handle = ped
                id = i
            end
        end
        ::continue::
    end
    return id ~= -1 and id or false, handle ~= nil and handle or false
end

function getVehicle(checkDist)
    local dist, id = checkDist, -1
    for k, veh in pairs(getAllVehicles()) do
        local _, vid = sampGetVehicleIdByCarHandle(veh)
        if _ then
            local driverCar = getDriverOfCar(veh) ~= -1
            if not driverCar then
                local car_pos = {getCarCoordinates(veh)}
                local player_pos = {getCharCoordinates(PLAYER_PED)}
                local new_distance = getDistanceBetweenCoords3d(car_pos[1], car_pos[2], car_pos[3], player_pos[1], player_pos[2], player_pos[3])
                if dist > new_distance then
                    id = vid
                    dist = new_distance
                end
            end
        end
    end
    return id ~= -1 and id or false, dist
end

function keys()
	return (not sampIsChatInputActive() and not sampIsDialogActive() and not sampIsCursorActive() and sampIsLocalPlayerSpawned())
end

function sampev.onSetPlayerPos(position)
    if MRvanka.orvn.invisSurf[0] then
        local mpos = vector(getCharCoordinates(PLAYER_PED))
        if getDistanceBetweenCoords3d(mpos.x, mpos.y, mpos.z, position.x, position.y, position.z) < 25 then
            return false
        end
    end
end

function sampev.onApplyPlayerAnimation(playerId, animLib, animName, frameDelta, loop, lockX, lockY, freeze, time)
    if MRvanka.orvn.invisSurf[0] then
        local block = {"IDLE_CHAT", "crry_prtial", "phone_talk", "BOM_Plant", "getup"}
        for k, v in ipairs(block) do
            if v == animName then
                return false
            end
        end
    end
end

function sampev.onSetVehicleAngle(vehicleId, angle)
    if MRvanka.vrvn.state or MRvanka.vrvn.slapstate or MRvanka.vrvn.meteorstate then
        return false
    end
end

function sampev.onSendPlayerSync(data)
    if MRvanka.orvn.state then
        if MRvanka.orvn.nop then
            return false
        end
    end
    if MRvanka.orvn.invisZ[0] and MRvanka.orvn.invisZState then
        data.position.z = MRvanka.orvn.invisZPos[0]
    end
    if MRvanka.orvn.invisSurf[0] then
        local id, dist = getVehicle(MRvanka.orvn.invisDist[0])
        if id then
            local mx, my, mz = getCharCoordinates(PLAYER_PED)
            local carHandle = select(2, sampGetCarHandleBySampVehicleId(id))
            local cx, cy, cz = getCarCoordinates(carHandle)
            data.surfingVehicleId = id
            data.surfingOffsets = {0, 0, -1}
            MRvanka.orvn.cid = id
            if getDistanceBetweenCoords3d(mx, my, mz, cx, cy, cz) > MRvanka.orvn.invisDist[0] then
                local vector = vector(mx - cx, my - cy, mz - cz)
                vector:normalize()
                cx = cx + vector.x * 4
                cy = cy + vector.y * 4
                cz = cz + vector.z * 4
                sendUnocInvis(cx, cy, cz, id)
                setCarCoordinates(carHandle, cx, cy, cz+0.3)
            end
            printStringNow(string.format("~b~ CarId: [~w~%d~b~] Dist: ~w~ %0.2f", id, dist), 500)
        else
            printStringNow("Try found a car", 100)
        end
    end
end

function sampev.onSendVehicleSync(data)
    if MRvanka.vrvn.state or MRvanka.vrvn.slapstate or MRvanka.vrvn.meteorstate then
        if MRvanka.vrvn.nop then
            return false
        else
            data.moveSpeed = {math.sin(-math.rad(getCharHeading(PLAYER_PED))) * MRvanka.vrvn.mxy, math.cos(-math.rad(getCharHeading(PLAYER_PED))) * MRvanka.vrvn.mxy, MRvanka.vrvn.mz}
        end
    end
    if MRvanka.vrvn.invisZ[0] and MRvanka.vrvn.invisZState then
        data.position.z = MRvanka.orvn.invisZPos[0]
    end
    if MRvanka.vrvn.invisSpawn[0] then
        if MRvanka.vrvn.invisPackets >= MRvanka.vrvn.invisPacket[0] then
            data.vehicleHealth = getCarHealth(storeCarCharIsInNoSave(PLAYER_PED))
            MRvanka.vrvn.invisPackets = 0
        else
            MRvanka.vrvn.invisPackets = MRvanka.vrvn.invisPackets + 1
            data.vehicleHealth = 1e+37
        end
    end
end

function sampev.onPlayerSync(playerId, data)
    if MRvanka.vrvn.state or MRvanka.vrvn.slapstate or MRvanka.vrvn.meteorstate then
        if data.surfingVehicleId == select(2, sampGetVehicleIdByCarHandle(getCarCharIsUsing(PLAYER_PED))) then
            if MRvanka.vrvn.rpos[0] then
                surfState = true
            end
            data.surfingVehicleId = 0
            return {playerId, data}
        else
            surfState = false
        end
    end
end

function sampev.onPlayerQuit(playerId, reason)
    if (MRvanka.orvn.state or MRvanka.vrvn.state or MRvanka.orvn.slapstate or MRvanka.vrvn.slapstate or MRvanka.vrvn.meteorstate) and MRvanka.settings.checker[0] then
        for k, v in pairs(MRvanka.other.id) do
            if v == playerId and reason == 2 then
                MRvanka.other.kicked = MRvanka.other.kicked + 1
                msg("%s[%d] Успешно был кикнут. Кол-во кикнутых: %d", sampGetPlayerNickname(playerId), playerId, MRvanka.other.kicked)
                table.remove(MRvanka.other.id, k)
                break
            end
        end
    end
end

function sampev.onPlayerDeath(playerId)
    if (MRvanka.orvn.state or MRvanka.vrvn.state or MRvanka.orvn.slapstate or MRvanka.vrvn.slapstate or MRvanka.vrvn.meteorstate) and MRvanka.settings.checker[0] then
        for k, v in pairs(MRvanka.other.id) do
            if v == playerId then
                msg(sampGetPlayerNickname(playerId).."["..playerId.."] Умер.")
                table.remove(MRvanka.other.id, k)
                break
            end
        end
    end
end

function getCarRealMatrix(handle)
	local memory = require('memory')
	local entity = getCarPointer(handle)
	if (entity ~= 0) then
		local carMatrix = memory.getuint32(entity + 20, true)
		if (carMatrix ~= 0) then
			local rx = memory.getfloat(carMatrix + (0 * 4), true)
			local ry = memory.getfloat(carMatrix + (1 * 4), true)
			local rz = memory.getfloat(carMatrix + (2 * 4), true)
			local dx = memory.getfloat(carMatrix + (4 * 4), true)
			local dy = memory.getfloat(carMatrix + (5 * 4), true)
			local dz = memory.getfloat(carMatrix + (6 * 4), true)
			return {rx, ry, rz}, {dx, dy, dz}
		end
	end
end

function theme()
    imgui.SwitchContext()
    local style = imgui.GetStyle()
    local colors = style.Colors

    local darkGray  = imgui.ImVec4(0.13, 0.13, 0.15, 1.00)
    local midGray   = imgui.ImVec4(0.20, 0.22, 0.27, 1.00)
    local accent    = imgui.ImVec4(0.20, 0.45, 0.75, 1.00)
    local accentHvr = imgui.ImVec4(0.30, 0.55, 0.85, 1.00)
    local accentAct = imgui.ImVec4(0.15, 0.40, 0.60, 1.00)

    colors[imgui.Col.WindowBg]          = darkGray
    colors[imgui.Col.ChildBg]           = midGray
    colors[imgui.Col.PopupBg]           = midGray
    colors[imgui.Col.Border]            = imgui.ImVec4(0.1, 0.1, 0.1, 1.0)
    colors[imgui.Col.Separator]         = accent
    colors[imgui.Col.Text]              = imgui.ImVec4(0.90, 0.95, 1.00, 1.00)
    colors[imgui.Col.TextDisabled]      = imgui.ImVec4(0.5, 0.5, 0.5, 1.0)
    colors[imgui.Col.Button]            = accent
    colors[imgui.Col.ButtonHovered]     = accentHvr
    colors[imgui.Col.ButtonActive]      = accentAct
    colors[imgui.Col.Tab]               = accent
    colors[imgui.Col.TabHovered]        = accentHvr
    colors[imgui.Col.TabActive]         = accentAct
    colors[imgui.Col.TabUnfocused]      = midGray
    colors[imgui.Col.SliderGrab]        = imgui.ImVec4(0.30, 0.65, 1.00, 1.00)
    colors[imgui.Col.SliderGrabActive]  = imgui.ImVec4(0.40, 0.70, 1.00, 1.00)
    style.WindowRounding                = 6
    style.ChildRounding                 = 6
    style.FrameRounding                 = 4
    style.GrabRounding                  = 4
    style.ScrollbarRounding            = 4
    style.FramePadding                 = imgui.ImVec2(6, 4)
    style.ItemSpacing                  = imgui.ImVec2(8, 4)
end

function imgui.ToggleButton(str_id, bool)
    local rBool = false

    if LastActiveTime == nil then
        LastActiveTime = {}
    end
    if LastActive == nil then
        LastActive = {}
    end

    local function ImSaturate(f)
        return f < 0.0 and 0.0 or (f > 1.0 and 1.0 or f)
    end

    local p = imgui.GetCursorScreenPos()
    local dl = imgui.GetWindowDrawList()

    local height = imgui.GetTextLineHeightWithSpacing()
    local width = height * 1.70
    local radius = height * 0.50
    local ANIM_SPEED = type == 2 and 0.10 or 0.15
    local butPos = imgui.GetCursorPos()

    if imgui.InvisibleButton(str_id, imgui.ImVec2(width, height)) then
        bool[0] = not bool[0]
        rBool = true
        LastActiveTime[tostring(str_id)] = os.clock()
        LastActive[tostring(str_id)] = true
    end

    imgui.SetCursorPos(imgui.ImVec2(butPos.x + width + 8, butPos.y + 2.5))
    imgui.Text( str_id:gsub('##.+', '') )

    local t = bool[0] and 1.0 or 0.0

    if LastActive[tostring(str_id)] then
        local time = os.clock() - LastActiveTime[tostring(str_id)]
        if time <= ANIM_SPEED then
            local t_anim = ImSaturate(time / ANIM_SPEED)
            t = bool[0] and t_anim or 1.0 - t_anim
        else
            LastActive[tostring(str_id)] = false
        end
    end

    local col_circle = bool[0] and imgui.ColorConvertFloat4ToU32(imgui.ImVec4(imgui.GetStyle().Colors[imgui.Col.ButtonActive])) or imgui.ColorConvertFloat4ToU32(imgui.ImVec4(imgui.GetStyle().Colors[imgui.Col.TextDisabled]))
    dl:AddRectFilled(p, imgui.ImVec2(p.x + width, p.y + height), imgui.ColorConvertFloat4ToU32(imgui.GetStyle().Colors[imgui.Col.FrameBg]), height * 0.5)
    dl:AddCircleFilled(imgui.ImVec2(p.x + radius + t * (width - radius * 2.0), p.y + radius), radius - 1.5, col_circle)
    return rBool
end

function imgui.CustomSlider(str_id, value, type, min, max, sformat, width)
    local text      = str_id:gsub('##.+', '')
    local sformat   = sformat or (type and '%d' or '%0.3f')
    local width     = width or 200

    local DL        = imgui.GetWindowDrawList()
    local p         = imgui.GetCursorScreenPos()

    local function math_round(x)
        local a = tostring(x):gsub('%d+%.', '0.')
        if tonumber(a) > 0.5 then
            return math.ceil(x)
        else
            return math.floor(x)
        end
    end
    local function bringVec4To(from, to, start_time, duration)
        local timer = os.clock() - start_time
        if timer >= 0.00 and timer <= duration then
            local count = timer / (duration / 100)
            return imgui.ImVec4(
                from.x + (count * (to.x - from.x) / 100),
                from.y + (count * (to.y - from.y) / 100),
                from.z + (count * (to.z - from.z) / 100),
                from.w + (count * (to.w - from.w) / 100)
            ), true
        end
        return (timer > duration) and to or from, false
    end

    if UI_CUSTOM_SLIDER == nil then UI_CUSTOM_SLIDER = {} end
    if UI_CUSTOM_SLIDER[str_id] == nil then 
        UI_CUSTOM_SLIDER[str_id] = {
            active = false,
            hovered = false,
            start = 0
        } 
    end

    imgui.InvisibleButton(str_id, imgui.ImVec2(width, 20))

    UI_CUSTOM_SLIDER[str_id].active = imgui.IsItemActive()
    if UI_CUSTOM_SLIDER[str_id].hovered ~= imgui.IsItemHovered() then
        UI_CUSTOM_SLIDER[str_id].hovered = imgui.IsItemHovered()
        UI_CUSTOM_SLIDER[str_id].start = os.clock()
    end

    local colorPadding = bringVec4To(
        UI_CUSTOM_SLIDER[str_id].hovered and imgui.GetStyle().Colors[imgui.Col.Button] or imgui.GetStyle().Colors[imgui.Col.ButtonHovered], 
        UI_CUSTOM_SLIDER[str_id].hovered and imgui.GetStyle().Colors[imgui.Col.ButtonHovered] or imgui.GetStyle().Colors[imgui.Col.Button], 
        UI_CUSTOM_SLIDER[str_id].start, 0.2
    )
    
    local colorBackGroundBefore = imgui.GetStyle().Colors[imgui.Col.Button]
    local colorBackGroundAfter = imgui.ImVec4(0,0,0,0)
    local colorCircle = imgui.GetStyle().Colors[imgui.Col.ButtonActive]

    if UI_CUSTOM_SLIDER[str_id].active then
        local c = imgui.GetMousePos()
        if c.x - p.x >= 0 and c.x - p.x <= width then
            local s = c.x - p.x - 10
            local pr = s / (width - 20)
            local v = min + (max - min) * pr
            if v >= min and v <= max then
                value[0] = type and math_round(v) or v
            else
                value[0] = v < min and min or max
            end
        end
    end

    local posCircleX = p.x + 10 + (width - 20) / (max - min) * (value[0] - min)

    if posCircleX > p.x + 10 then DL:AddRectFilled(imgui.ImVec2(p.x, p.y), imgui.ImVec2(posCircleX, p.y + 20), imgui.GetColorU32Vec4(colorBackGroundBefore), 10, 15) end
    if posCircleX < p.x + width - 10 then DL:AddRectFilled(imgui.ImVec2(posCircleX, p.y), imgui.ImVec2(p.x + width, p.y + 20), imgui.GetColorU32Vec4(colorBackGroundAfter), 10, 15) end
    DL:AddRect(imgui.ImVec2(p.x, p.y), imgui.ImVec2(p.x + width, p.y + 20), imgui.GetColorU32Vec4(colorPadding), 10, 15)
    DL:AddCircleFilled(imgui.ImVec2(posCircleX, p.y + 10), 10, imgui.GetColorU32Vec4(colorCircle))

    local sf = imgui.CalcTextSize(string.format(sformat, value[0]))
    local st = imgui.CalcTextSize(text)
    DL:AddText(imgui.ImVec2(p.x + width / 2 - sf.x / 2, p.y + 10 - sf.y / 2), imgui.GetColorU32Vec4(imgui.GetStyle().Colors[imgui.Col.Text]), string.format(sformat, value[0]))
    imgui.SameLine()
    local p = imgui.GetCursorPos()
    imgui.SetCursorPos(imgui.ImVec2(p.x - 5, p.y + 10 - st.y / 2))
    imgui.Text(text)

    return UI_CUSTOM_SLIDER[str_id].active
end

imgui.OnInitialize(function()
    imgui.GetIO().IniFilename = nil
    local config = imgui.ImFontConfig()
    local iconRanges = imgui.new.ImWchar[3](faicons.min_range, faicons.max_range, 0)
    config.MergeMode = true
    config.PixelSnapH = true
    font = imgui.GetIO().Fonts:AddFontFromFileTTF("moonloader/fonts/arialuni.ttf", 38)
    imgui.GetIO().Fonts:AddFontFromMemoryCompressedBase85TTF(faicons.get_font_data_base85('solid'), 14, config, iconRanges)
    theme()
end)

function imgui.RoundedRectButton(label, width, height, cornerRadius, colorNormal, colorHover, colorActive)
    local pos = imgui.GetCursorScreenPos()
    local size = imgui.ImVec2(width, height)

    imgui.InvisibleButton(label, size)
    local hovered = imgui.IsItemHovered()
    local active = imgui.IsItemActive()

    local color = colorNormal
    if active then
        color = colorActive
    elseif hovered then
        color = colorHover
    end

    local draw_list = imgui.GetWindowDrawList()
    draw_list:AddRectFilled(pos, imgui.ImVec2(pos.x + width, pos.y + height), color, cornerRadius)

    local textSize = imgui.CalcTextSize(label)
    local center = imgui.ImVec2(
        pos.x + (width - textSize.x) / 2,
        pos.y + (height - textSize.y) / 2
    )
    draw_list:AddText(center, imgui.GetColorU32(imgui.Col.Text), label)

    return imgui.IsItemClicked()
end

function imgui.Hint(str_id, hint, delay)
    local hovered = imgui.IsItemHovered()
    local animTime = 0.2
    local delay = delay or 0.00
    local show = true

    if not allHints then allHints = {} end
    if not allHints[str_id] then
        allHints[str_id] = {
            status = false,
            timer = 0
        }
    end

    if hovered then
        for k, v in pairs(allHints) do
            if k ~= str_id and os.clock() - v.timer <= animTime  then
                show = false
            end
        end
    end

    if show and allHints[str_id].status ~= hovered then
        allHints[str_id].status = hovered
        allHints[str_id].timer = os.clock() + delay
    end

    if show then
        local between = os.clock() - allHints[str_id].timer
        if between <= animTime then
            local s = function(f)
                return f < 0.0 and 0.0 or (f > 1.0 and 1.0 or f)
            end
            local alpha = hovered and s(between / animTime) or s(1.00 - between / animTime)
            imgui.PushStyleVarFloat(imgui.StyleVar.Alpha, alpha)
            imgui.SetTooltip(hint)
            imgui.PopStyleVar()
        elseif hovered then
            imgui.SetTooltip(hint)
        end
    end
end

function join_argb(a, r, g, b)
    local argb = b
    argb = bit.bor(argb, bit.lshift(g, 8))
    argb = bit.bor(argb, bit.lshift(r, 16))
    argb = bit.bor(argb, bit.lshift(a, 24))
    return argb
end

function rainbow(speed, alpha, offset)
    local clock = os.clock() + offset
    local r = math.floor(math.sin(clock * speed) * 127 + 128)
    local g = math.floor(math.sin(clock * speed + 2) * 127 + 128)           
    local b = math.floor(math.sin(clock * speed + 4) * 127 + 128)
    return r,g,b,alpha
end

function rainbow_line(distance, size)
    local op = imgui.GetCursorPos()
    local p = imgui.GetCursorScreenPos()
    for i = 0, distance do
        local r, g, b, a = rainbow(1, 255, i / -50)
        imgui.GetWindowDrawList():AddRectFilled(imgui.ImVec2(p.x + i, p.y), imgui.ImVec2(p.x + i + 1, p.y + size), join_argb(a, r, g, b))
    end
    imgui.SetCursorPos(imgui.ImVec2(op.x, op.y + size + imgui.GetStyle().ItemSpacing.y))
end

function samp_create_sync_data(sync_type, copy_from_player)
    local ffi = require('ffi')
    local sampfuncs = require('sampfuncs')
    -- from SAMP.Lua
    local raknet = require ('samp.raknet')
    require('samp.synchronization')
    copy_from_player = copy_from_player or true
    local sync_traits = { 
        player = {'PlayerSyncData', raknet.PACKET.PLAYER_SYNC, sampStorePlayerOnfootData}, 
        vehicle = {'VehicleSyncData', raknet.PACKET.VEHICLE_SYNC, sampStorePlayerIncarData}, 
        passenger = {'PassengerSyncData', raknet.PACKET.PASSENGER_SYNC, sampStorePlayerPassengerData}, 
        aim = {'AimSyncData', raknet.PACKET.AIM_SYNC, sampStorePlayerAimData}, 
        trailer = {'TrailerSyncData', raknet.PACKET.TRAILER_SYNC, sampStorePlayerTrailerData}, 
        unoccupied = {'UnoccupiedSyncData', raknet.PACKET.UNOCCUPIED_SYNC, nil}, 
        bullet = {'BulletSyncData', raknet.PACKET.BULLET_SYNC, nil}, 
        spectator = {'SpectatorSyncData', raknet.PACKET.SPECTATOR_SYNC, nil}
    }
    local sync_info = sync_traits[sync_type]
    local data_type = 'struct ' .. sync_info[1]
    local data = ffi.new(data_type, {})
    local raw_data_ptr = tonumber(ffi.cast('uintptr_t', ffi.new(data_type .. '*', data)))
    -- copy player's sync data to the allocated memory
    if copy_from_player then
        local copy_func = sync_info[3]
        if copy_func then
            local _, player_id
            if copy_from_player == true then
                _, player_id = sampGetPlayerIdByCharHandle(PLAYER_PED)
            else
                player_id = tonumber(copy_from_player)
            end
            copy_func(player_id, raw_data_ptr)
        end
    end
    -- function to send packet
    local function func_send()
        local bs = raknetNewBitStream()
        raknetBitStreamWriteInt8(bs, sync_info[2])
        raknetBitStreamWriteBuffer(bs, raw_data_ptr, ffi.sizeof(data))
        raknetSendBitStreamEx(bs, sampfuncs.HIGH_PRIORITY, sampfuncs.UNRELIABLE_SEQUENCED, 1)
        raknetDeleteBitStream(bs)
    end
    -- metatable to access sync data and 'send' function
    local mt = {
        __index = function(t, index)
            return data[index]
        end,
        __newindex = function(t, index, value)
            data[index] = value
        end
    }
    return setmetatable({send = func_send}, mt)
end

function onReceiveRpc(id, bs) 
    if id == 162 and MRvanka.orvn.invisSurf[0] then
        return false
    end
end