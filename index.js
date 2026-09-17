const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
    ],
});

client.once('ready', () => {
    console.log(`[ONLINE] ${client.user.tag} is active and ready!`);
    client.user.setActivity('HimalayanHub | /help', { type: 3 });
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    const content = message.content.toLowerCase();

    if (content === '!ping' || content === '/ping') {
        message.reply('🏔️ HimalayanHub is online and operating at peak performance!');
    }
    
    if (content.includes('hello') || content.includes('hi')) {
        message.channel.send(`Namaste ${message.author}! Batao, HimalayanHub aapki kya madad kar sakta hai?`);
    }
});

client.login(process.env.DISCORD_BOT_TOKEN);

