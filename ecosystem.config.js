module.exports = {
    apps: [{
        name: 'Ingress Sojourner Reminder',
        cmd: 'bot.py',
        interpreter: '/home/ubuntu/.miniconda3/envs/telegram/bin/python3',
        // autorestart: false,
        // watch: true,
    }]
};