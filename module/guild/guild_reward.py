from module.guild.lobby import GuildLobby
from module.guild.logistics import GuildLogistics
from module.guild.operations import GuildOperations
from module.ui.page import page_guild, page_main
from datetime import datetime, timedelta

class RewardGuild(GuildLobby, GuildLogistics, GuildOperations):
    def run(self):
        """
        AzurPilot handler function for guild reward loop

        Returns:
            bool: If executed

        Pages:
            in: page_main
            out: page_main
        """
        if not self.config.GuildLogistics_Enable and not self.config.GuildOperation_Enable:
            self.config.Scheduler_Enable = False
            self.config.task_stop()

        self.ui_ensure(page_guild)
        success = True

        # Lobby
        self.guild_lobby()

        # Logistics
        if self.config.GuildLogistics_Enable:
            success &= self.guild_logistics()

        # Operation
        if self.config.GuildOperation_Enable:
            success &= self.guild_operations()

        self.ui_goto(page_main)

        # Scheduler
        # 定点时间表与容差
        TARGET_HOURS = [0, 3, 6, 9, 12, 15, 18, 21]
        OFFSET_MINUTES = 3
        now = datetime.now()
        next_run = None
        # 寻找下一个有效时间点
        for h in TARGET_HOURS:
            candidate = now.replace(hour=h, minute=OFFSET_MINUTES, second=0, microsecond=0)
            if candidate > now:
                next_run = candidate
                break
        # 顺延到明天第一个点
        if next_run is None:
            next_run = (now + timedelta(days=1)).replace(
                hour=TARGET_HOURS[0], 
                minute=OFFSET_MINUTES, 
                second=0, 
                microsecond=0
            )
        if success:
            self.config.task_delay(target=next_run)
        else:
            self.config.task_delay(success=False, minute=60)
