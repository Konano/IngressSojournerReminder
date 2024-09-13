module.exports = {
    apps: [{
        name: 'IngressSojourner',
        cmd: 'bot.py',
        interpreter: '/home/ubuntu/.miniconda3/envs/telegram/bin/python3',
        autorestart: true,
        // watch: true,
    }]
};
