const { Client, GatewayIntentBits, PermissionsBitField, EmbedBuilder } = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildVoiceStates
    ]
});

client.once('ready', () => {
    console.log(`HimalayanHub Bot is online and running live as ${client.user.tag}! 🚀`);
});

client.on('messageCreate', async message => {
    if (message.author.bot) return;

    const args = message.content.trim().split(/ +/);
    const command = args.shift().toLowerCase();

    // --- 1. CORE & UTILITY COMMANDS ---
    if (command === '!ping') {
        const latency = Date.now() - message.createdTimestamp;
        message.reply(`Pong! 🏓 WebSocket Latency: ${client.ws.ping}ms | Message Latency: ${latency}ms`);
    }

    if (command === '!help') {
        const embed = new EmbedBuilder()
            .setColor('#5865F2')
            .setTitle('🌟 HimalayanHub Command Center')
            .setDescription('Here are the available commands for your server:')
            .addFields(
                { name: '🛡️ Moderation', value: '`!kick`, `!ban`, `!purge`', inline: false },
                { name: '🎉 Fun & Games', value: '`!8ball`, `!roll`, `!flip`', inline: false },
                { name: '🤗 Anime Social Actions', value: '`!hug`, `!kiss`, `!slap`, `!pat`, `!cuddle`, `!bonk`', inline: false }
            )
            .setFooter({ text: 'Powered by FusionHub Developer Portal' });
        message.reply({ embeds: [embed] });
    }

    // --- 2. MODERATION COMMANDS ---
    if (command === '!kick') {
        if (!message.member.permissions.has(PermissionsBitField.Flags.KickMembers)) {
            return message.reply('❌ You do not have permission to use `!kick`.');
        }
        const member = message.mentions.members.first();
        if (!member) return message.reply('⚠️ Please mention a valid user to kick! (e.g., `!kick @user`)');
        
        const reason = args.slice(1).join(' ') || 'No reason provided';
        try {
            await member.kick(reason);
            message.reply(`✅ Successfully kicked **${member.user.tag}**. Reason: ${reason}`);
        } catch (err) {
            console.error(err);
            message.reply('❌ Failed to kick this user (Check role hierarchy or bot permissions).');
        }
    }

    if (command === '!ban') {
        if (!message.member.permissions.has(PermissionsBitField.Flags.BanMembers)) {
            return message.reply('❌ You do not have permission to use `!ban`.');
        }
        const member = message.mentions.members.first();
        if (!member) return message.reply('⚠️ Please mention a valid user to ban! (e.g., `!ban @user`)');

        const reason = args.slice(1).join(' ') || 'No reason provided';
        try {
            await member.ban({ reason });
            message.reply(`🔨 Successfully banned **${member.user.tag}**. Reason: ${reason}`);
        } catch (err) {
            console.error(err);
            message.reply('❌ Failed to ban this user.');
        }
    }

    if (command === '!purge' || command === '!clear') {
        if (!message.member.permissions.has(PermissionsBitField.Flags.ManageMessages)) {
            return message.reply('❌ You do not have permission to manage messages.');
        }
        const count = parseInt(args[0]);
        if (!count || count < 1 || count > 100) {
            return message.reply('⚠️ Please specify a number between 1 and 100! (e.g., `!purge 10`)');
        }
        try {
            await message.channel.bulkDelete(count, true);
            const replyMsg = await message.channel.send(`🧹 Successfully cleared ${count} messages.`);
            setTimeout(() => replyMsg.delete().catch(() => {}), 4000);
        } catch (err) {
            console.error(err);
            message.reply('❌ Error deleting messages (Messages older than 14 days cannot be bulk deleted).');
        }
    }

    // --- 3. FUN & GAMES ---
    if (command === '!8ball') {
        const question = args.join(' ');
        if (!question) return message.reply('⚠️ Please ask a question! (e.g., `!8ball will I win?`)');
        const responses = [
            'Yes, definitely! 👍',
            'Outlook not so good. ❌',
            'Signs point to yes. ✨',
            'Cannot predict now. 🤔',
            'Reply hazy, try again. 🔄',
            'Better not tell you now. 🤫'
        ];
        const answer = responses[Math.floor(Math.random() * responses.length)];
        message.reply(`🎱 **Question:** ${question}\n🔮 **Answer:** ${answer}`);
    }

    if (command === '!flip') {
        const result = Math.random() < 0.5 ? 'Heads 🪙' : 'Tails 🪙';
        message.reply(`The coin landed on: **${result}**`);
    }

    // --- 4. ANIME SOCIAL ACTIONS ---
    const handleAnimeAction = (actionName, defaultSelfMsg, actionMsg) => {
        const target = message.mentions.users.first();
        if (!target) {
            return message.reply(defaultSelfMsg);
        }
        message.channel.send(actionMsg(message.author, target));
    };

    if (command === '!hug') {
        handleAnimeAction(
            'hug',
            `🤗 ${message.author} gave themselves a warm hug! (So cozy)`,
            (author, target) => `🤗 **${author.username}** wrapped their arms around **${target.username}** for a warm hug! ❤️`
        );
    }

    if (command === '!kiss') {
        handleAnimeAction(
            'kiss',
            `😘 ${message.author} blew a flying kiss to everyone!`,
            (author, target) => `😘 **${author.username}** gave a sweet, loving kiss to **${target.username}**! ✨`
        );
    }

    if (command === '!slap') {
        handleAnimeAction(
            'slap',
            `👋 ${message.author} slapped the air!`,
            (author, target) => `💥 **${author.username}** gave an energetic slap to **${target.username}**! Ouch! 🖐️`
        );
    }

    if (command === '!pat') {
        handleAnimeAction(
            'pat',
            `🤗 ${message.author} patted themselves!`,
            (author, target) => `🐾 **${author.username}** patted **${target.username}** softly on the head! ✨`
        );
    }

    if (command === '!cuddle') {
        handleAnimeAction(
            'cuddle',
            `🥰 ${message.author} is cuddling with a pillow!`,
            (author, target) => `🥰 **${author.username}** cuddled up cozy with **${target.username}**! ❤️`
        );
    }

    if (command === '!bonk') {
        handleAnimeAction(
            'bonk',
            `🔨 ${message.author} bonked themselves!`,
            (author, target) => `🔨 **${author.username}** bonked **${target.username}** straight to horny jail! 🐕`
        );
    }
});

process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

client.login(process.env.DISCORD_BOT_TOKEN);
