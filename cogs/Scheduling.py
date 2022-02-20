import discord
import aiosqlite
import asyncio
import traceback
import sys
from datetime import datetime, timedelta
from random import randrange
from discord.ext import commands, tasks

class Scheduling(commands.Cog, name="Scheduling"):
    
    def __init__(self, client):
        self.client = client
        self.client.database_dir = "./cogs/database/schedule.db"
        
    async def _e(self, ctx, title, description, colour, footer_bool=None, footer_text=None):
        e = discord.Embed(
            title = title,
            description = description,
            colour = colour
        )
        
        if footer_bool == True:
            e.set_footer(text=footer_text)
            
        return e
    
    @commands.command()
    async def schedule(self, ctx):
        def check(user):
            return user.author.id == ctx.author.id
        
        week = {"monday": {}, "tuesday": {}, "wednesday": {}, "thursday": {}, "friday": {}}
        class_dict = {}
        
        classes = None
        days = []
        _format = "%I:%M%p"
        
        class_title_text = "Enter your classes!"
        class_desc_text = "What classes do you have this semester?\nEnter them with a `,` separation between each class.\nEnter the word `nothing` to exit the process."
        class_footer_text = "Process will time out in 10 minutes if there is no activity."
        class_embed = await Scheduling._e(self, ctx, class_title_text, class_desc_text, 0xdeadaf, True, class_footer_text)
        
        while True:
            classes_text = ""
            what_classes = await ctx.send(
                embed = class_embed
            )
            try:
                classes_check = await self.client.wait_for(
                    'message', 
                    timeout = 600, 
                    check = check
                )
            except asyncio.TimeoutError:
                await what_classes.delete()
                await ctx.send("Request timed out.")
                return
            else:
                await what_classes.delete()

                if classes_check.content.lower() == "nothing":
                    return await ctx.send("Aborting process.")
                
                classes_content = classes_check.content.lower().replace(" ", "").split(",")
                
                for i in range(len(classes_content)):
                    classes_text += classes_content[i] + ((", ") if i < len(classes_content) - 1 else "")
                
                class_question = await ctx.send(f"Are these classes, `{classes_text}`, correct? (Yes/No)")
                try:
                    classes_question_check = await self.client.wait_for(
                        'message', 
                        timeout = 600, 
                        check = check
                    )
                except asyncio.TimeoutError:
                    await class_question.delete()
                    await ctx.send("Request timed out.")
                    return
                else:
                    await class_question.delete()
                    if classes_question_check.content.lower() != "yes":
                        continue
                    else:
                        classes = classes_content
                        for _class in classes:
                            class_dict[_class] = []
                        break
        
        for _c in classes:
            day_title_text = "Enter your days!"
            day_desc_text = f"What days of the week do you have `{_c}` this semester?\nEnter them with a `,` separation between each day.\nIf you only have this class for one day, then only enter one day.\nIf you wish to stop the process, enter the word `nothing`."
            day_footer_text = "Process will time out in 10 minutes if there is no activity."
            day_embed = await Scheduling._e(self, ctx, day_title_text, day_desc_text, 0xdeadaf, True, day_footer_text)
            while True:
                oh_shit_go_back = False
                day_text = ""
                what_days = await ctx.send(
                    embed = day_embed
                )
                try:
                    days_check = await self.client.wait_for(
                        'message', 
                        timeout = 600, 
                        check = check
                    )
                except asyncio.TimeoutError:
                    await what_days.delete()
                    await ctx.send("Request timed out.")
                    return
                else:
                    await what_days.delete()
                    
                    if days_check.content.lower() == "nothing":
                        return await ctx.send("Aborting process.")
                    
                    days_content = days_check.content.replace(" ", "").split(",")
                    
                    for i in range(len(days_content)):
                        day_text += days_content[i] + ((", ") if i < len(days_content) - 1 else "")
                    
                    day_question = await ctx.send(f"Are these days, `{day_text}`, correct? (Yes/No)")
                    try:
                        day_question_check = await self.client.wait_for(
                            'message', 
                            timeout = 600, 
                            check = check
                        )
                    except asyncio.TimeoutError:
                        await day_question.delete()
                        await ctx.send("Request timed out.")
                        return
                    else:
                        await day_question.delete()
                        if day_question_check.content.lower() != "yes":
                            continue
                        else:
                            for _day in days_content:
                                try:
                                    week[_day.lower()][_c] = []
                                except KeyError:
                                    await ctx.send(f"{_day} is an invalid day of the week.\nPlease try again!")
                                    oh_shit_go_back = True
                                    break
                            if oh_shit_go_back == True:
                                continue
                            
                            class_dict[_c] = days_content
                            break
        
        for k, v in class_dict.items():
            for _d in v:
                time_title_text = "Enter your times!"
                time_desc_text = f"What times do you have `{k}` on `{_d}`?\nEnter in `Hour:MinutesAM/PM` format with the start and end times separated by a comma.\nIf you wish to stop the process, enter the word `nothing`.\nIf you do not have this class on this day, enter the word `none`."
                time_footer_text = "Process will time out in 10 minutes if there is no activity."
                time_embed = await Scheduling._e(self, ctx, time_title_text, time_desc_text, 0xdeadaf, True, time_footer_text)
                while True:
                    time_text = ""
                    what_times = await ctx.send(
                        embed = time_embed
                    )
                    try:
                        times_check = await self.client.wait_for(
                            'message', 
                            timeout = 600, 
                            check = check
                        )
                    except asyncio.TimeoutError:
                        await what_times.delete()
                        await ctx.send("Request timed out.")
                        return
                    else:
                        await what_times.delete()
                        
                        if times_check.content.lower() == "none":
                            break
                        
                        if times_check.content.lower() == "nothing":
                            return await ctx.send("Aborting process.")
                        
                        times_content = times_check.content.replace(" ", "").split(",")
                        
                        if len(times_content) != 2:
                            await ctx.send("You need **one** start time and **one** end time. Please try again!")
                            continue
                        
                        for i in range(len(times_content)):
                            time_text += times_content[i] + ((", ") if i < len(times_content) - 1 else "")
                        
                        time_question = await ctx.send(f"Are these times, `{time_text}`, correct? (Yes/No)")
                        try:
                            time_question_check = await self.client.wait_for(
                                'message', 
                                timeout = 600, 
                                check = check
                            )
                        except asyncio.TimeoutError:
                            await time_question.delete()
                            await ctx.send("Request timed out.")
                            return
                        else:
                            await time_question.delete()
                            if time_question_check.content.lower() != "yes":
                                continue
                            else:
                                for _time in times_content:
                                    try:
                                        _t = datetime.strptime(_time, _format)
                                        week[_d.lower()][k].append(_time)
                                    except (ValueError, KeyError):
                                        await ctx.send(f"Either the time is incorrectly formatted or there is a different error. Please try again!")
                                    continue
                                break

        try:
            conn = await aiosqlite.connect(self.client.database_dir)
            c = await conn.cursor()
            
            await c.execute(f'''drop table if exists TABLE_{ctx.author.id}''')
            
            await c.execute(f'''create table if not exists TABLE_{ctx.author.id} ("Monday" TEXT DEFAULT 'None', "Tuesday" TEXT DEFAULT 'None', "Wednesday" TEXT DEFAULT 'None', "Thursday" TEXT DEFAULT 'None', "Friday" TEXT DEFAULT 'None');''')
            
            _list = []
            
            for k, v in week.items():
                _list.append(v)
                
            await c.execute(f"insert into TABLE_{ctx.author.id} values(?, ?, ?, ?, ?)", (f"{_list[0]}", f"{_list[1]}", f"{_list[2]}", f"{_list[3]}", f"{_list[4]}",))
        
        except aiosqlite.Error as er:
            if not isinstance(er, aiosqlite.IntegrityError) and not isinstance(er, aiosqlite.OperationalError):
                print('SQLite error: %s' % (' '.join(er.args)))
                print("Exception class is: ", er.__class__)
                print('SQLite traceback: ')
                exc_type, exc_value, exc_tb = sys.exc_info()
                print(traceback.format_exception(exc_type, exc_value, exc_tb))
        
        finally:
            await conn.commit()
            await conn.close()
            
        await ctx.send("Done!")


    @commands.command()
    async def showSchedule(self, ctx):
        try:
            conn = await aiosqlite.connect(self.client.database_dir)
            c = await conn.cursor()
            
            await c.execute(f"select * from TABLE_{ctx.author.id}")
            
            f = await c.fetchall() #list inside tuple, 5 elements
            
            if len(f) == 0:
                return await ctx.send("You have no schedule set up. Use the schedule command to set up your schedule!")
            
            f = f[0]
            
            week = ["", "", "", "", ""]
            weekdays = ["**Monday**\n", "**Tuesday**\n", "**Wednesday**\n", "**Thursday**\n", "**Friday**\n"]            
                        
            for i in range(len(f)):
                element = eval(f[i])
                
                for k, v in element.items():
                    if len(v) != 0:
                        week[i] += f"**__{k.upper()}__**\n"
                        week[i] += f"Starts at: **{v[0]}**\nEnds at: **{v[1]}**\n"
            
            final = ""
            for i in range(len(week)):
                if week[i] != "":
                    final += f"{weekdays[i]}{week[i]}\n"
                
            await ctx.send(content=final)

        except aiosqlite.Error as er:
            if not isinstance(er, aiosqlite.IntegrityError) and not isinstance(er, aiosqlite.OperationalError):
                print('SQLite error: %s' % (' '.join(er.args)))
                print("Exception class is: ", er.__class__)
                print('SQLite traceback: ')
                exc_type, exc_value, exc_tb = sys.exc_info()
                print(traceback.format_exception(exc_type, exc_value, exc_tb))
        
        finally:
            await conn.commit()
            await conn.close()

    
def setup(client):
    client.add_cog(Scheduling(client))