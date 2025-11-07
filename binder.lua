script_name('SA:MP Binder')
script_author('MonetLoader')
script_version('1.0.0')

-- Ïîäêëş÷åíèå áèáëèîòåê
local imgui = require('mimgui')
local jsoncfg = require('jsoncfg')
local samp = require('samp')
local fa = require('fAwesome6_solid')
local monetloader = require('monetloader')
local memory = require('SAMemory')
local monet = require('MoonMonet')
local encoding = require('encoding')
encoding.default = 'CP1251'
local u8 = encoding.UTF8

-- Êîíôèãóğàöèÿ
local config_path = getWorkingDirectory() .. '/config/binder_config.json'
local default_config = {
    binds = {},
    window_size = {800, 600},
    theme = 0
}

local config = jsoncfg.load(config_path, default_config)

-- ImGui ïåğåìåííûå
local main_window = imgui.new.bool(false)
local binds = config.binds or {}
local selected_bind = 0

-- Ïîëÿ äëÿ äîáàâëåíèÿ/ğåäàêòèğîâàíèÿ áèíäà
local bind_name = imgui.new.char[256]()
local bind_key = imgui.new.char[128]()
local bind_command = imgui.new.char[1024]()
local bind_delay = imgui.new.int(0)
local bind_enabled = imgui.new.bool(true)

-- Öâåòîâàÿ ñõåìà
local colors = {
    primary = imgui.ImVec4(monet.buildColors(monetloader.getMonetColor(), 1.0, true).accent1[7] / 255,
                          monet.buildColors(monetloader.getMonetColor(), 1.0, true).accent1[8] / 255,
                          monet.buildColors(monetloader.getMonetColor(), 1.0, true).accent1[9] / 255, 1.0),
    background = imgui.ImVec4(0.09, 0.09, 0.09, 0.95),
    hover = imgui.ImVec4(0.2, 0.2, 0.2, 1.0),
    active = imgui.ImVec4(0.3, 0.3, 0.3, 1.0)
}

-- Ôóíêöèè äëÿ ğàáîòû ñ áèíäàìè
local function save_config()
    config.binds = binds
    jsoncfg.save(config_path, config)
end

local function add_bind(name, key, command, delay, enabled)
    table.insert(binds, {
        name = name,
        key = key,
        command = command,
        delay = delay or 0,
        enabled = enabled == nil and true or enabled,
        id = os.time() .. math.random(1000, 9999)
    })
    save_config()
end

local function delete_bind(index)
    table.remove(binds, index)
    save_config()
end

local function edit_bind(index, name, key, command, delay, enabled)
    binds[index].name = name
    binds[index].key = key
    binds[index].command = command
    binds[index].delay = delay or 0
    binds[index].enabled = enabled
    save_config()
end

local function execute_bind(bind)
    if not bind.enabled then return end
    
    lua_thread.create(function()
        local commands = {}
        for cmd in bind.command:gmatch("[^\n]+") do
            table.insert(commands, cmd)
        end
        
        for _, cmd in ipairs(commands) do
            if cmd:find("^/") then
                sampSendChat(cmd)
            else
                sampSendChat(cmd)
            end
            
            if bind.delay > 0 then
                wait(bind.delay)
            end
        end
    end)
end

local function clear_bind_fields()
    bind_name[0] = '\0'
    bind_key[0] = '\0'
    bind_command[0] = '\0'
    bind_delay[0] = 0
    bind_enabled[0] = true
    selected_bind = 0
end

local function load_bind_to_fields(index)
    local bind = binds[index]
    imgui.StrCopy(bind_name, u8(bind.name))
    imgui.StrCopy(bind_key, u8(bind.key))
    imgui.StrCopy(bind_command, u8(bind.command))
    bind_delay[0] = bind.delay
    bind_enabled[0] = bind.enabled
    selected_bind = index
end

-- Ïğèìåíåíèå òåìû ImGui
local function apply_imgui_style()
    local style = imgui.GetStyle()
    local colors = style.Colors
    local icol = imgui.Col
    local ImVec4 = imgui.ImVec4
    local ImVec2 = imgui.ImVec2
    
    style.WindowPadding = ImVec2(15, 15)
    style.WindowRounding = 10.0
    style.FramePadding = ImVec2(8, 6)
    style.FrameRounding = 6.0
    style.ItemSpacing = ImVec2(12, 8)
    style.ItemInnerSpacing = ImVec2(8, 6)
    style.IndentSpacing = 25.0
    style.ScrollbarSize = 15.0
    style.ScrollbarRounding = 9.0
    style.GrabMinSize = 5.0
    style.GrabRounding = 3.0
    style.ChildRounding = 8.0
    style.PopupRounding = 8.0
    
    -- Öâåòà èç MonetLoader
    local monet_colors = monet.buildColors(monetloader.getMonetColor(), 1.0, true)
    
    colors[icol.Text] = ImVec4(0.95, 0.96, 0.98, 1.00)
    colors[icol.TextDisabled] = ImVec4(0.50, 0.50, 0.50, 1.00)
    colors[icol.WindowBg] = ImVec4(0.09, 0.09, 0.09, 0.95)
    colors[icol.ChildBg] = ImVec4(0.12, 0.12, 0.12, 0.95)
    colors[icol.PopupBg] = ImVec4(0.08, 0.08, 0.08, 0.94)
    colors[icol.Border] = ImVec4(0.20, 0.20, 0.20, 0.50)
    colors[icol.BorderShadow] = ImVec4(0.00, 0.00, 0.00, 0.00)
    colors[icol.FrameBg] = ImVec4(0.16, 0.16, 0.16, 1.00)
    colors[icol.FrameBgHovered] = ImVec4(0.20, 0.20, 0.20, 1.00)
    colors[icol.FrameBgActive] = ImVec4(0.25, 0.25, 0.25, 1.00)
    colors[icol.TitleBg] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.TitleBgActive] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.TitleBgCollapsed] = ImVec4(0.00, 0.00, 0.00, 0.51)
    colors[icol.MenuBarBg] = ImVec4(0.14, 0.14, 0.14, 1.00)
    colors[icol.ScrollbarBg] = ImVec4(0.02, 0.02, 0.02, 0.53)
    colors[icol.ScrollbarGrab] = ImVec4(0.31, 0.31, 0.31, 1.00)
    colors[icol.ScrollbarGrabHovered] = ImVec4(0.41, 0.41, 0.41, 1.00)
    colors[icol.ScrollbarGrabActive] = ImVec4(0.51, 0.51, 0.51, 1.00)
    colors[icol.CheckMark] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.SliderGrab] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.SliderGrabActive] = ImVec4(monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, monet_colors.accent1[7]/255, 1.00)
    colors[icol.Button] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.ButtonHovered] = ImVec4(monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, monet_colors.accent1[7]/255, 1.00)
    colors[icol.ButtonActive] = ImVec4(monet_colors.accent1[4]/255, monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, 1.00)
    colors[icol.Header] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 0.55)
    colors[icol.HeaderHovered] = ImVec4(monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, monet_colors.accent1[7]/255, 0.80)
    colors[icol.HeaderActive] = ImVec4(monet_colors.accent1[4]/255, monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, 1.00)
    colors[icol.Separator] = ImVec4(0.28, 0.28, 0.28, 0.50)
    colors[icol.SeparatorHovered] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 0.78)
    colors[icol.SeparatorActive] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.ResizeGrip] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 0.25)
    colors[icol.ResizeGripHovered] = ImVec4(monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, monet_colors.accent1[7]/255, 0.67)
    colors[icol.ResizeGripActive] = ImVec4(monet_colors.accent1[4]/255, monet_colors.accent1[5]/255, monet_colors.accent1[6]/255, 0.95)
    colors[icol.Tab] = ImVec4(0.18, 0.18, 0.18, 1.00)
    colors[icol.TabHovered] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 0.80)
    colors[icol.TabActive] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 1.00)
    colors[icol.TabUnfocused] = ImVec4(0.07, 0.10, 0.15, 0.97)
    colors[icol.TabUnfocusedActive] = ImVec4(0.14, 0.26, 0.42, 1.00)
    colors[icol.PlotLines] = ImVec4(0.61, 0.61, 0.61, 1.00)
    colors[icol.PlotLinesHovered] = ImVec4(1.00, 0.43, 0.35, 1.00)
    colors[icol.PlotHistogram] = ImVec4(0.90, 0.70, 0.00, 1.00)
    colors[icol.PlotHistogramHovered] = ImVec4(1.00, 0.60, 0.00, 1.00)
    colors[icol.TextSelectedBg] = ImVec4(monet_colors.accent1[7]/255, monet_colors.accent1[8]/255, monet_colors.accent1[9]/255, 0.35)
end

-- Ãëàâíîå îêíî
imgui.OnFrame(function() return main_window[0] end, function(player)
    local resX, resY = getScreenResolution()
    imgui.SetNextWindowPos(imgui.ImVec2(resX / 2, resY / 2), imgui.Cond.FirstUseEver, imgui.ImVec2(0.5, 0.5))
    imgui.SetNextWindowSize(imgui.ImVec2(900, 600), imgui.Cond.FirstUseEver)
    
    if imgui.Begin(fa.ICON_FA_KEYBOARD .. u8' SA:MP Binder Menu', main_window, imgui.WindowFlags.NoCollapse) then
        -- Ëåâàÿ ïàíåëü ñî ñïèñêîì áèíäîâ
        imgui.BeginChild('left_panel', imgui.ImVec2(300, 0), true)
        imgui.PushStyleColor(imgui.Col.Text, imgui.ImVec4(1.0, 1.0, 1.0, 1.0))
        imgui.TextWrapped(fa.ICON_FA_LIST .. u8' Ñïèñîê áèíäîâ')
        imgui.PopStyleColor()
        imgui.Separator()
        
        if #binds == 0 then
            imgui.TextWrapped(u8'Íåò ñîçäàííûõ áèíäîâ.\nÄîáàâüòå íîâûé áèíä ñïğàâà.')
        else
            for i, bind in ipairs(binds) do
                local checkbox_enabled = imgui.new.bool(bind.enabled)
                
                if imgui.Checkbox('##enable_' .. i, checkbox_enabled) then
                    bind.enabled = checkbox_enabled[0]
                    save_config()
                end
                
                imgui.SameLine()
                
                local color = bind.enabled and imgui.ImVec4(1.0, 1.0, 1.0, 1.0) or imgui.ImVec4(0.5, 0.5, 0.5, 1.0)
                imgui.PushStyleColor(imgui.Col.Text, color)
                
                if imgui.Selectable(u8(bind.name) .. '##' .. i, selected_bind == i) then
                    load_bind_to_fields(i)
                end
                
                imgui.PopStyleColor()
                
                if imgui.IsItemHovered() then
                    imgui.BeginTooltip()
                    imgui.Text(u8'Êëàâèøà: ' .. u8(bind.key))
                    imgui.Text(u8'Çàäåğæêà: ' .. bind.delay .. u8' ìñ')
                    imgui.EndTooltip()
                end
            end
        end
        
        imgui.EndChild()
        
        imgui.SameLine()
        
        -- Ïğàâàÿ ïàíåëü ñ ğåäàêòèğîâàíèåì
        imgui.BeginChild('right_panel', imgui.ImVec2(0, 0), true)
        imgui.PushStyleColor(imgui.Col.Text, imgui.ImVec4(1.0, 1.0, 1.0, 1.0))
        if selected_bind > 0 then
            imgui.TextWrapped(fa.ICON_FA_PEN .. u8' Ğåäàêòèğîâàíèå áèíäà')
        else
            imgui.TextWrapped(fa.ICON_FA_PLUS .. u8' Ñîçäàíèå íîâîãî áèíäà')
        end
        imgui.PopStyleColor()
        imgui.Separator()
        
        imgui.Text(fa.ICON_FA_TAG .. u8' Íàçâàíèå áèíäà:')
        imgui.PushItemWidth(-1)
        imgui.InputText('##bind_name', bind_name, 256)
        imgui.PopItemWidth()
        
        imgui.Spacing()
        
        imgui.Text(fa.ICON_FA_KEY .. u8' Êëàâèøà àêòèâàöèè:')
        imgui.PushItemWidth(-1)
        imgui.InputText('##bind_key', bind_key, 128)
        imgui.PopItemWidth()
        imgui.TextWrapped(u8'(Íàïğèìåğ: F1, F2, F3... èëè 1, 2, 3...)')
        
        imgui.Spacing()
        
        imgui.Text(fa.ICON_FA_TERMINAL .. u8' Êîìàíäà/Òåêñò:')
        imgui.PushItemWidth(-1)
        imgui.InputTextMultiline('##bind_command', bind_command, 1024, imgui.ImVec2(-1, 200))
        imgui.PopItemWidth()
        imgui.TextWrapped(u8'(Êàæäàÿ ñòğîêà = îòäåëüíàÿ êîìàíäà/ñîîáùåíèå)')
        
        imgui.Spacing()
        
        imgui.Text(fa.ICON_FA_CLOCK .. u8' Çàäåğæêà ìåæäó êîìàíäàìè (ìñ):')
        imgui.PushItemWidth(-1)
        imgui.InputInt('##bind_delay', bind_delay)
        imgui.PopItemWidth()
        
        imgui.Spacing()
        
        imgui.Checkbox(u8'Áèíä âêëş÷åí', bind_enabled)
        
        imgui.Spacing()
        imgui.Separator()
        imgui.Spacing()
        
        -- Êíîïêè äåéñòâèé
        if selected_bind > 0 then
            if imgui.Button(fa.ICON_FA_FLOPPY_DISK .. u8' Ñîõğàíèòü èçìåíåíèÿ', imgui.ImVec2(-1, 40)) then
                local name = u8:decode(ffi.string(bind_name))
                local key = u8:decode(ffi.string(bind_key))
                local command = u8:decode(ffi.string(bind_command))
                
                if name ~= '' and key ~= '' and command ~= '' then
                    edit_bind(selected_bind, name, key, command, bind_delay[0], bind_enabled[0])
                    sampAddChatMessage('[Binder] {FFFFFF}Áèíä îáíîâë¸í!', 0x00FF00)
                end
            end
            
            imgui.Spacing()
            
            if imgui.Button(fa.ICON_FA_TRASH .. u8' Óäàëèòü áèíä', imgui.ImVec2(-1, 40)) then
                delete_bind(selected_bind)
                clear_bind_fields()
                sampAddChatMessage('[Binder] {FFFFFF}Áèíä óäàë¸í!', 0xFF0000)
            end
            
            imgui.Spacing()
            
            if imgui.Button(fa.ICON_FA_XMARK .. u8' Îòìåíà', imgui.ImVec2(-1, 40)) then
                clear_bind_fields()
            end
        else
            if imgui.Button(fa.ICON_FA_CIRCLE_PLUS .. u8' Äîáàâèòü áèíä', imgui.ImVec2(-1, 40)) then
                local name = u8:decode(ffi.string(bind_name))
                local key = u8:decode(ffi.string(bind_key))
                local command = u8:decode(ffi.string(bind_command))
                
                if name ~= '' and key ~= '' and command ~= '' then
                    add_bind(name, key, command, bind_delay[0], bind_enabled[0])
                    clear_bind_fields()
                    sampAddChatMessage('[Binder] {FFFFFF}Áèíä äîáàâëåí!', 0x00FF00)
                else
                    sampAddChatMessage('[Binder] {FFFFFF}Çàïîëíèòå âñå ïîëÿ!', 0xFF0000)
                end
            end
            
            imgui.Spacing()
            
            if imgui.Button(fa.ICON_FA_ERASER .. u8' Î÷èñòèòü ïîëÿ', imgui.ImVec2(-1, 40)) then
                clear_bind_fields()
            end
        end
        
        imgui.EndChild()
        
        imgui.End()
    end
end):register()

-- Îáğàáîòêà íàæàòèé êëàâèø
function onWindowMessage(msg, wparam, lparam)
    if msg == 0x100 or msg == 0x101 then -- WM_KEYDOWN è WM_KEYUP
        if msg == 0x100 then -- Ïğè íàæàòèè êëàâèøè
            for i, bind in ipairs(binds) do
                if bind.enabled then
                    local key_name = bind.key:upper()
                    local vk_code = nil
                    
                    -- F-êëàâèøè
                    if key_name:find('F%d+') then
                        local f_num = tonumber(key_name:match('%d+'))
                        if f_num and f_num >= 1 and f_num <= 12 then
                            vk_code = 0x6F + f_num
                        end
                    -- Öèôğû
                    elseif key_name:find('^%d$') then
                        vk_code = tonumber(key_name) + 0x30
                    -- Áóêâû
                    elseif key_name:len() == 1 and key_name:match('%a') then
                        vk_code = string.byte(key_name)
                    end
                    
                    if vk_code and wparam == vk_code then
                        execute_bind(bind)
                    end
                end
            end
        end
    end
end

-- Êîìàíäû ÷àòà
function sampev.onServerMessage(color, text)
    -- Îáğàáîòêà ñåğâåğíûõ ñîîáùåíèé åñëè íóæíî
end

-- Ğåãèñòğàöèÿ êîìàíäû
function main()
    if not isSampLoaded() or not isSampfuncsLoaded() then return end
    while not isSampAvailable() do wait(100) end
    
    apply_imgui_style()
    
    sampRegisterChatCommand('binder', function()
        main_window[0] = not main_window[0]
    end)
    
    sampAddChatMessage('[Binder] {FFFFFF}Ñêğèïò çàãğóæåí! Èñïîëüçóéòå {00FF00}/binder {FFFFFF}äëÿ îòêğûòèÿ ìåíş', 0x00FF00)
    sampAddChatMessage('[Binder] {FFFFFF}Âåğñèÿ: {00FF00}1.0.0', 0x00FF00)
    
    wait(-1)
end
