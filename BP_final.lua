local imgui = require 'mimgui'
local inicfg = require 'inicfg'
local se = require 'lib.samp.events'
local encoding = require 'encoding'
encoding.default = 'CP1251'
u8 = encoding.UTF8

local main_window_state = imgui.ImBool(false)
local daily = {}
local premium = {}
local quests = {}
local premiumBP = false

local function loadJsonFile(path)
	local file = io.open(getWorkingDirectory() .. "/resource/" .. path, "r")
	if file then
		local content = file:read("*a")
		file:close()
		if content and content ~= "" then
			local result = decodeJson(content)
			if result then
				return result
			end
		end
	end
	return {}
end

daily = loadJsonFile("BPdaily.json")
premium = loadJsonFile("BPpremium.json")

function main()
	while not isSampAvailable() do 
		wait(100) 
	end
	
	sampRegisterChatCommand('bph', function()
		if #quests > 0 then
			main_window_state.v = not main_window_state.v
			imgui.Process = main_window_state.v
		else
			sampAddChatMessage("{32CD32}[BP Helper] {FFFFFF}Для работы скрипта откройте {32CD32}Боевой Пропуск{FFFFFF}!", -1)
		end
	end)
	
	while true do
		wait(0)
		if not main_window_state.v then
			imgui.Process = false
		end
	end
end

function imgui.OnDrawFrame()
	if main_window_state.v then
		local resX, resY = getScreenResolution()
		local sizeX = resX * 0.26
		local sizeY = premiumBP and resY * 0.78 or resY * 0.47
		imgui.SetNextWindowPos(imgui.ImVec2(resX - sizeX / 2, resY - sizeY / 2), imgui.Cond.FirstUseEver, imgui.ImVec2(0.5, 0.5))
		imgui.SetNextWindowSize(imgui.ImVec2(sizeX, sizeY), imgui.Cond.FirstUseEver)
		imgui.ShowCursor = false
		
		imgui.Begin('bphelper', main_window_state, imgui.WindowFlags.NoCollapse + imgui.WindowFlags.NoTitleBar)
		imgui.GetStyle().Colors[imgui.Col.WindowBg].w = 1.0
		
		local uncompleted_quests = {}
		local completed_quests = {}
		local hidden_quests = {}
		local pinned_quests = {}

		for _, quest in ipairs(quests) do
			if quest.pinned.v and not quest.progress then
				table.insert(pinned_quests, quest)
			elseif not quest.show.v and not quest.progress then
				table.insert(hidden_quests, quest)
			elseif not quest.progress then
				table.insert(uncompleted_quests, quest)
			else
				table.insert(completed_quests, quest)
			end
		end

		local sorted_quests = {}
		for _, quest in ipairs(pinned_quests) do
			table.insert(sorted_quests, quest)
		end
		for _, quest in ipairs(uncompleted_quests) do
			table.insert(sorted_quests, quest)
		end
		for _, quest in ipairs(completed_quests) do
			table.insert(sorted_quests, quest)
		end
		for _, quest in ipairs(hidden_quests) do
			table.insert(sorted_quests, quest)
		end

		local window_width = imgui.GetContentRegionAvail().x
		imgui.Columns(2, "Quests", false)
		imgui.SetColumnWidth(0, window_width - 20)
		
		imgui.NextColumn()
		imgui.Text('Pin')
		imgui.NextColumn()
		
		for index, quest in ipairs(sorted_quests) do
			if quest.pinned.v and not quest.progress then
				DrawCustomCheckbox(quest.text .. '##' .. index, quest.show, imgui.ImVec4(1.0, 0.85, 0.0, 1.0))
				imgui.NextColumn()
				imgui.Checkbox('##pinned' .. tostring(index), quest.pinned)
				imgui.NextColumn()
			elseif not quest.progress and quest.show.v then
				DrawCustomCheckbox(quest.text .. '##' .. index, quest.show, imgui.ImVec4(1.0, 1.0, 1.0, 1.0))
				imgui.NextColumn()
				imgui.Checkbox('##pinned' .. tostring(index), quest.pinned)
				imgui.NextColumn()
			elseif quest.progress then
				DrawCustomCheckbox(quest.text .. '##' .. index, quest.show, imgui.ImVec4(0.196, 0.804, 0.196, 1.0))
				imgui.NextColumn()
				imgui.Checkbox('##pinned' .. tostring(index), quest.pinned)
				imgui.NextColumn()
			else
				DrawCustomCheckbox(quest.text .. '##' .. index, quest.show, imgui.ImVec4(0.412, 0.412, 0.412, 1.0))
				imgui.NextColumn()
				imgui.Checkbox('##pinned' .. tostring(index), quest.pinned)
				imgui.NextColumn()
			end
		end
		
		imgui.Columns(1)
		imgui.End()
	end
end

function findItemById(array, id)
	if not array then return nil end
	for _, item in ipairs(array) do
		if item.id == id then
			return item
		end
	end
	return nil
end

function hasItemWithCategoryAndId(array, target, progress)
	for index, item in ipairs(array) do
		if item.id == target.id and item.categoryId == target.categoryId then
			if item.progress ~= progress then
				quests[index].progress = progress
			end
			return true
		end
	end
	return false
end

function se.onServerMessage(color, text)
	if text and string.find(text, "%[Боевой Пропуск%]%{ffffff%} Вы успешно выполнили задание") then
		local result = string.match(text, "'(.-)'")
		if result then
			for _, quest in ipairs(quests) do
				if quest.title == result then
					quest.progress = true
					break
				end
			end
		end
	end
end

addEventHandler('onReceivePacket', function(id, bs)
	if id == 220 then
		raknetBitStreamIgnoreBits(bs, 8)
		if raknetBitStreamReadInt8(bs) == 17 then
			raknetBitStreamIgnoreBits(bs, 32)
			local length = raknetBitStreamReadInt16(bs)
			local encoded = raknetBitStreamReadInt8(bs)
			local str = (encoded ~= 0) and raknetBitStreamDecodeString(bs, length + encoded) or raknetBitStreamReadString(bs, length)
			if str and str:find("event.battlePass.initializeBattlePassData") then
				local battlePassData = str:match("`(.+)`")
				if battlePassData then
					local battlePassDataParsed = decodeJson(battlePassData)
					if battlePassDataParsed and battlePassDataParsed[1] and battlePassDataParsed[1].premium ~= 0 then
						premiumBP = true
					end
				end
			elseif str and str:find("event.battlePass.updateQuestsProgress") then
				local innerList = string.match(str, "%[%[(.-)%]%]")
				if innerList then
					innerList = "[" .. innerList .. "]"
					local data = decodeJson(innerList)
					if data then
						for i, item in ipairs(data) do
							local source = (item.categoryId == "daily" and daily) or (item.categoryId == "premium" and premiumBP and premium) or nil
							if source then
								local matchedItem = findItemById(source, item.id)
								if matchedItem then
									if not hasItemWithCategoryAndId(quests, matchedItem, item.progress >= matchedItem.totalProgress) then
										table.insert(quests, {
											id = matchedItem.id,
											categoryId = matchedItem.categoryId,
											text = matchedItem.description,
											progress = item.progress >= matchedItem.totalProgress,
											title = matchedItem.title,
											show = imgui.ImBool(true),
											pinned = imgui.ImBool(false)
										})
									end
								end
							end
						end
					end
				end
			end
		end
	end
end)

function DrawCustomCheckbox(label, state, textColor)
	imgui.PushStyleColor(imgui.Col.Text, textColor)
	imgui.Checkbox(u8(label), state)
	imgui.PopStyleColor(1)
end
