import discord
import database

class RemoveTaskView(discord.ui.View):
    def __init__(self, matches):
        super().__init__(timeout=60)
        self.message = None
        for task in matches:
            label = task.text[:75]
            self.add_item(RemoveTaskButton(task.id, label))
            
    async def on_timeout(self):
        if self.message:
            await self.message.edit(content="Selection has expired. Please try again if needed.", view=None)

class RemoveTaskButton(discord.ui.Button):
    def __init__(self, task_id, label):
        super().__init__(label=label, style=discord.ButtonStyle.danger)
        self.task_id = task_id

    async def callback(self, interaction: discord.Interaction):
        removed = database.remove_task_by_id(self.task_id)
        await interaction.response.edit_message(content=f"Task removed: {removed}.", view=None)
