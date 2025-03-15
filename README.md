# Arctic Adventures Bot 🌍❄️

A Telegram bot for discovering and managing sights in Arkhangelskaya Oblast' with multilingual support and admin features.

![Bot Demo](demo.gif)

## Features ✨

- **Multilingual Interface** 🇬🇧/🇷🇺  
  Supports English and Russian with easy language switching (`/lang`)

- **Interactive Sight Exploration** 🏰
  - `/start` - Begin your journey
  - `/rand` - Get random sight with photo and map link
  - `/list` - Paginated list of all sights with details

- **Admin Tools** 🧙
  - `/add` - Add new sights (photo + location)
  - `/del` - Remove existing sights
  - Whitelist protection for admin commands

- **User-Friendly Design** 🎨
  - Emoji-rich interface
  - Child-friendly content
  - Error-resistant architecture

## Installation 🛠️

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/arkhangelsk-bot.git
cd arkhangelsk-bot
```

2. **Install Dependencies**
```bash
pip install python-telegram-bot=13.5 deep-translator
```

3. **Configuration**
- Get Telegram bot token from [@BotFather](https://t.me/BotFather) and replace `YOUR_BOT_TOKEN` with a real token
- Create config files:
  ```bash
  touch sights.json
  mkdir images
  ```
- Update `WHITELIST` in bot.py with admin user IDs

4. **Run Bot**
```bash
python bot.py
```

## Usage 🤖

### Basic Commands
- `/start` - Initialize bot and choose language
- `/help` - Show available commands
- `/lang` - Change language (EN/RU)
- `/dev` - Show bot technical info

### Exploration Commands
- `/rand` - Discover random sight
- `/list` - Browse all sights with pagination

### Admin Commands
- `/add` - Start sight creation wizard
- `/del` - Remove existing sight

## Tech Stack 💻
- Python 3.9
- [python-telegram-bot 13.5](https://python-telegram-bot.org/)
- [Deep Translator](https://deep-translator.readthedocs.io/)

## License 📄
MIT License - See [LICENSE](LICENSE) for details

---

**Created with ❤️ by [apaww](https://github.com/apaww) and [Andrew Akentev](https://github.com/AnAkfiaSaltes)**  
[Report Issues](https://github.com/apaww/Arctic-Adventures-Bot/issues) | [Contribute](https://github.com/apaww/Arctic-Adventures-Bot/pulls)
```
