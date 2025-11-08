// ХроноКолода: Путешествие сквозь Эпохи - Game Logic

class ChronoDeckGame {
    constructor() {
        this.currentLevel = 1;
        this.chronoCrystals = 0;
        this.playerLevel = 1;
        this.unlockedCards = [];
        this.completedLevels = [];
        this.gameState = null;
        this.cardDatabase = this.initCardDatabase();
        this.levelsDatabase = this.initLevelsDatabase();
        this.loadProgress();
    }

    initCardDatabase() {
        return [
            // Исторические персонажи
            { id: 1, name: 'Леонардо да Винчи', type: 'character', era: 'renaissance', icon: '??', cost: 2, description: 'Изобретатель и художник', ability: 'invention', rarity: 'epic' },
            { id: 2, name: 'Клеопатра', type: 'character', era: 'ancient', icon: '??', cost: 3, description: 'Египетская царица', ability: 'diplomacy', rarity: 'legendary' },
            { id: 3, name: 'Архимед', type: 'character', era: 'ancient', icon: '??', cost: 2, description: 'Математик и изобретатель', ability: 'science', rarity: 'rare' },
            { id: 4, name: 'Жанна д\'Арк', type: 'character', era: 'medieval', icon: '??', cost: 3, description: 'Героиня Франции', ability: 'courage', rarity: 'epic' },
            { id: 5, name: 'Никола Тесла', type: 'character', era: 'industrial', icon: '?', cost: 3, description: 'Гений электричества', ability: 'electricity', rarity: 'legendary' },
            
            // События
            { id: 6, name: 'Открытие Америки', type: 'event', era: 'renaissance', icon: '??', cost: 2, description: 'Великое географическое открытие', ability: 'exploration', rarity: 'rare' },
            { id: 7, name: 'Падение Рима', type: 'event', era: 'ancient', icon: '???', cost: 3, description: 'Конец великой империи', ability: 'transformation', rarity: 'epic' },
            { id: 8, name: 'Первый полёт', type: 'event', era: 'industrial', icon: '??', cost: 2, description: 'Братья Райт', ability: 'innovation', rarity: 'rare' },
            { id: 9, name: 'Строительство пирамид', type: 'event', era: 'ancient', icon: '???', cost: 3, description: 'Чудо древнего мира', ability: 'construction', rarity: 'epic' },
            { id: 10, name: 'Изобретение книгопечатания', type: 'event', era: 'medieval', icon: '??', cost: 2, description: 'Гутенберг меняет мир', ability: 'knowledge', rarity: 'rare' },
            
            // Артефакты
            { id: 11, name: 'Философский камень', type: 'artifact', era: 'medieval', icon: '??', cost: 4, description: 'Легендарный артефакт алхимиков', ability: 'transmutation', rarity: 'legendary' },
            { id: 12, name: 'Золотое руно', type: 'artifact', era: 'mythical', icon: '??', cost: 3, description: 'Предмет греческих мифов', ability: 'fortune', rarity: 'legendary' },
            { id: 13, name: 'Экскалибур', type: 'artifact', era: 'medieval', icon: '???', cost: 3, description: 'Меч короля Артура', ability: 'power', rarity: 'legendary' },
            { id: 14, name: 'Компас', type: 'artifact', era: 'medieval', icon: '??', cost: 1, description: 'Инструмент навигации', ability: 'guidance', rarity: 'common' },
            { id: 15, name: 'Телескоп', type: 'artifact', era: 'renaissance', icon: '??', cost: 2, description: 'Окно в космос', ability: 'vision', rarity: 'rare' },
            
            // Ресурсы
            { id: 16, name: 'Энергия времени', type: 'resource', era: 'universal', icon: '?', cost: 0, description: 'Базовая энергия', ability: 'energy', rarity: 'common' },
            { id: 17, name: 'Знание', type: 'resource', era: 'universal', icon: '??', cost: 1, description: 'Сила разума', ability: 'intellect', rarity: 'common' },
            { id: 18, name: 'Храбрость', type: 'resource', era: 'universal', icon: '??', cost: 1, description: 'Сила духа', ability: 'bravery', rarity: 'common' },
            
            // Мифологические персонажи
            { id: 19, name: 'Одиссей', type: 'character', era: 'mythical', icon: '??', cost: 3, description: 'Хитроумный герой', ability: 'cunning', rarity: 'epic' },
            { id: 20, name: 'Прометей', type: 'character', era: 'mythical', icon: '??', cost: 4, description: 'Даритель огня', ability: 'sacrifice', rarity: 'legendary' },
            
            // Футуристические карты
            { id: 21, name: 'Квантовый компьютер', type: 'artifact', era: 'future', icon: '??', cost: 4, description: 'Сверхмощный вычислитель', ability: 'computation', rarity: 'legendary' },
            { id: 22, name: 'Терраформер', type: 'artifact', era: 'future', icon: '??', cost: 5, description: 'Преобразует планеты', ability: 'terraform', rarity: 'legendary' },
            { id: 23, name: 'ИИ Помощник', type: 'character', era: 'future', icon: '??', cost: 2, description: 'Искусственный интеллект', ability: 'assistance', rarity: 'rare' },
            
            // Дополнительные карты для разнообразия
            { id: 24, name: 'Александр Македонский', type: 'character', era: 'ancient', icon: '??', cost: 4, description: 'Великий завоеватель', ability: 'conquest', rarity: 'legendary' },
            { id: 25, name: 'Мария Кюри', type: 'character', era: 'industrial', icon: '??', cost: 3, description: 'Первая женщина-нобелевский лауреат', ability: 'radiation', rarity: 'epic' },
            { id: 26, name: 'Конфуций', type: 'character', era: 'ancient', icon: '??', cost: 2, description: 'Древний философ', ability: 'wisdom', rarity: 'rare' },
            { id: 27, name: 'Да Винчи Кодекс', type: 'artifact', era: 'renaissance', icon: '??', cost: 2, description: 'Записи великого мастера', ability: 'secrets', rarity: 'epic' },
            { id: 28, name: 'Библиотека Александрии', type: 'event', era: 'ancient', icon: '???', cost: 3, description: 'Центр знаний древности', ability: 'knowledge', rarity: 'epic' },
            { id: 29, name: 'Великая Китайская стена', type: 'event', era: 'ancient', icon: '??', cost: 3, description: 'Величайшее строение', ability: 'defense', rarity: 'rare' },
            { id: 30, name: 'Вавилонская башня', type: 'event', era: 'ancient', icon: '??', cost: 4, description: 'Легендарное строение', ability: 'unity', rarity: 'epic' }
        ];
    }

    initLevelsDatabase() {
        const levels = [];
        
        // Первые 10 уровней - обучающие и исторические
        levels.push({
            id: 1,
            name: 'Начало пути',
            description: 'Познакомьтесь с основами игры',
            era: 'tutorial',
            goal: { type: 'collect', cards: ['resource'], count: 3 },
            startingHand: [16, 16, 17, 18],
            deckCards: [16, 16, 17, 17, 18, 18],
            turns: 10,
            reward: { crystals: 10, cards: [1, 14] }
        });
        
        levels.push({
            id: 2,
            name: 'Древний Египет',
            description: 'Помогите построить пирамиды',
            era: 'ancient',
            goal: { type: 'collect', cards: ['event', 'character'], count: 2 },
            startingHand: [2, 16, 17, 18],
            deckCards: [9, 2, 16, 17, 18, 3, 16, 17],
            turns: 8,
            reward: { crystals: 15, cards: [9, 3] }
        });
        
        levels.push({
            id: 3,
            name: 'Греческие мифы',
            description: 'Найдите Золотое руно',
            era: 'mythical',
            goal: { type: 'collect', cards: ['artifact'], count: 1, specific: [12] },
            startingHand: [19, 16, 17, 18],
            deckCards: [12, 19, 16, 17, 18, 20, 16, 17, 18],
            turns: 10,
            reward: { crystals: 20, cards: [12, 19, 20] }
        });
        
        levels.push({
            id: 4,
            name: 'Средневековые легенды',
            description: 'Обретите Экскалибур',
            era: 'medieval',
            goal: { type: 'collect', cards: ['artifact', 'character'], count: 2 },
            startingHand: [4, 16, 17, 18],
            deckCards: [13, 4, 10, 16, 17, 18, 14, 16, 17],
            turns: 9,
            reward: { crystals: 18, cards: [13, 4, 10] }
        });
        
        levels.push({
            id: 5,
            name: 'Эпоха Возрождения',
            description: 'Помогите Леонардо завершить изобретения',
            era: 'renaissance',
            goal: { type: 'collect', cards: ['character', 'artifact'], count: 3 },
            startingHand: [1, 15, 16, 17],
            deckCards: [1, 15, 27, 6, 16, 17, 18, 16, 17],
            turns: 10,
            reward: { crystals: 25, cards: [1, 15, 27] }
        });
        
        levels.push({
            id: 6,
            name: 'Великие открытия',
            description: 'Откройте Новый Свет',
            era: 'renaissance',
            goal: { type: 'collect', cards: ['event'], count: 2 },
            startingHand: [6, 14, 16, 17],
            deckCards: [6, 14, 16, 17, 18, 16, 17, 18],
            turns: 8,
            reward: { crystals: 20, cards: [6, 14] }
        });
        
        levels.push({
            id: 7,
            name: 'Падение Рима',
            description: 'Спасите знания империи',
            era: 'ancient',
            goal: { type: 'collect', cards: ['event', 'resource'], count: 4 },
            startingHand: [7, 28, 17, 17],
            deckCards: [7, 28, 24, 16, 17, 18, 17, 18, 26],
            turns: 10,
            reward: { crystals: 22, cards: [7, 24, 26] }
        });
        
        levels.push({
            id: 8,
            name: 'Индустриальная революция',
            description: 'Зажгите искру прогресса',
            era: 'industrial',
            goal: { type: 'collect', cards: ['character', 'event'], count: 3 },
            startingHand: [5, 8, 16, 17],
            deckCards: [5, 8, 25, 16, 17, 18, 16, 17, 18],
            turns: 9,
            reward: { crystals: 30, cards: [5, 8, 25] }
        });
        
        levels.push({
            id: 9,
            name: 'Мифы и легенды',
            description: 'Помогите Прометею',
            era: 'mythical',
            goal: { type: 'collect', cards: ['character'], count: 2, specific: [19, 20] },
            startingHand: [19, 20, 16, 17],
            deckCards: [19, 20, 12, 16, 17, 18, 16, 17, 18],
            turns: 8,
            reward: { crystals: 35, cards: [20, 12] }
        });
        
        levels.push({
            id: 10,
            name: 'Босс: Хранитель Эпох',
            description: 'Первое испытание Хранителя',
            era: 'boss',
            goal: { type: 'collect', cards: ['character', 'event', 'artifact'], count: 5 },
            startingHand: [1, 2, 16, 17],
            deckCards: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            turns: 15,
            reward: { crystals: 100, cards: [11, 13, 20] }
        });
        
        // Генерация дополнительных уровней (11-100+)
        for (let i = 11; i <= 120; i++) {
            const era = this.getRandomEra(i);
            const difficulty = Math.floor(i / 10);
            
            levels.push({
                id: i,
                name: `Уровень ${i}: ${this.getLevelName(i, era)}`,
                description: this.getLevelDescription(i, era),
                era: era,
                goal: this.generateLevelGoal(difficulty),
                startingHand: this.generateStartingHand(difficulty),
                deckCards: this.generateDeck(difficulty),
                turns: 8 + Math.floor(difficulty / 2),
                reward: { crystals: 10 + (i * 2), cards: this.getRandomRewardCards(difficulty) },
                boss: i % 10 === 0
            });
        }
        
        return levels;
    }

    getRandomEra(level) {
        const eras = ['ancient', 'mythical', 'medieval', 'renaissance', 'industrial', 'future'];
        if (level % 10 === 0) return 'boss';
        return eras[Math.floor(Math.random() * eras.length)];
    }

    getLevelName(level, era) {
        const names = {
            ancient: ['Тайны Вавилона', 'Величие Египта', 'Золотой век Греции', 'Римская империя', 'Мудрость Востока'],
            mythical: ['Подвиги Геракла', 'Сокровища Олимпа', 'Загадки Сфинкса', 'Битва Титанов', 'Путь героя'],
            medieval: ['Рыцарские турниры', 'Замки и драконы', 'Святая война', 'Путь самурая', 'Викинги'],
            renaissance: ['Эпоха открытий', 'Расцвет искусств', 'Научная революция', 'Новый мир', 'Реформация'],
            industrial: ['Паровая эра', 'Электрический век', 'Автомобили', 'Покорение неба', 'Радио волны'],
            future: ['Киберэпоха', 'Звездные войны', 'ИИ восстание', 'Марсианские колонии', 'Квантовый мир'],
            boss: ['Испытание Хранителя', 'Временной парадокс', 'Властелин времени', 'Хаос эпох', 'Последняя битва']
        };
        const eraNames = names[era] || names['ancient'];
        return eraNames[Math.floor(Math.random() * eraNames.length)];
    }

    getLevelDescription(level, era) {
        const descriptions = {
            ancient: 'Исправьте временной сбой в древности',
            mythical: 'Восстановите баланс мифологического мира',
            medieval: 'Верните порядок в средневековье',
            renaissance: 'Сохраните достижения эпохи',
            industrial: 'Направьте прогресс по верному пути',
            future: 'Предотвратите катастрофу будущего',
            boss: 'Сразитесь с могущественным противником'
        };
        return descriptions[era] || 'Выполните задание уровня';
    }

    generateLevelGoal(difficulty) {
        const types = ['collect', 'sequence', 'combo'];
        const goalType = types[Math.floor(Math.random() * types.length)];
        
        return {
            type: goalType,
            cards: ['character', 'event', 'artifact'],
            count: 2 + difficulty,
            specific: null
        };
    }

    generateStartingHand(difficulty) {
        const hand = [16, 17, 18]; // базовые ресурсы
        const cardPool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15];
        for (let i = 0; i < 1 + Math.floor(difficulty / 3); i++) {
            hand.push(cardPool[Math.floor(Math.random() * cardPool.length)]);
        }
        return hand;
    }

    generateDeck(difficulty) {
        const deck = [];
        const cardPool = this.cardDatabase.map(c => c.id);
        const deckSize = 15 + (difficulty * 2);
        
        for (let i = 0; i < deckSize; i++) {
            deck.push(cardPool[Math.floor(Math.random() * cardPool.length)]);
        }
        
        // Добавляем базовые ресурсы
        for (let i = 0; i < 5; i++) {
            deck.push(16, 17, 18);
        }
        
        return deck;
    }

    getRandomRewardCards(difficulty) {
        const count = 1 + Math.floor(difficulty / 2);
        const rewards = [];
        const cardPool = this.cardDatabase.filter(c => c.rarity !== 'common');
        
        for (let i = 0; i < count && i < 5; i++) {
            const card = cardPool[Math.floor(Math.random() * cardPool.length)];
            if (card) rewards.push(card.id);
        }
        
        return rewards;
    }

    startGame() {
        this.currentLevel = 1;
        this.saveProgress();
        this.loadLevel(1);
        this.showScreen('game-screen');
    }

    continueGame() {
        if (this.currentLevel > 1) {
            this.loadLevel(this.currentLevel);
            this.showScreen('game-screen');
        } else {
            this.startGame();
        }
    }

    loadLevel(levelId) {
        const level = this.levelsDatabase[levelId - 1];
        if (!level) {
            alert('Уровень не найден!');
            return;
        }

        this.gameState = {
            level: level,
            turn: 1,
            energy: 3,
            hand: [],
            playedCards: [],
            deck: [...level.deckCards],
            goalProgress: [],
            paradoxes: 0
        };

        // Shuffle deck
        this.shuffleDeck();

        // Deal starting hand
        level.startingHand.forEach(cardId => {
            const card = this.getCardById(cardId);
            if (card) this.gameState.hand.push(card);
        });

        this.updateUI();
    }

    shuffleDeck() {
        for (let i = this.gameState.deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.gameState.deck[i], this.gameState.deck[j]] = 
            [this.gameState.deck[j], this.gameState.deck[i]];
        }
    }

    drawCard() {
        if (this.gameState.deck.length === 0) {
            this.showMessage('Колода пуста!');
            return;
        }

        if (this.gameState.energy < 1) {
            this.showMessage('Недостаточно энергии!');
            return;
        }

        const cardId = this.gameState.deck.pop();
        const card = this.getCardById(cardId);
        
        if (card) {
            this.gameState.hand.push(card);
            this.gameState.energy -= 1;
            this.updateUI();
            this.animateCardDraw();
        }
    }

    playCard(card) {
        if (this.gameState.energy < card.cost) {
            this.showMessage('Недостаточно энергии!');
            return;
        }

        // Remove from hand
        const index = this.gameState.hand.findIndex(c => c.id === card.id);
        if (index !== -1) {
            this.gameState.hand.splice(index, 1);
            this.gameState.playedCards.push(card);
            this.gameState.energy -= card.cost;

            // Check goal progress
            this.checkGoalProgress(card);

            // Check for paradoxes
            this.checkParadox();

            this.updateUI();
            this.checkWinCondition();
        }
    }

    checkGoalProgress(card) {
        const goal = this.gameState.level.goal;
        
        if (goal.type === 'collect') {
            if (goal.specific) {
                // Specific cards needed
                if (goal.specific.includes(card.id)) {
                    if (!this.gameState.goalProgress.includes(card.id)) {
                        this.gameState.goalProgress.push(card.id);
                    }
                }
            } else {
                // Any cards of specified types
                if (goal.cards.includes(card.type)) {
                    this.gameState.goalProgress.push(card.id);
                }
            }
        }
    }

    checkParadox() {
        // Check for anachronisms
        const playedEras = this.gameState.playedCards.map(c => c.era);
        const uniqueEras = [...new Set(playedEras)];
        
        if (uniqueEras.length > 3 && this.gameState.playedCards.length > 5) {
            this.gameState.paradoxes++;
            if (this.gameState.paradoxes >= 3) {
                this.gameLost('Слишком много временных парадоксов!');
            }
        }
    }

    checkWinCondition() {
        const goal = this.gameState.level.goal;
        let won = false;

        if (goal.type === 'collect') {
            if (goal.specific) {
                won = goal.specific.every(id => this.gameState.goalProgress.includes(id));
            } else {
                won = this.gameState.goalProgress.length >= goal.count;
            }
        }

        if (won) {
            this.gameWon();
        }
    }

    endTurn() {
        this.gameState.turn++;
        this.gameState.energy = 3 + Math.floor(this.gameState.turn / 3);

        if (this.gameState.turn > this.gameState.level.turns) {
            this.gameLost('Время истекло!');
            return;
        }

        this.updateUI();
    }

    gameWon() {
        const reward = this.gameState.level.reward;
        this.chronoCrystals += reward.crystals;
        
        if (reward.cards) {
            reward.cards.forEach(cardId => {
                if (!this.unlockedCards.includes(cardId)) {
                    this.unlockedCards.push(cardId);
                }
            });
        }

        if (!this.completedLevels.includes(this.currentLevel)) {
            this.completedLevels.push(this.currentLevel);
        }

        document.getElementById('victory-message').textContent = 
            `Вы восстановили ${this.gameState.level.name}!`;
        
        document.getElementById('rewards').innerHTML = `
            <p>?? Получено ХроноКристаллов: ${reward.crystals}</p>
            <p>?? Новых карт: ${reward.cards ? reward.cards.length : 0}</p>
        `;

        this.showModal('victory-modal');
        this.saveProgress();
    }

    gameLost(reason) {
        document.getElementById('defeat-message').textContent = reason;
        this.showModal('defeat-modal');
    }

    nextLevel() {
        this.currentLevel++;
        this.hideModal('victory-modal');
        
        if (this.currentLevel <= this.levelsDatabase.length) {
            this.loadLevel(this.currentLevel);
        } else {
            alert('Поздравляем! Вы прошли все уровни!');
            this.returnToMenu();
        }
    }

    retryLevel() {
        this.hideModal('defeat-modal');
        this.loadLevel(this.currentLevel);
    }

    showCollection() {
        this.showScreen('collection-screen');
        this.renderCollection('all');
    }

    filterCollection(filter) {
        // Update filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        this.renderCollection(filter);
    }

    renderCollection(filter) {
        const container = document.getElementById('collection-cards');
        container.innerHTML = '';

        let cards = this.cardDatabase;
        if (filter !== 'all') {
            cards = cards.filter(c => c.type === filter.slice(0, -1)); // remove 's'
        }

        cards.forEach(card => {
            const isUnlocked = this.unlockedCards.includes(card.id) || card.rarity === 'common';
            const cardEl = this.createCardElement(card, !isUnlocked);
            container.appendChild(cardEl);
        });
    }

    showArchive() {
        this.showScreen('archive-screen');
        this.renderArchive();
    }

    renderArchive() {
        const content = document.getElementById('archive-content');
        content.innerHTML = `
            <div class="archive-era">
                <h3>??? Древний мир</h3>
                <p>Период с 3000 г. до н.э. до 476 г. н.э. Эпоха великих цивилизаций: Египет, Греция, Рим.</p>
                <p>Ключевые события: строительство пирамид, расцвет демократии, создание империй.</p>
            </div>
            <div class="archive-era">
                <h3>?? Средневековье</h3>
                <p>Период с 476 по 1492 год. Эпоха рыцарей, замков и крестовых походов.</p>
                <p>Ключевые события: феодализм, изобретение книгопечатания, великие путешествия.</p>
            </div>
            <div class="archive-era">
                <h3>?? Возрождение</h3>
                <p>XIV-XVII века. Расцвет искусства, науки и географических открытий.</p>
                <p>Ключевые фигуры: Леонардо да Винчи, Микеланджело, Христофор Колумб.</p>
            </div>
            <div class="archive-era">
                <h3>?? Индустриальная эра</h3>
                <p>XVIII-XIX века. Время технологической революции и научного прогресса.</p>
                <p>Ключевые изобретения: паровой двигатель, электричество, железные дороги.</p>
            </div>
            <div class="archive-era">
                <h3>?? Будущее</h3>
                <p>XXI век и далее. Эра искусственного интеллекта и освоения космоса.</p>
                <p>Перспективы: колонизация Марса, квантовые компьютеры, нанотехнологии.</p>
            </div>
            <div class="archive-era">
                <h3>?? Мифология</h3>
                <p>Легенды и мифы различных культур. Герои, боги и мифические существа.</p>
                <p>Включает: греческую, римскую, скандинавскую и восточную мифологию.</p>
            </div>
        `;
    }

    createCardElement(card, locked = false) {
        const cardDiv = document.createElement('div');
        cardDiv.className = `card ${card.type}`;
        if (locked) cardDiv.classList.add('locked');

        cardDiv.innerHTML = `
            <div class="card-cost">${card.cost}</div>
            <div class="card-icon">${locked ? '??' : card.icon}</div>
            <div class="card-name">${locked ? '???' : card.name}</div>
            <div class="card-type">${this.translateType(card.type)}</div>
            <div class="card-description">${locked ? 'Заблокировано' : card.description}</div>
            <div class="card-era">${this.translateEra(card.era)}</div>
        `;

        if (!locked) {
            cardDiv.onclick = () => this.playCard(card);
        }

        return cardDiv;
    }

    translateType(type) {
        const types = {
            character: 'Персонаж',
            event: 'Событие',
            artifact: 'Артефакт',
            resource: 'Ресурс'
        };
        return types[type] || type;
    }

    translateEra(era) {
        const eras = {
            ancient: 'Древность',
            mythical: 'Мифы',
            medieval: 'Средневековье',
            renaissance: 'Возрождение',
            industrial: 'Индустриальная',
            future: 'Будущее',
            universal: 'Универсальная',
            boss: 'Босс'
        };
        return eras[era] || era;
    }

    updateUI() {
        if (!this.gameState) return;

        // Update header
        document.getElementById('level-title').textContent = this.gameState.level.name;
        document.getElementById('level-description').textContent = this.gameState.level.description;
        document.getElementById('energy').textContent = this.gameState.energy;
        document.getElementById('turn').textContent = `${this.gameState.turn}/${this.gameState.level.turns}`;
        document.getElementById('crystals').textContent = this.chronoCrystals;
        document.getElementById('deck-count').textContent = this.gameState.deck.length;

        // Update goal area
        const goalDiv = document.getElementById('goal-cards');
        goalDiv.innerHTML = '';
        const goal = this.gameState.level.goal;
        
        for (let i = 0; i < goal.count; i++) {
            const slot = document.createElement('div');
            slot.className = 'card-slot';
            if (i < this.gameState.goalProgress.length) {
                slot.classList.add('filled');
                const card = this.getCardById(this.gameState.goalProgress[i]);
                if (card) slot.textContent = card.icon;
            }
            goalDiv.appendChild(slot);
        }

        document.getElementById('goal-progress').textContent = 
            `Прогресс: ${this.gameState.goalProgress.length}/${goal.count}`;

        // Update hand
        const handDiv = document.getElementById('player-hand');
        handDiv.innerHTML = '';
        this.gameState.hand.forEach(card => {
            handDiv.appendChild(this.createCardElement(card));
        });

        // Update played cards
        const playedDiv = document.getElementById('played-cards');
        playedDiv.innerHTML = '';
        this.gameState.playedCards.forEach(card => {
            const cardEl = this.createCardElement(card);
            cardEl.onclick = null;
            cardEl.style.transform = 'scale(0.8)';
            playedDiv.appendChild(cardEl);
        });

        // Update menu stats
        document.getElementById('player-level').textContent = this.playerLevel;
        document.getElementById('chrono-crystals').textContent = this.chronoCrystals;
    }

    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(screenId).classList.add('active');
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }

    returnToMenu() {
        this.hideModal('victory-modal');
        this.hideModal('defeat-modal');
        this.showScreen('main-menu');
        this.updateUI();
    }

    getCardById(id) {
        return this.cardDatabase.find(c => c.id === id);
    }

    animateCardDraw() {
        const hand = document.getElementById('player-hand');
        const lastCard = hand.lastChild;
        if (lastCard) {
            lastCard.classList.add('card-draw-animation');
        }
    }

    showMessage(message) {
        // Simple alert for now, could be improved with toast notifications
        const toast = document.createElement('div');
        toast.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.8);color:white;padding:15px 30px;border-radius:10px;z-index:9999;';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }

    saveProgress() {
        const progress = {
            currentLevel: this.currentLevel,
            chronoCrystals: this.chronoCrystals,
            playerLevel: this.playerLevel,
            unlockedCards: this.unlockedCards,
            completedLevels: this.completedLevels
        };
        localStorage.setItem('chronoDeckProgress', JSON.stringify(progress));
    }

    loadProgress() {
        const saved = localStorage.getItem('chronoDeckProgress');
        if (saved) {
            const progress = JSON.parse(saved);
            this.currentLevel = progress.currentLevel || 1;
            this.chronoCrystals = progress.chronoCrystals || 0;
            this.playerLevel = progress.playerLevel || 1;
            this.unlockedCards = progress.unlockedCards || [];
            this.completedLevels = progress.completedLevels || [];
        } else {
            // Start with some basic cards unlocked
            this.unlockedCards = [1, 2, 3, 14, 16, 17, 18];
        }
    }
}

// Initialize game
const game = new ChronoDeckGame();
game.updateUI();
